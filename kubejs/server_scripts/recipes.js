// Mundus Foci: recipes. Reload with /reload.
// Every recipe gets an explicit id under mundusfoci: so it is easy to find in JEI / override in datapacks.

ServerEvents.recipes(event => {
  const id = path => `mundusfoci:${path}`

  // ------------------------------------------------------------------ Hearthstone
  event.shaped('4x mundusfoci:hearthstone', ['BS', 'SB'], {
    B: 'minecraft:brick',
    S: '#minecraft:stone_crafting_materials',
  }).id(id('hearthstone'))

  event.shaped('4x mundusfoci:hearthstone_bricks', ['HH', 'HH'], {
    H: 'mundusfoci:hearthstone',
  }).id(id('hearthstone_bricks'))

  event.shaped('mundusfoci:chiseled_hearthstone', ['S', 'S'], {
    S: 'mundusfoci:hearthstone_brick_slab',
  }).id(id('chiseled_hearthstone'))

  event.shaped('4x mundusfoci:hearthstone_brick_stairs', ['B  ', 'BB ', 'BBB'], {
    B: 'mundusfoci:hearthstone_bricks',
  }).id(id('hearthstone_brick_stairs'))

  event.shaped('6x mundusfoci:hearthstone_brick_slab', ['BBB'], {
    B: 'mundusfoci:hearthstone_bricks',
  }).id(id('hearthstone_brick_slab'))

  event.shaped('6x mundusfoci:hearthstone_brick_wall', ['BBB', 'BBB'], {
    B: 'mundusfoci:hearthstone_bricks',
  }).id(id('hearthstone_brick_wall'))

  // Stonecutter: everything from raw hearthstone or bricks, vanilla-style.
  // (Rhino, KubeJS's JS engine, mishandles `const` inside for-loops, so loops use forEach.)
  ;['hearthstone', 'hearthstone_bricks'].forEach(src => {
    let input = `mundusfoci:${src}`
    if (src === 'hearthstone') {
      event.stonecutting('mundusfoci:hearthstone_bricks', input).id(id(`stonecutting/hearthstone_bricks_from_${src}`))
    }
    event.stonecutting('mundusfoci:chiseled_hearthstone', input).id(id(`stonecutting/chiseled_hearthstone_from_${src}`))
    event.stonecutting('mundusfoci:hearthstone_brick_stairs', input).id(id(`stonecutting/hearthstone_brick_stairs_from_${src}`))
    event.stonecutting('2x mundusfoci:hearthstone_brick_slab', input).id(id(`stonecutting/hearthstone_brick_slab_from_${src}`))
    event.stonecutting('mundusfoci:hearthstone_brick_wall', input).id(id(`stonecutting/hearthstone_brick_wall_from_${src}`))
  })

  event.shaped('2x mundusfoci:hearth_lamp', [' B ', 'GCG', ' B '], {
    B: 'mundusfoci:hearthstone_bricks',
    G: 'minecraft:glowstone_dust',
    C: 'minecraft:campfire',
  }).id(id('hearth_lamp'))

  // ------------------------------------------------------------------------ Items
  event.shaped('mundusfoci:lodestone_charm', ['R R', 'I I', 'IEI'], {
    R: 'minecraft:redstone',
    I: 'minecraft:iron_ingot',
    E: 'minecraft:ender_pearl',
  }).id(id('lodestone_charm'))

  event.shapeless('4x mundusfoci:trail_mix', [
    '#c:foods/berries',
    'minecraft:dried_kelp',
    '#mundusfoci:snack_seeds',
    'minecraft:honey_bottle', // the glass bottle is returned automatically
  ]).id(id('trail_mix'))

  // Farmer's Delight cooking pot. Uses shared c: tags so crops from either
  // Farmer's Delight or Let's Do: Farm & Charm are accepted.
  event.custom({
    type: 'farmersdelight:cooking',
    cookingtime: 200,
    experience: 1.0,
    recipe_book_tab: 'meals',
    ingredients: [
      { tag: 'c:foods/raw_meats' },
      { tag: 'c:crops/onion' },
      { tag: 'c:crops/carrot' },
      { tag: 'c:crops/potato' },
      { item: 'minecraft:brown_mushroom' },
    ],
    container: { item: 'minecraft:bowl' },
    result: { item: 'mundusfoci:hearth_stew' },
  }).id(id('cooking/hearth_stew'))

  // ------------------------------------------------------- Vanilla QoL recipes
  event.shaped('16x minecraft:stick', ['L', 'L'], { L: '#minecraft:logs' }).id(id('sticks_from_logs'))

  event.shaped('4x minecraft:chest', ['LLL', 'L L', 'LLL'], { L: '#minecraft:logs' }).id(id('chests_from_logs'))

  event.shapeless('minecraft:name_tag', [
    'minecraft:paper', 'minecraft:paper', 'minecraft:string', 'minecraft:iron_ingot',
  ]).id(id('name_tag'))

  event.shaped('minecraft:saddle', ['LLL', 'LSL', 'I I'], {
    L: 'minecraft:leather',
    S: 'minecraft:string',
    I: 'minecraft:iron_ingot',
  }).id(id('saddle'))

  event.shapeless('4x minecraft:string', ['#minecraft:wool']).id(id('string_from_wool'))

  event.smoking('minecraft:leather', 'minecraft:rotten_flesh').xp(0.1).id(id('smoking/leather_from_rotten_flesh'))

  // Raw ore blocks in the blast furnace: same yield and XP as nine single smelts, nine times as long.
  ;['iron', 'gold', 'copper'].forEach(metal => {
    event.blasting(`minecraft:${metal}_block`, `minecraft:raw_${metal}_block`)
      .xp(metal === 'gold' ? 9.0 : 6.3)
      .cookingTime(900)
      .id(id(`blasting/${metal}_block_from_raw_block`))
  })

  // Woodcutting on the stonecutter for vanilla wood types.
  const WOODS = [
    ['oak', '#minecraft:oak_logs'],
    ['spruce', '#minecraft:spruce_logs'],
    ['birch', '#minecraft:birch_logs'],
    ['jungle', '#minecraft:jungle_logs'],
    ['acacia', '#minecraft:acacia_logs'],
    ['dark_oak', '#minecraft:dark_oak_logs'],
    ['mangrove', '#minecraft:mangrove_logs'],
    ['cherry', '#minecraft:cherry_logs'],
    ['crimson', '#minecraft:crimson_stems'],
    ['warped', '#minecraft:warped_stems'],
  ]
  WOODS.forEach(entry => {
    let wood = entry[0]
    let planks = `minecraft:${wood}_planks`
    event.stonecutting(`4x ${planks}`, entry[1]).id(id(`woodcutting/${wood}_planks`))
    event.stonecutting(`2x minecraft:${wood}_slab`, planks).id(id(`woodcutting/${wood}_slab`))
    event.stonecutting(`minecraft:${wood}_stairs`, planks).id(id(`woodcutting/${wood}_stairs`))
  })
})
