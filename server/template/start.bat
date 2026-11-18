@echo off
rem Mundus Foci dedicated server launcher (Windows).
rem Change MEMORY below (or set it before running) to give the server more or less RAM.
cd /d "%~dp0"

if not defined JAVA set JAVA=java
if not defined MEMORY set MEMORY=6G
if not defined JVM_ARGS set JVM_ARGS=-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15

if not exist server.properties copy /y server.properties.default server.properties >nul

findstr /b /c:"eula=true" eula.txt >nul 2>&1
if errorlevel 1 (
  if not exist eula.txt echo eula=false> eula.txt
  echo You must accept the Minecraft EULA ^(https://aka.ms/MinecraftEULA^) to run a server.
  echo Open eula.txt, change eula=false to eula=true, then run start.bat again.
  pause
  exit /b 1
)

"%JAVA%" -Xms%MEMORY% -Xmx%MEMORY% %JVM_ARGS% -jar fabric-server-launch.jar nogui
pause
