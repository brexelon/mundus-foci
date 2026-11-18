// Mundus Foci: commands & aliases. Changes need /reload (commands re-register on reload).
//
//   /mundus [help|version]     everyone   pack info
//   /mundus pregen <radius>    op (3)     pre-generate the overworld around spawn with Chunky
//   /spawn                     config     teleport to world spawn (cooldown, see 00_config.js)
//   /coords                    everyone   share your position in chat
//   /playtime                  everyone   show your total play time
//   /gmc /gms /gma /gmsp       op (2)     gamemode shortcuts

const $Stats = Java.loadClass('net.minecraft.stats.Stats')

ServerEvents.commandRegistry(event => {
  const { commands: Commands, arguments: Arguments } = event

  const HELP = [
    ['/spawn', 'Teleport to world spawn'],
    ['/coords', 'Share your position in chat'],
    ['/playtime', 'Show your total play time'],
    ['/mundus version', 'Show the pack version'],
  ]

  const help = ctx => {
    let src = ctx.source
    src.sendSystemMessage(Text.gold(`Mundus Foci ${global.MF_CONFIG.packVersion}`).bold(true))
    HELP.forEach(h => src.sendSystemMessage(Text.yellow(h[0]).append(Text.gray(` - ${h[1]}`))))
    if (src.hasPermission(2)) {
      src.sendSystemMessage(Text.yellow('/gmc /gms /gma /gmsp').append(Text.gray(' - Gamemode shortcuts (op)')))
    }
    if (src.hasPermission(3)) {
      src.sendSystemMessage(Text.yellow('/mundus pregen <radius>').append(Text.gray(' - Pre-generate chunks around spawn (op)')))
    }
    return 1
  }

  const pregen = ctx => {
    let radius = Arguments.INTEGER.getResult(ctx, 'radius')
    let server = ctx.source.server
    let spawn = server.overworld().getSharedSpawnPos()
    ;[
      'chunky world minecraft:overworld',
      'chunky shape square',
      `chunky center ${spawn.x} ${spawn.z}`,
      `chunky radius ${radius}`,
      'chunky start',
    ].forEach(cmd => server.runCommandSilent(cmd))
    ctx.source.sendSystemMessage(
      Text.green(`Pre-generating a ${radius}-block radius around spawn. `).append(Text.gray('Use /chunky progress, /chunky pause or /chunky cancel.'))
    )
    return 1
  }

  event.register(
    Commands.literal('mundus')
      .executes(help)
      .then(Commands.literal('help').executes(help))
      .then(Commands.literal('version').executes(ctx => {
        ctx.source.sendSystemMessage(Text.gold(`Mundus Foci ${global.MF_CONFIG.packVersion}`))
        return 1
      }))
      .then(Commands.literal('pregen')
        .requires(src => src.hasPermission(3))
        .then(Commands.argument('radius', Arguments.INTEGER.create(event)).executes(pregen)))
  )

  // ------------------------------------------------------------------ /spawn
  const spawnCfg = global.MF_CONFIG.spawnCommand
  if (spawnCfg.enabled) {
    event.register(
      Commands.literal('spawn')
        .requires(src => src.hasPermission(spawnCfg.permissionLevel))
        .executes(ctx => {
          let player = ctx.source.getPlayerOrException()
          let now = Date.now()
          let last = player.persistentData.getLong('mundusfoci_spawn_last')
          let waitMs = spawnCfg.cooldownSeconds * 1000 - (now - last)
          if (waitMs > 0 && !ctx.source.hasPermission(2)) {
            player.tell(Text.red(`/spawn is on cooldown for another ${Math.ceil(waitMs / 1000)}s.`))
            return 0
          }
          let level = ctx.source.server.overworld()
          let pos = level.getSharedSpawnPos()
          player.teleportTo(level, pos.x + 0.5, pos.y, pos.z + 0.5, player.getYRot(), player.getXRot())
          player.persistentData.putLong('mundusfoci_spawn_last', now)
          player.tell(Text.green('Welcome back to spawn.'))
          return 1
        })
    )
  }

  // ----------------------------------------------------------------- /coords
  event.register(
    Commands.literal('coords').executes(ctx => {
      let player = ctx.source.getPlayerOrException()
      let dim = String(ctx.source.getLevel().dimension().location())
      let msg = Text.gold(player.username)
        .append(Text.gray(' is at '))
        .append(Text.yellow(`${Math.floor(player.getX())} ${Math.floor(player.getY())} ${Math.floor(player.getZ())}`))
        .append(Text.gray(` in ${dim}`))
      ctx.source.server.tell(msg)
      return 1
    })
  )

  // --------------------------------------------------------------- /playtime
  event.register(
    Commands.literal('playtime').executes(ctx => {
      let player = ctx.source.getPlayerOrException()
      let ticks = player.getStats().getValue($Stats.CUSTOM.get($Stats.PLAY_TIME))
      let minutes = Math.floor(ticks / 1200)
      let text = `${Math.floor(minutes / 60)}h ${minutes % 60}m`
      player.tell(Text.gray('You have played on this world for ').append(Text.gold(text)))
      return 1
    })
  )

  // ------------------------------------------------------- Gamemode aliases
  const GAMEMODES = { gmc: 'creative', gms: 'survival', gma: 'adventure', gmsp: 'spectator' }
  Object.keys(GAMEMODES).forEach(alias => {
    event.register(
      Commands.literal(alias)
        .requires(src => src.hasPermission(2))
        .executes(ctx => {
          let player = ctx.source.getPlayerOrException()
          ctx.source.server.runCommandSilent(`gamemode ${GAMEMODES[alias]} ${player.username}`)
          player.tell(Text.gray(`Gamemode set to ${GAMEMODES[alias]}.`))
          return 1
        })
    )
  })
})
