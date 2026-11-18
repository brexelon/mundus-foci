# Self-contained Mundus Foci server image with the pack baked in.
# Build from the repo root after `python tools/build.py mrpack`:
#
#   docker build -f server/Dockerfile -t mundus-foci-server .
#   docker run -d -p 25565:25565 -p 24454:24454/udp -e EULA=TRUE -v mundus-world:/data mundus-foci-server
#
# (or simply: python tools/build.py --docker)
FROM itzg/minecraft-server:java17

COPY dist/mundus-foci-latest.mrpack /modpacks/mundus-foci.mrpack

ENV TYPE=MODRINTH \
    MODRINTH_MODPACK=/modpacks/mundus-foci.mrpack \
    MEMORY=6G \
    USE_AIKAR_FLAGS=TRUE \
    MOTD="§6Mundus Foci§r §7- a world to call home" \
    DIFFICULTY=normal \
    VIEW_DISTANCE=10 \
    SIMULATION_DISTANCE=8 \
    ALLOW_FLIGHT=TRUE \
    MAX_TICK_TIME=-1 \
    SPAWN_PROTECTION=0

EXPOSE 25565/tcp 24454/udp
