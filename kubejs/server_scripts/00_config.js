// priority: 1000
// Mundus Foci server-side settings. Edit these, then run /reload in-game (or restart the server).
// Loaded first (highest priority) so every other server script can read global.MF_CONFIG.

global.MF_CONFIG = {
  // Kept in sync with pack.toml by `python tools/build.py --set-version X.Y.Z`. Do not edit by hand.
  packVersion: '1.0.2',

  // /spawn: teleport to world spawn. Ops (permission level 2+) bypass the cooldown.
  spawnCommand: {
    enabled: true,
    permissionLevel: 0, // 0 = everyone, 2 = ops only
    cooldownSeconds: 300,
  },

  // Lodestone Charm (item magnet).
  magnet: {
    radius: 6.0, // blocks
    intervalTicks: 4, // how often to pull (20 ticks = 1 second)
    pullXp: true,
  },

  // Gamerules applied ONCE when a world is first loaded with this pack.
  // Change them later with /gamerule like normal; this will not overwrite your changes.
  initialGamerules: {
    playersSleepingPercentage: 50,
  },

  // Give each new player the Mundus Foci field guide on first join.
  giveGuideBook: true,
}
