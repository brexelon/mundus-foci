// Mundus Foci: gameplay events. Settings live in 00_config.js (global.MF_CONFIG).

const $ItemEntity = Java.loadClass('net.minecraft.world.entity.item.ItemEntity')
const $ExperienceOrb = Java.loadClass('net.minecraft.world.entity.ExperienceOrb')

const CHARM_ID = 'mundusfoci:lodestone_charm'
const CHARM_ACTIVE_NBT = '{MFActive:1b,Enchantments:[{}],HideFlags:1}' // empty enchant list = glint

// ------------------------------------------------------------- Lodestone Charm
function isActiveCharm(stack) {
  if (stack.isEmpty() || stack.id != CHARM_ID) return false
  let tag = stack.getTag()
  return tag != null && tag.getBoolean('MFActive')
}

function hasActiveCharm(player) {
  let inv = player.getInventory()
  for (let i = 0; i < inv.getContainerSize(); i++) {
    if (isActiveCharm(inv.getItem(i))) return true
  }
  return false
}

ItemEvents.rightClicked(CHARM_ID, event => {
  let player = event.player
  let nowActive = !isActiveCharm(event.item)
  player.setItemInHand(event.hand, nowActive ? Item.of(CHARM_ID, CHARM_ACTIVE_NBT) : Item.of(CHARM_ID))
  player.setStatusMessage(nowActive ? Text.green('Lodestone Charm: active') : Text.gray('Lodestone Charm: inactive'))
  event.server.runCommandSilent(
    `execute at ${player.username} run playsound minecraft:block.amethyst_block.chime player ${player.username} ~ ~ ~ 0.7 ${nowActive ? 1.4 : 0.7}`
  )
  event.cancel()
})

PlayerEvents.tick(event => {
  let cfg = global.MF_CONFIG.magnet
  let player = event.player
  if (player.tickCount % cfg.intervalTicks != 0) return
  if (player.isSpectator() || player.isShiftKeyDown() || !player.isAlive()) return
  if (!hasActiveCharm(player)) return

  let box = player.getBoundingBox().inflate(cfg.radius)
  let x = player.getX()
  let y = player.getY()
  let z = player.getZ()

  event.level.getEntitiesOfClass($ItemEntity, box).forEach(item => {
    if (!item.hasPickUpDelay()) item.setPos(x, y, z)
  })
  if (cfg.pullXp) {
    event.level.getEntitiesOfClass($ExperienceOrb, box).forEach(orb => orb.setPos(x, y, z))
  }
})

// --------------------------------------------------------------- Hearth Stew
// Bowl foods return their bowl.
ItemEvents.foodEaten('mundusfoci:hearth_stew', event => {
  if (!event.player.isCreative()) event.player.give('minecraft:bowl')
})

// ------------------------------------------------------------- First join
function guideBook() {
  // A leading "" stops the first element's style from bleeding into the rest of the page.
  let page = parts => JSON.stringify([''].concat(parts))
  let pages = [
    page([
      { text: 'Mundus Foci\n', bold: true, color: 'dark_red' },
      { text: 'A world to call home.\n\n', italic: true, color: 'dark_gray' },
      { text: 'This pack keeps the heart of vanilla Minecraft and fills the world with new biomes, creatures, food and furniture.\n\nTurn the page for tips.' },
    ]),
    page([
      { text: 'Getting Around\n\n', bold: true },
      { text: "- Nature's Compass", bold: true },
      { text: ' finds any biome.\n' },
      { text: '- Waystones', bold: true },
      { text: ' link your bases.\n' },
      { text: '- Xaero\'s maps', bold: true },
      { text: ': press Y (minimap) or M (world map).\n' },
      { text: '- /spawn', bold: true },
      { text: ' takes you back to world spawn.' },
    ]),
    page([
      { text: 'Food & Farming\n\n', bold: true },
      { text: "Build a Cooking Pot (Farmer's Delight) to make stews. Crops from Farmer's Delight and Farm & Charm can be swapped in recipes.\n\nTry " },
      { text: 'Hearth Stew', bold: true },
      { text: ': meat, onion, carrot, potato and a brown mushroom.' },
    ]),
    page([
      { text: 'Handy Things\n\n', bold: true },
      { text: '- Hover + R', bold: true },
      { text: ' shows any recipe (JEI).\n' },
      { text: '- Lodestone Charm', bold: true },
      { text: ' pulls items to you. Right-click to toggle, sneak to pause.\n' },
      { text: '- Sneak + empty hand', bold: true },
      { text: ' picks up chests and animals (Carry On).' },
    ]),
    page([
      { text: 'Commands\n\n', bold: true },
      { text: '/mundus help\n/spawn\n/coords\n/playtime\n\n' },
      { text: 'Have fun, and welcome home.', italic: true },
    ]),
  ]
  return Item.of('minecraft:written_book', {
    title: 'Mundus Foci Field Guide',
    author: 'The Hearthkeepers',
    generation: 0,
    pages: pages,
  })
}

PlayerEvents.loggedIn(event => {
  let player = event.player
  if (!player.stages.has('mundusfoci_welcomed')) {
    player.stages.add('mundusfoci_welcomed')
    if (global.MF_CONFIG.giveGuideBook) player.give(guideBook())
    player.tell(Text.gold(`Welcome to Mundus Foci, ${player.username}! `).append(Text.gray('Check the field guide in your inventory.')))
  } else {
    player.tell(Text.gold('Welcome back to Mundus Foci. ').append(Text.gray('/mundus help for commands.')))
  }
})

// ------------------------------------------------------ One-time gamerules
ServerEvents.loaded(event => {
  let server = event.server
  let data = server.persistentData
  if (data.getBoolean('mundusfoci_gamerules_applied')) return
  let rules = global.MF_CONFIG.initialGamerules
  Object.keys(rules).forEach(rule => server.runCommandSilent(`gamerule ${rule} ${rules[rule]}`))
  data.putBoolean('mundusfoci_gamerules_applied', true)
})
