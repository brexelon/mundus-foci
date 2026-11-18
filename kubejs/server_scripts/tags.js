// Mundus Foci: tags. Reload with /reload.

ServerEvents.tags('item', event => {
  // Used by the Trail Mix recipe.
  event.add('mundusfoci:snack_seeds', [
    'minecraft:wheat_seeds',
    'minecraft:pumpkin_seeds',
    'minecraft:melon_seeds',
  ])

  // --- Farmer's Delight <-> Let's Do: Farm & Charm ingredient bridging ---
  // FD uses c:foods/raw_meats/<meat>; Farm & Charm uses c:raw_<meat>. Crops (tomato, onion,
  // cabbage/lettuce) and dough already share tags. Items are added in one direction only and the
  // FD tag is nested into the F&C tag, which keeps the tags from referencing each other in a loop.
  const MEATS = {
    beef: ['farm_and_charm:minced_beef'],
    chicken: ['farm_and_charm:chicken_parts'],
    mutton: ['farm_and_charm:lamb_ham'],
    pork: [],
    bacon: ['farm_and_charm:bacon'],
  }
  Object.keys(MEATS).forEach(meat => {
    let fdTag = `c:foods/raw_meats/raw_${meat}`
    if (MEATS[meat].length > 0) event.add(fdTag, MEATS[meat])
    event.add(`c:raw_${meat}`, `#${fdTag}`)
  })

  event.add('c:foods/pastas/raw_pastas', 'farm_and_charm:raw_pasta')
  event.add('c:pasta', 'farmersdelight:raw_pasta')
})
