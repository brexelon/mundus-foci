#!/usr/bin/env python3
"""Mundus Foci build tool.

Produces every distribution format from the packwiz source in this repo:

    dist/Mundus-Foci-<ver>.mrpack             Modrinth format (Prism, Modrinth App, ATLauncher, ...)
    dist/Mundus-Foci-<ver>-curseforge.zip     CurseForge format (CurseForge App import)
    dist/Mundus-Foci-<ver>-server.zip         Ready-to-run dedicated server (unzip, run start script)
    dist/mundus-foci-latest.mrpack            Stable filename used by server/docker-compose.yml
    MODLIST.md                                Generated list of every mod and where it runs

Usage:
    python tools/build.py                      build everything
    python tools/build.py mrpack server        build only some targets
    python tools/build.py --set-version 1.1.0  bump the pack version everywhere, then build
    python tools/build.py --docker             also build the Docker image (needs Docker running)
    python tools/build.py server --test-server boot the server pack once and report success/crash

Requires: Python 3.11+, packwiz on PATH. --test-server also needs Java 17 or 21.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import tomllib
import urllib.request
import zipfile
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
CACHE = BUILD / "cache"
SERVER_TEMPLATE = ROOT / "server" / "template"
KUBEJS_CONFIG = ROOT / "kubejs" / "server_scripts" / "00_config.js"
UA = {"User-Agent": "mundus-foci-build/1.0 (+packwiz)"}
TARGETS = ("mrpack", "curseforge", "server", "modlist")


# ----------------------------------------------------------------------------- utils
def log(msg: str) -> None:
    print(f"\033[1;33m==>\033[0m {msg}", flush=True)


def die(msg: str) -> NoReturn:
    print(f"\033[1;31merror:\033[0m {msg}", file=sys.stderr)
    sys.exit(1)


def packwiz(*args: str) -> None:
    exe = shutil.which("packwiz")
    if not exe:
        die("packwiz is not on PATH. Install it: https://packwiz.infra.link/installation/")
    subprocess.run([exe, *args], cwd=ROOT, check=True)


def read_pack() -> dict:
    with open(ROOT / "pack.toml", "rb") as f:
        return tomllib.load(f)


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")


def fetch(url: str, dest: Path, sha512: str | None = None, sha1: str | None = None) -> Path:
    """Download url to dest, using a hash-addressed cache and verifying hashes when given."""
    key = sha512 or sha1
    cached = CACHE / key if key else None
    if cached and cached.exists():
        data = cached.read_bytes()
    else:
        req = urllib.request.Request(url, headers=UA)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                break
            except OSError as e:  # network hiccup: retry
                if attempt == 2:
                    die(f"download failed: {url}: {e}")
                time.sleep(2 * (attempt + 1))
        if sha512 and hashlib.sha512(data).hexdigest() != sha512:
            die(f"sha512 mismatch for {url}")
        if sha1 and hashlib.sha1(data).hexdigest() != sha1:
            die(f"sha1 mismatch for {url}")
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(data)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def safe_join(base: Path, rel: str) -> Path:
    """Join an archive-provided path onto base, refusing anything that escapes it."""
    out = (base / rel).resolve()
    if base.resolve() not in out.parents and out != base.resolve():
        die(f"refusing unsafe path in archive: {rel}")
    return out


def zip_dir(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                info = zipfile.ZipInfo.from_file(p, p.relative_to(src).as_posix())
                if p.suffix == ".sh":
                    info.external_attr = 0o755 << 16  # keep start.sh executable
                with open(p, "rb") as f:
                    z.writestr(info, f.read(), zipfile.ZIP_DEFLATED)


# --------------------------------------------------------------------------- version
def set_version(version: str) -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?", version):
        die(f"not a valid version: {version}")
    pack = ROOT / "pack.toml"
    text = pack.read_text(encoding="utf-8")
    pack.write_text(re.sub(r'(?m)^version = ".*"$', f'version = "{version}"', text, count=1), encoding="utf-8")
    cfg = KUBEJS_CONFIG.read_text(encoding="utf-8")
    KUBEJS_CONFIG.write_text(re.sub(r"packVersion: '[^']*'", f"packVersion: '{version}'", cfg, count=1), encoding="utf-8")
    log(f"version set to {version}")


def check_version(pack: dict) -> None:
    m = re.search(r"packVersion: '([^']*)'", KUBEJS_CONFIG.read_text(encoding="utf-8"))
    if not m or m.group(1) != pack["version"]:
        die(
            f"kubejs packVersion ({m.group(1) if m else '?'}) != pack.toml version ({pack['version']}). "
            f"Run: python tools/build.py --set-version {pack['version']}"
        )


# --------------------------------------------------------------------------- targets
def build_mrpack(pack: dict) -> Path:
    out = DIST / f"{slug(pack['name'])}-{pack['version']}.mrpack"
    log(f"Modrinth pack -> {out.relative_to(ROOT)}")
    packwiz("modrinth", "export", "-o", str(out))
    shutil.copyfile(out, DIST / "mundus-foci-latest.mrpack")
    return out


def build_curseforge(pack: dict) -> Path:
    out = DIST / f"{slug(pack['name'])}-{pack['version']}-curseforge.zip"
    log(f"CurseForge pack -> {out.relative_to(ROOT)}")
    packwiz("curseforge", "export", "-o", str(out))
    return out


def fabric_server_launcher(mc: str, loader: str, dest: Path) -> None:
    with urllib.request.urlopen(urllib.request.Request("https://meta.fabricmc.net/v2/versions/installer", headers=UA)) as r:
        installer = next(i["version"] for i in json.load(r) if i.get("stable"))
    url = f"https://meta.fabricmc.net/v2/versions/loader/{mc}/{loader}/{installer}/server/jar"
    fetch(url, dest)


def build_server(pack: dict, mrpack: Path) -> Path:
    """Assemble a self-contained server from the mrpack (respects each file's env.server)."""
    stage = BUILD / "server"
    out = DIST / f"{slug(pack['name'])}-{pack['version']}-server.zip"
    log(f"Server pack -> {out.relative_to(ROOT)}")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    with zipfile.ZipFile(mrpack) as z:
        index = json.loads(z.read("modrinth.index.json"))
        files = [f for f in index["files"] if f.get("env", {}).get("server", "required") != "unsupported"]
        skipped = len(index["files"]) - len(files)
        for i, f in enumerate(files, 1):
            print(f"  [{i:3}/{len(files)}] {f['path']}", flush=True)
            fetch(f["downloads"][0], safe_join(stage, f["path"]), sha512=f["hashes"].get("sha512"), sha1=f["hashes"].get("sha1"))
        for prefix in ("overrides/", "server-overrides/"):
            for n in z.namelist():
                if n.startswith(prefix) and not n.endswith("/"):
                    dest = safe_join(stage, n[len(prefix):])
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(z.read(n))
    print(f"  {len(files)} server files, {skipped} client-only files skipped")

    deps = index["dependencies"]
    fabric_server_launcher(deps["minecraft"], deps["fabric-loader"], stage / "fabric-server-launch.jar")

    if SERVER_TEMPLATE.exists():
        shutil.copytree(SERVER_TEMPLATE, stage, dirs_exist_ok=True)
    (stage / "MUNDUS_FOCI_VERSION").write_text(pack["version"] + "\n", encoding="utf-8")

    zip_dir(stage, out)
    return out


def build_modlist(pack: dict) -> Path:
    rows = []
    for p in sorted((ROOT / "mods").glob("*.pw.toml")):
        with open(p, "rb") as f:
            m = tomllib.load(f)
        upd = m.get("update", {})
        if "modrinth" in upd:
            source, link = "Modrinth", f"https://modrinth.com/mod/{upd['modrinth']['mod-id']}"
        elif "curseforge" in upd:
            source, link = "CurseForge", f"https://www.curseforge.com/projects/{upd['curseforge']['project-id']}"
        else:
            source, link = "URL", m["download"].get("url", "")
        side = m.get("side", "both")
        opt = " (optional)" if m.get("option", {}).get("optional") else ""
        pinned = " 📌" if m.get("pin") else ""
        rows.append(f"| [{m['name']}]({link}) | {side}{opt} | {source}{pinned} | `{m['filename']}` |")
    out = ROOT / "MODLIST.md"
    out.write_text(
        f"# {pack['name']} {pack['version']} — Mod List\n\n"
        f"Minecraft {pack['versions']['minecraft']} · Fabric Loader {pack['versions']['fabric']} · {len(rows)} mods\n\n"
        "_Generated by `python tools/build.py modlist`. Do not edit by hand._\n\n"
        "Side: `both` = client and server, `client` = client only. 📌 = pinned (skipped by `packwiz update --all`).\n\n"
        "| Mod | Side | Source | File |\n|---|---|---|---|\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    log(f"Mod list -> MODLIST.md ({len(rows)} mods)")
    return out


def build_docker(pack: dict) -> None:
    if not shutil.which("docker"):
        die("docker not found on PATH")
    tag = f"mundus-foci-server:{pack['version']}"
    log(f"Docker image -> {tag} (and :latest)")
    subprocess.run(
        ["docker", "build", "-f", "server/Dockerfile", "-t", tag, "-t", "mundus-foci-server:latest", "."],
        cwd=ROOT,
        check=True,
    )


# ------------------------------------------------------------------------ test boot
def find_java(explicit: str | None) -> str:
    candidates = [explicit] if explicit else []
    if os.environ.get("JAVA_HOME"):
        candidates.append(str(Path(os.environ["JAVA_HOME"]) / "bin" / "java"))
    candidates.append("java")
    for c in candidates:
        exe = shutil.which(c) or (c if Path(c).exists() else None)
        if exe:
            return exe
    die("no Java found. Pass --java /path/to/java (Java 17 or 21).")


def test_server(server_zip: Path, java: str, timeout_min: int) -> None:
    """Unpack the server zip into build/test-server and boot it until 'Done' or a crash."""
    test = BUILD / "test-server"
    if test.exists():
        shutil.rmtree(test)
    with zipfile.ZipFile(server_zip) as z:
        z.extractall(test)
    # The test world is throw-away; running this test means you accept the Minecraft EULA
    # (https://aka.ms/MinecraftEULA) for this local test server.
    (test / "eula.txt").write_text("eula=true\n", encoding="utf-8")

    ver = subprocess.run([java, "-version"], capture_output=True, text=True).stderr.splitlines()[0]
    log(f"Booting test server with {ver}")
    proc = subprocess.Popen(
        [java, "-Xms2G", "-Xmx6G", "-jar", "fabric-server-launch.jar", "nogui"],
        cwd=test,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    done = threading.Event()
    tail: list[str] = []

    def pump() -> None:
        assert proc.stdout
        for line in proc.stdout:
            tail.append(line.rstrip())
            del tail[:-200]
            if re.search(r"Done \(\d", line):
                done.set()
            if re.search(r"(ERROR|Exception|Caused by|KubeJS.*error)", line):
                print("  " + line.rstrip())

    t = threading.Thread(target=pump, daemon=True)
    t.start()
    deadline = time.time() + timeout_min * 60
    while time.time() < deadline and proc.poll() is None and not done.is_set():
        time.sleep(1)

    if done.is_set():
        log("Server reached 'Done'. Stopping...")
        assert proc.stdin
        proc.stdin.write("stop\n")
        proc.stdin.flush()
        proc.wait(timeout=120)
        errs: list[str] = []
        for name in ("startup.log", "server.log"):
            kube = test / "logs" / "kubejs" / name
            if kube.exists():
                errs += [f"{name}: {l}" for l in kube.read_text(encoding="utf-8", errors="replace").splitlines() if "[ERR" in l]
        if errs:
            print("\nKubeJS script errors:\n  " + "\n  ".join(errs[:60]))
            die("server booted, but KubeJS reported script errors (see above and build/test-server/logs/kubejs/)")
        print("KubeJS scripts loaded without errors.")
        log("TEST PASSED")
        return

    if proc.poll() is None:
        proc.kill()
        print("\n".join(tail[-60:]))
        die(f"server did not finish starting within {timeout_min} minutes")
    print("\n".join(tail[-80:]))
    crash = sorted((test / "crash-reports").glob("*.txt")) if (test / "crash-reports").exists() else []
    die(f"server exited with code {proc.returncode}" + (f"; crash report: {crash[-1]}" if crash else ""))


# ------------------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="*", help=f"any of: {', '.join(TARGETS)} (default: all)")
    ap.add_argument("--set-version", metavar="X.Y.Z")
    ap.add_argument("--docker", action="store_true", help="also build the Docker image")
    ap.add_argument("--test-server", action="store_true", help="boot the built server pack once")
    ap.add_argument("--java", help="java executable for --test-server")
    ap.add_argument("--timeout", type=int, default=20, help="--test-server timeout in minutes")
    args = ap.parse_args()

    unknown = set(args.targets) - set(TARGETS)
    if unknown:
        die(f"unknown target(s): {', '.join(sorted(unknown))}. Choose from: {', '.join(TARGETS)}")
    if args.set_version:
        set_version(args.set_version)
    targets = set(args.targets or TARGETS)
    if args.test_server or args.docker:
        targets |= {"mrpack"}
    if args.test_server:
        targets |= {"server"}

    pack = read_pack()
    check_version(pack)
    DIST.mkdir(exist_ok=True)
    log("Refreshing packwiz index")
    packwiz("refresh")

    mrpack = build_mrpack(pack) if "mrpack" in targets or "server" in targets else None
    if "curseforge" in targets:
        build_curseforge(pack)
    server_zip = build_server(pack, mrpack) if "server" in targets and mrpack else None
    if "modlist" in targets:
        build_modlist(pack)
    if args.docker:
        build_docker(pack)
    if args.test_server and server_zip:
        test_server(server_zip, find_java(args.java), args.timeout)
    log("Done. Output in dist/")


if __name__ == "__main__":
    main()
