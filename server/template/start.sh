#!/usr/bin/env sh
# Mundus Foci dedicated server launcher (Linux / macOS).
# Override settings with environment variables, e.g.:  MEMORY=8G ./start.sh
set -e
cd "$(dirname "$0")"

JAVA="${JAVA:-java}"
MEMORY="${MEMORY:-6G}"
JVM_ARGS="${JVM_ARGS:--XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15}"

[ -f server.properties ] || cp server.properties.default server.properties

if ! grep -qs '^eula=true' eula.txt; then
  [ -f eula.txt ] || echo 'eula=false' > eula.txt
  echo "You must accept the Minecraft EULA (https://aka.ms/MinecraftEULA) to run a server."
  echo "Open eula.txt, change eula=false to eula=true, then run ./start.sh again."
  exit 1
fi

# shellcheck disable=SC2086
exec "$JAVA" -Xms"$MEMORY" -Xmx"$MEMORY" $JVM_ARGS -jar fabric-server-launch.jar nogui
