// Mundus Foci: client-side tooltips. Reload with F3+T.

ItemEvents.tooltip(event => {
  event.addAdvanced('mundusfoci:lodestone_charm', (item, advanced, text) => {
    let tag = item.getTag()
    let active = tag != null && tag.getBoolean('MFActive')
    text.add(1, active ? Text.green('Active') : Text.darkGray('Inactive'))
    text.add(2, Text.gray('Pulls nearby items and XP while in your inventory.'))
    text.add(3, Text.darkGray('Right-click to toggle. Sneak to pause.'))
  })

  event.add('mundusfoci:hearth_stew', Text.gray('Slow-cooked in a Cooking Pot. Warms you through.'))
  event.add('mundusfoci:trail_mix', Text.gray('Quick to eat on the road.'))
  event.add('mundusfoci:hearth_lamp', Text.gray('A warm, bright light.'))
})
