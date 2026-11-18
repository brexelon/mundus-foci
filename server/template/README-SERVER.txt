MUNDUS FOCI - DEDICATED SERVER
==============================

Requirements: Java 17 or 21 (64-bit), 6 GB+ RAM for the server, ports 25565/tcp and 24454/udp.

First start
  1. Start once:   Windows: start.bat        Linux/macOS: ./start.sh
  2. Open eula.txt and set eula=true (you are agreeing to https://aka.ms/MinecraftEULA).
  3. Start again. First boot downloads Minecraft and takes a few minutes.
  4. Optional: pre-generate the world to cut lag when players explore:
       /mundus pregen 3000

RAM: edit MEMORY in start.bat, or run  MEMORY=8G ./start.sh

Ports
  25565/tcp  Minecraft
  24454/udp  Simple Voice Chat (forward this too, or voice chat will not connect)

Updating to a new Mundus Foci version
  1. Stop the server and BACK UP the whole folder (especially world/).
  2. Delete the old  mods/  and  kubejs/  folders.
  3. Extract the new server zip over this folder. It never contains world/, server.properties,
     ops.json, whitelist.json or eula.txt, so those are kept.
  4. Start the server.

Clients must use the SAME pack version as the server.
