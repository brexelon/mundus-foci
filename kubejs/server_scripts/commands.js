// Mundus Foci: commands & aliases. Changes need /reload (commands re-register on reload).
//
//   /mundus [help|version]     everyone   pack info
//   /mundus pregen <radius>    op (3)     pre-generate the overworld around spawn with Chunky
//   /coords                    everyone   share your position in chat
//   /playtime                  everyone   show your total play time
//   /gmc /gms /gma /gmsp       op (2)     gamemode shortcuts

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

  // ----------------------------------------------------------------- /coords
  event.register(
    Commands.literal('coords').executes(ctx => {
      let player = ctx.source.getPlayerOrException()
      // KubeJS's LevelKJS.getDimension() shadows vanilla dimension(), so read it as a property.
      let dim = String(ctx.source.getLevel().dimension)
      let msg = Text.gold(player.username)
        .append(Text.gray(' is at '))
        .append(Text.yellow(`${Math.floor(player.x)} ${Math.floor(player.y)} ${Math.floor(player.z)}`))
        .append(Text.gray(` in ${dim}`))
      ctx.source.server.tell(msg)
      return 1
    })
  )

  // --------------------------------------------------------------- /playtime
  event.register(
    Commands.literal('playtime').executes(ctx => {
      let player = ctx.source.getPlayerOrException()
      // KubeJS wraps getStats() in PlayerStatsJS, which has its own play time getter.
      let ticks = player.stats.playTime
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
