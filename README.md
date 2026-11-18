# Mundus Foci

*A world to call home.* A Fabric 1.20.1 modpack that keeps the heart of vanilla Minecraft and adds new
biomes, creatures, food, farming, furniture and quality-of-life touches without overhauling the game.

- **Minecraft** 1.20.1 · **Fabric Loader** 0.20.1 · **129 mods** (full list in [MODLIST.md](MODLIST.md))
- Managed with [packwiz](https://packwiz.infra.link/); built for clients **and** servers
- Ships as `.mrpack`, CurseForge `.zip`, a ready-to-run server `.zip`, and a Docker image

---

## What's inside

| Theme | Mods |
|---|---|
| **World generation** | Oh The Biomes We've Gone, YUNG's full suite (Dungeons, Mineshafts, Strongholds, Ocean Monuments, Desert & Jungle Temples, Witch Huts, Nether Fortresses, End Island, Bridges, Extras, Cave Biomes), ChoiceTheorem's Overhauled Village, Towns and Towers, Dungeons and Taverns |
| **Creatures** | Alex's Mobs *(Forge, via Kilt)*, Naturalist, Friends & Foes, Creeper Overhaul |
| **Furniture & decoration** | Macaw's full suite (Furniture, Windows, Doors, Trapdoors, Roofs, Bridges, Fences & Walls, Stairs, Paths, Lights, Paintings, Holidays), MrCrayfish's Furniture Mod: Refurbished, Cluttered, Handcrafted, Another Furniture, Chipped, Supplementaries + Amendments, Every Compat |
| **Farming & food** | Farmer's Delight Refabricated, Let's Do: Farm & Charm, Bakery, Brewery, Candlelight, Vinery, Meadow, Harvest with Ease, AppleSkin |
| **Storage & travel** | Sophisticated Backpacks & Storage (Fabric ports), Waystones, Nature's Compass, Carry On, Comforts, Trinkets, Xaero's Minimap & World Map |
| **Quality of life** | JEI, Jade, Inventory Profiles Next, Mouse Tweaks, Easy Anvils, Easy Magic, FallingTree, Leaves Be Gone, Clumps, Shulker Box Tooltip, You're in Grave Danger, Controlling, Searchables, YUNG's Menu Tweaks |
| **Multiplayer & admin** | Simple Voice Chat, No Chat Reports, spark, Chunky |
| **Performance** | Sodium, Lithium, FerriteCore, ModernFix, ImmediatelyFast, Entity Culling, More Culling, Dynamic FPS, Krypton, Indium, Sodium Extra, Reese's Sodium Options |
| **Visual polish** *(optional on the client)* | Iris Shaders, Continuity, 3D Skin Layers, Wavey Capes, Not Enough Animations, Visuality, Particle Rain, AmbientSounds, Zoomify, Better Third Person, Chat Heads |
| **Pack glue** | KubeJS (custom content below), Kilt (runs the Forge-only mods) |

### Custom content (KubeJS)

| | What it does |
|---|---|
| **Hearthstone** block set | Bricks, chiseled, stairs, slab and wall. Craft 2 bricks (item) + 2 cobblestone → 4; stonecutter supported. |
| **Hearth Lamp** | Full-brightness decorative lamp (hearthstone bricks + glowstone + campfire). |
| **Lodestone Charm** | Item magnet. Right-click to toggle, sneak to pause. Pulls items and XP within 6 blocks. |
| **Hearth Stew** | Farmer's Delight cooking-pot meal: Regeneration + Absorption. |
| **Trail Mix** | Fast-to-eat travel snack with a short Speed boost. |
| **QoL recipes** | Sticks and chests from logs, name tags, saddles, string from wool, leather from rotten flesh (smoker), raw ore blocks in the blast furnace, woodcutting on the stonecutter. |
| **Mod glue** | Farmer's Delight and Farm & Charm ingredients (meats, pasta) work in each other's recipes. |
| **Commands** | `/mundus help`, `/spawn` (with cooldown), `/coords`, `/playtime`; ops: `/gmc /gms /gma /gmsp`, `/mundus pregen <radius>` |
| **First join** | New players get a short field-guide book. Sleeping skips the night when 50% of players sleep. |

Settings for the commands, magnet and first-join behaviour are in
[kubejs/server_scripts/00_config.js](kubejs/server_scripts/00_config.js).

---

## Playing

Every client needs about **6 GB of RAM** allocated to Minecraft.

| Launcher | How |
|---|---|
| **Prism Launcher / Modrinth App / ATLauncher** | Import `Mundus-Foci-<ver>.mrpack`. Prism lets you toggle the optional visual mods. |
| **CurseForge App** | *Create Custom Profile → Import* and choose `Mundus-Foci-<ver>-curseforge.zip`. |
| **Auto-updating (Prism/MultiMC)** | Create a Fabric 1.20.1 instance, put [packwiz-installer-bootstrap.jar](https://github.com/packwiz/packwiz-installer-bootstrap/releases) in the `.minecraft` folder and set the pre-launch command to:<br>`"$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/YOUR_USER/mundus-foci/main/pack.toml`<br>The instance then updates itself every time it launches. |

## Hosting a server

Clients and the server **must run the same pack version**. Open **25565/tcp** for Minecraft and
**24454/udp** for voice chat.

**Option 1: server zip.** Unzip `Mundus-Foci-<ver>-server.zip`, run `start.bat` or `./start.sh`,
accept the EULA in `eula.txt`, and run it again. Needs Java 17 or 21. Updating is covered in the zip's
`README-SERVER.txt`.

**Option 2: Docker Compose.** Uses [itzg/minecraft-server](https://docker-minecraft-server.readthedocs.io/).
```sh
python tools/build.py mrpack           # creates dist/mundus-foci-latest.mrpack
cd server
# edit docker-compose.yml: set EULA: "TRUE" (and OPS / whitelist if you like)
docker compose up -d && docker compose logs -f mc
```
The world lives in `server/data/`. The compose file also has a commented **packwiz URL** mode that
re-syncs the pack from GitHub on every restart.

**Option 3: Docker image.** `python tools/build.py --docker` builds `mundus-foci-server:<ver>`. Tagged
GitHub releases also push `ghcr.io/<owner>/mundus-foci-server`.
```sh
docker run -d --name mundus-foci -p 25565:25565 -p 24454:24454/udp \
  -e EULA=TRUE -e MEMORY=6G -v mundus-world:/data mundus-foci-server
```

**Option 4: Coolify.** Runs the release image from Option 3 on a [Coolify](https://coolify.io/) server.
The host needs about **8 GB of RAM** (6 GB for Minecraft plus overhead).

1. Make the image pullable. GitHub creates `ghcr.io/<owner>/mundus-foci-server` as a private package,
   so either set it to **Public** (GitHub → *Packages* → `mundus-foci-server` → *Package settings*), or
   run `docker login ghcr.io` on the Coolify host with a token that has `read:packages`.
2. In Coolify, choose **+ New → Resource → Docker Compose Empty**, pick the server, and paste:
   ```yaml
   services:
     mc:
       image: ghcr.io/YOUR_USER/mundus-foci-server:v1.0.0   # use the release your players have
       restart: unless-stopped
       tty: true
       stdin_open: true
       ports:
         - "25565:25565"      # Minecraft
         - "24454:24454/udp"  # Simple Voice Chat
       environment:
         EULA: "TRUE"         # accepts https://aka.ms/MinecraftEULA
         MEMORY: 6G
         OPS: ${OPS:-}
         WHITELIST: ${WHITELIST:-}
       volumes:
         - mundus-world:/data
   volumes:
     mundus-world:
   ```
   Any other [itzg variable](https://docker-minecraft-server.readthedocs.io/en/latest/variables/) can be
   added under `environment`.
3. In the **Environment Variables** tab, set `OPS` (and `WHITELIST`, comma-separated) to Minecraft usernames.
4. Leave the **Domains** field empty. Minecraft doesn't use HTTP, so Coolify's proxy isn't involved and
   players connect straight to the host's IP or DNS name. Open **25565/tcp** and **24454/udp** in the
   host's firewall (`ufw`) and in your cloud provider's firewall.
5. Click **Deploy** and watch the **Logs** tab. The first boot takes several minutes.
6. To run server commands, open the **Terminal** tab, pick the `mc` container and use `rcon-cli`, for example
   `rcon-cli mundus pregen 3000`.

To update, back up the `mundus-world` volume (listed under **Persistent Storage**), change the image tag to
the new release and **Redeploy**. To follow `main` instead of releases, use `itzg/minecraft-server:java17`
as the image and copy the **packwiz URL** variables (Option B) from
[server/docker-compose.yml](server/docker-compose.yml). That mode re-syncs the pack on every restart.

On a fresh server, pre-generate the world to reduce exploration lag: `/mundus pregen 3000`.

---

## Maintaining the pack

You need [packwiz](https://packwiz.infra.link/installation/) and Python 3.11+.

```sh
packwiz modrinth add <slug>       # add a mod from Modrinth (dependencies are offered automatically)
packwiz curseforge add <slug>     # add a mod only on CurseForge
packwiz remove <slug>             # remove a mod
packwiz update --all              # update every mod that isn't pinned
packwiz refresh                   # re-index after editing files in kubejs/ or config/

python tools/build.py             # build every format into dist/ and regenerate MODLIST.md
python tools/check_deps.py        # static check: missing dependencies or "breaks" conflicts per side
python tools/build.py --test-server --java "C:/path/to/java17/bin/java"   # boot the server once
python tools/build.py --set-version 1.1.0   # bump the version (pack.toml + KubeJS) before a release
```

**Release flow:** bump the version, update `CHANGELOG.md`, commit, then `git tag v1.1.0 && git push --tags`.
GitHub Actions builds every format, checks dependencies, boots a test server, publishes a GitHub release
and pushes the Docker image.

### Rules worth knowing

- **Prefer Modrinth.** CurseForge-only mods (currently MrCrayfish's Furniture + Framework) are embedded in
  the `.mrpack` as overrides. That is fine for private use, but Modrinth won't accept the pack for public
  listing while they're included.
- **Worldgen and gameplay mods must be `side = "both"`**, even when Modrinth says "server only".
  Singleplayer runs an integrated server, so the client needs them too. After adding a mod, check its
  `side` in `mods/<slug>.pw.toml`, then run `tools/check_deps.py`. For example, Athena is tagged
  client-only on Modrinth but Chipped needs it on the server.
- **Optional client mods** have an `[option]` block in their `.pw.toml`. They appear as toggles in
  Prism and packwiz-installer.
- **Pinned mods** (`packwiz pin`) are skipped by `packwiz update --all`: Kilt, Alex's Mobs and Citadel.
  The Forge mods have to be pinned because packwiz only looks for Fabric versions. To update one by hand:
  `packwiz modrinth add --project-id alexs-mobs --version-id <forge-version-id> -y`.
- **Line endings:** packwiz hashes every file, so `.gitattributes` forces LF. Don't turn that off.
- **Textures** for the custom content are generated by `python tools/gen_textures.py`.

### ⚠ Kilt (Forge mods on Fabric)

Alex's Mobs and Citadel are the only Forge mods in the pack, and only because neither has a Fabric
version. Everything else that was Forge-first (Cluttered, Sophisticated Backpacks, Farmer's Delight) uses
a native Fabric build. **Kilt is marked "very experimental", and its 1.20.1 line was declared
end-of-life on 8 Nov 2026.** If Alex's Mobs misbehaves (crashes, invisible mobs, broken spawns), remove it
cleanly. Naturalist and Friends & Foes still cover the new-wildlife side:

```sh
packwiz remove alexs-mobs && packwiz remove citadel && packwiz remove kilt
# keep fabric-language-kotlin: Inventory Profiles Next, libIPN and Zoomify also need it
```
