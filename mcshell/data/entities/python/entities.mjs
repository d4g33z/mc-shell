// Helper for picker blocks (can be shared if in a common scope)
function createPickerGenerator(block, generator, fieldName = 'ENTITY_ID') { const blockId = block.getFieldValue(fieldName); return [`'${blockId}'`, generator.ORDER_ATOMIC]; }

export function installMCEntityGenerator(pythonGenerator) {

    pythonGenerator.forBlock['minecraft_picker_entity_hostile_mobs'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'ENTITY_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_entity_minecarts'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'ENTITY_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_entity_miscellaneous_entities'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'ENTITY_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_entity_passive_mobs'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'ENTITY_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_entity_projectiles'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'ENTITY_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_entity_utility_and_special'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'ENTITY_ID');
    };

} // End of installEntityGenerators
