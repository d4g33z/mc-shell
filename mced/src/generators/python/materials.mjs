// src/generators/python/materials.js (Auto-generated content)
import { pythonGenerator } from 'blockly/python';

// Helper function for simple picker blocks
function createPickerGenerator(block, generator, fieldName = 'MATERIAL_ID') {
    const blockId = block.getFieldValue(fieldName);
    return [`'${blockId}'`, generator.ORDER_ATOMIC];
}

export function installMCMaterialsGenerator(pythonGenerator) {

    pythonGenerator.forBlock['minecraft_material_banner'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('BANNER'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('BANNER'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('BANNER'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_BANNER`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_bed'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('BED'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('BED'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('BED'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_BED`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_candle'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('CANDLE'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('CANDLE'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('CANDLE'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_CANDLE`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_carpet'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('CARPET'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('CARPET'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('CARPET'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_CARPET`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_concrete'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('CONCRETE'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('CONCRETE'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('CONCRETE'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_CONCRETE`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_concrete_powder'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('CONCRETE_POWDER'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('CONCRETE_POWDER'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('CONCRETE_POWDER'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_CONCRETE_POWDER`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_glazed_terracotta'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('GLAZED_TERRACOTTA'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('GLAZED_TERRACOTTA'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('GLAZED_TERRACOTTA'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_GLAZED_TERRACOTTA`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_shulker_box'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('SHULKER_BOX'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('SHULKER_BOX'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('SHULKER_BOX'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_SHULKER_BOX`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_stained_glass'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('STAINED_GLASS'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('STAINED_GLASS'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('STAINED_GLASS'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_stained_glass_pane'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('STAINED_GLASS_PANE'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('STAINED_GLASS_PANE'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('STAINED_GLASS_PANE'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_terracotta'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('TERRACOTTA'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('TERRACOTTA'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('TERRACOTTA'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_TERRACOTTA`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_material_wool'] = function(block, generator) {
        const colourIdValue = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
        let rawColourId = 'WHITE'; // Default
        if (colourIdValue && colourIdValue.length > 2) {
            rawColourId = colourIdValue.substring(1, colourIdValue.length - 1);
        }

        // Construct the final Bukkit Material ID string
        let outputBukkitId = '';
        if (rawColourId === 'TINTED_GLASS_BLOCK') {
            outputBukkitId = 'TINTED_GLASS'; // The material is just TINTED_GLASS
        } else if ('WOOL'.includes('GLASS_PANE')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS_PANE`;
        } else if ('WOOL'.includes('GLASS')) {
            outputBukkitId = `${rawColourId}_STAINED_GLASS`;
        } else if ('WOOL'.includes('BANNER')) {
             // Logic for banners might be complex if WALL_BANNER is separate
             outputBukkitId = `${rawColourId}_BANNER`;
        } else {
            outputBukkitId = `${rawColourId}_WOOL`;
        }

        return [`'${outputBukkitId}'`, generator.ORDER_ATOMIC];
    };

    pythonGenerator.forBlock['minecraft_picker_doors'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_fences'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_gates'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_glass'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_ores'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_redstone_components'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_slabs'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_stairs'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_stone_bricks'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_trapdoors'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_walls'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_wood_full'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_wood_logs'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_wood_planks'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_world'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

    pythonGenerator.forBlock['minecraft_picker_miscellaneous'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'MATERIAL_ID');
    };

} // End of installMaterialGenerators
