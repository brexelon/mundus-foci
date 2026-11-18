#!/usr/bin/env python3
"""Static dependency check for a built pack, without launching Minecraft.

Reads fabric.mod.json from every jar (including jar-in-jar) in the built server zip and in the
client file set from the mrpack, then reports required dependencies that no mod provides, and
declared "breaks" that are present. Forge mods loaded through Kilt are listed but not checked.

    python tools/check_deps.py            (run after `python tools/build.py`)

Version ranges are only checked loosely (missing mods are what usually break a pack).
"""
from __future__ import annotations

import io
import re
import json
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build import CACHE, read_pack, slug  # noqa: E402

BUILTIN = {"minecraft", "java", "fabricloader", "fabric", "fabric-api-base"}


Ver = tuple  # (core numbers, pre-release numbers or None)


def _vt(v: str) -> Ver | None:
    """Parse like Fabric's SemanticVersion: core[-prerelease][+build]."""
    core, _, pre = v.strip().lstrip("v").split("+")[0].partition("-")
    nums = re.findall(r"\d+", core)
    if not nums:
        return None
    return (tuple(int(n) for n in nums), tuple(int(n) for n in re.findall(r"\d+", pre)) if pre else None)


def _pad(a: tuple, b: tuple) -> tuple[tuple, tuple]:
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)), b + (0,) * (n - len(b))


def _cmp(a: Ver, b: Ver) -> int:
    x, y = _pad(a[0], b[0])
    if x != y:
        return (x > y) - (x < y)
    if a[1] is None or b[1] is None:  # a release sorts after its pre-releases
        return (a[1] is None) - (b[1] is None)
    x, y = _pad(a[1], b[1])
    return (x > y) - (x < y)


def satisfies(version: str, constraint: str | list) -> bool | None:
    """Loose Fabric version-range check. None = could not tell."""
    if isinstance(constraint, list):
        results = [satisfies(version, c) for c in constraint]
        return None if all(r is None for r in results) else any(r for r in results)
    v = _vt(version)
    if v is None:
        return None
    for part in str(constraint).split():
        if part in ("*", ""):
            continue
        m = re.match(r"^(>=|<=|>|<|=|\^|~)?(.*)$", part)
        op, target = m.group(1) or "=", m.group(2).replace(".x", "").replace(".*", "")
        t = _vt(target)
        if t is None:
            return None
        c = _cmp(v, t)
        ok = {
            ">=": c >= 0, "<=": c <= 0, ">": c > 0, "<": c < 0,
            "=": v[0][: len(t[0])] == t[0],
            "^": c >= 0 and v[0][:1] == t[0][:1],
            "~": c >= 0 and v[0][:2] == t[0][:2],
        }[op]
        if not ok:
            return False
    return True


def mod_jsons(data: bytes, depth: int = 0) -> list[dict]:
    """Return fabric.mod.json dicts for a jar and its nested jars."""
    out: list[dict] = []
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return out
    with z:
        if "fabric.mod.json" in z.namelist():
            try:
                out.append(json.loads(z.read("fabric.mod.json").decode("utf-8-sig"), strict=False))
            except json.JSONDecodeError:
                pass
        elif "META-INF/mods.toml" in z.namelist() and depth == 0:
            try:
                t = tomllib.loads(z.read("META-INF/mods.toml").decode("utf-8", "replace"))
                for m in t.get("mods", []):
                    out.append({"id": m.get("modId"), "_forge": True})
            except tomllib.TOMLDecodeError:
                out.append({"id": "?", "_forge": True})
        if depth < 3:
            for n in z.namelist():
                if n.startswith("META-INF/jars/") and n.endswith(".jar"):
                    for j in mod_jsons(z.read(n), depth + 1):
                        j["_nested"] = True
                        out.append(j)
    return out


def dep_version_breaks(version: str | None, rng: str | list) -> bool:
    # Unknown version or unparsable range: report it so a human can look.
    return version is None or satisfies(version, rng) is not False


def check(label: str, jars: dict[str, bytes]) -> int:
    provided: dict[str, str] = {i: "builtin" for i in BUILTIN}
    versions: dict[str, str] = {}
    top: list[tuple[str, dict]] = []
    forge: list[str] = []
    for name, data in jars.items():
        for mj in mod_jsons(data):
            if mj.get("_forge"):
                forge.append(f"{mj['id']} ({name})")
                continue
            ver = str(mj.get("version", ""))
            # Prefer the highest version when several jars bundle the same library.
            if mj["id"] not in versions or (_vt(ver) and _vt(versions[mj["id"]]) and _cmp(_vt(ver), _vt(versions[mj["id"]])) > 0):
                versions[mj["id"]] = ver
            provided.setdefault(mj["id"], name)
            for p in mj.get("provides", []):
                provided.setdefault(p, name)
            if not mj.get("_nested"):
                provided[mj["id"]] = name
                top.append((name, mj))
    problems = 0
    for name, mj in top:
        for dep, rng in (mj.get("depends") or {}).items():
            if dep not in provided:
                print(f"  [{label}] MISSING  {mj['id']} ({name}) requires '{dep}' {rng}")
                problems += 1
            elif dep in versions and satisfies(versions[dep], rng) is False:
                print(f"  [{label}] VERSION  {mj['id']} requires {dep} {rng}, pack has {versions[dep]}")
                problems += 1
        for brk, rng in (mj.get("breaks") or {}).items():
            if brk in provided and provided[brk] != name and dep_version_breaks(versions.get(brk), rng):
                print(f"  [{label}] BREAKS   {mj['id']} breaks {brk} {rng}, pack has {versions.get(brk)}")
                problems += 1
    print(f"[{label}] {len(top)} Fabric mods, {len(forge)} Forge mods via Kilt ({', '.join(forge) or '-'}), {problems} problem(s)")
    return problems


def main() -> None:
    pack = read_pack()
    base = f"{slug(pack['name'])}-{pack['version']}"
    server_zip = ROOT / "dist" / f"{base}-server.zip"
    mrpack = ROOT / "dist" / f"{base}.mrpack"
    if not server_zip.exists() or not mrpack.exists():
        sys.exit("build first: python tools/build.py")

    with zipfile.ZipFile(server_zip) as z:
        server = {n: z.read(n) for n in z.namelist() if n.startswith("mods/") and n.endswith(".jar")}

    client: dict[str, bytes] = {}
    with zipfile.ZipFile(mrpack) as z:
        idx = json.loads(z.read("modrinth.index.json"))
        for f in idx["files"]:
            if f["env"]["client"] == "unsupported":
                continue
            cached = CACHE / f["hashes"]["sha512"]
            if not cached.exists():
                from build import fetch  # downloads into the shared cache

                fetch(f["downloads"][0], ROOT / "build" / "tmp.jar", sha512=f["hashes"]["sha512"])
            client[f["path"]] = cached.read_bytes()
        for n in z.namelist():
            if n.startswith("overrides/mods/") and n.endswith(".jar"):
                client[n] = z.read(n)

    total = check("server", server) + check("client", client)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
