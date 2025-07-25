export function defineMinecraftEntityBlocks(Blockly) {

    Blockly.Blocks['minecraft_picker_entity_hostile_mobs'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Hostile Mobs")
                .appendField(new Blockly.FieldDropdown([
                    ["BLAZE", "BLAZE"],
                    ["CAVE SPIDER", "CAVE_SPIDER"],
                    ["CREEPER", "CREEPER"],
                    ["ELDER GUARDIAN", "ELDER_GUARDIAN"],
                    ["ENDERMAN", "ENDERMAN"],
                    ["ENDERMITE", "ENDERMITE"],
                    ["EVOKER", "EVOKER"],
                    ["GHAST", "GHAST"],
                    ["GUARDIAN", "GUARDIAN"],
                    ["HUSK", "HUSK"],
                    ["ILLUSIONER", "ILLUSIONER"],
                    ["MAGMA CUBE", "MAGMA_CUBE"],
                    ["SHULKER", "SHULKER"],
                    ["SILVERFISH", "SILVERFISH"],
                    ["SKELETON", "SKELETON"],
                    ["SLIME", "SLIME"],
                    ["SPIDER", "SPIDER"],
                    ["STRAY", "STRAY"],
                    ["VEX", "VEX"],
                    ["VINDICATOR", "VINDICATOR"],
                    ["WITCH", "WITCH"],
                    ["WITHER", "WITHER"],
                    ["WITHER SKELETON", "WITHER_SKELETON"],
                    ["ZOMBIE", "ZOMBIE"],
                    ["ZOMBIE VILLAGER", "ZOMBIE_VILLAGER"],
                    ["ZOMBIFIED PIGLIN", "ZOMBIFIED_PIGLIN"]
                ]), "ENTITY_ID"); // Use a consistent field name
            this.setOutput(true, "Entity"); // Output a generic "Entity" type
            this.setColour(260); // A color for entity blocks
            this.setTooltip("Select a Hostile Mobs.");
        }
    };

    Blockly.Blocks['minecraft_picker_entity_minecarts'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Minecarts")
                .appendField(new Blockly.FieldDropdown([
                    ["MINECART", "MINECART"],
                    ["CHEST MINECART", "CHEST_MINECART"],
                    ["COMMAND BLOCK MINECART", "COMMAND_BLOCK_MINECART"],
                    ["FURNACE MINECART", "FURNACE_MINECART"],
                    ["HOPPER MINECART", "HOPPER_MINECART"],
                    ["SPAWNER MINECART", "SPAWNER_MINECART"],
                    ["TNT MINECART", "TNT_MINECART"]
                ]), "ENTITY_ID"); // Use a consistent field name
            this.setOutput(true, "Entity"); // Output a generic "Entity" type
            this.setColour(260); // A color for entity blocks
            this.setTooltip("Select a Minecarts.");
        }
    };

    Blockly.Blocks['minecraft_picker_entity_miscellaneous_entities'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Miscellaneous Entities")
                .appendField(new Blockly.FieldDropdown([
                    ["ENDER DRAGON", "ENDER_DRAGON"],
                    ["EVOKER FANGS", "EVOKER_FANGS"],
                    ["GIANT", "GIANT"],
                    ["IRON GOLEM", "IRON_GOLEM"],
                    ["LLAMA", "LLAMA"],
                    ["SKELETON HORSE", "SKELETON_HORSE"],
                    ["SNOW GOLEM", "SNOW_GOLEM"],
                    ["TNT", "TNT"],
                    ["ZOMBIE HORSE", "ZOMBIE_HORSE"]
                ]), "ENTITY_ID"); // Use a consistent field name
            this.setOutput(true, "Entity"); // Output a generic "Entity" type
            this.setColour(260); // A color for entity blocks
            this.setTooltip("Select a Miscellaneous Entities.");
        }
    };

    Blockly.Blocks['minecraft_picker_entity_passive_mobs'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Passive Mobs")
                .appendField(new Blockly.FieldDropdown([
                    ["BAT", "BAT"],
                    ["CHICKEN", "CHICKEN"],
                    ["COW", "COW"],
                    ["DONKEY", "DONKEY"],
                    ["HORSE", "HORSE"],
                    ["MOOSHROOM", "MOOSHROOM"],
                    ["MULE", "MULE"],
                    ["OCELOT", "OCELOT"],
                    ["PARROT", "PARROT"],
                    ["PIG", "PIG"],
                    ["POLAR BEAR", "POLAR_BEAR"],
                    ["RABBIT", "RABBIT"],
                    ["SHEEP", "SHEEP"],
                    ["SQUID", "SQUID"],
                    ["VILLAGER", "VILLAGER"],
                    ["WOLF", "WOLF"]
                ]), "ENTITY_ID"); // Use a consistent field name
            this.setOutput(true, "Entity"); // Output a generic "Entity" type
            this.setColour(260); // A color for entity blocks
            this.setTooltip("Select a Passive Mobs.");
        }
    };

    Blockly.Blocks['minecraft_picker_entity_projectiles'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Projectiles")
                .appendField(new Blockly.FieldDropdown([
                    ["ARROW", "ARROW"],
                    ["DRAGON FIREBALL", "DRAGON_FIREBALL"],
                    ["EGG", "EGG"],
                    ["ENDER PEARL", "ENDER_PEARL"],
                    ["EXPERIENCE BOTTLE", "EXPERIENCE_BOTTLE"],
                    ["FIREBALL", "FIREBALL"],
                    ["FIREWORK ROCKET", "FIREWORK_ROCKET"],
                    ["LLAMA SPIT", "LLAMA_SPIT"],
                    ["SHULKER BULLET", "SHULKER_BULLET"],
                    ["SMALL FIREBALL", "SMALL_FIREBALL"],
                    ["SNOWBALL", "SNOWBALL"],
                    ["SPECTRAL ARROW", "SPECTRAL_ARROW"],
                    ["SPLASH POTION", "SPLASH_POTION"],
                    ["WITHER SKULL", "WITHER_SKULL"]
                ]), "ENTITY_ID"); // Use a consistent field name
            this.setOutput(true, "Entity"); // Output a generic "Entity" type
            this.setColour(260); // A color for entity blocks
            this.setTooltip("Select a Projectiles.");
        }
    };

    Blockly.Blocks['minecraft_picker_entity_utility_and_special'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Utility And Special")
                .appendField(new Blockly.FieldDropdown([
                    ["AREA EFFECT CLOUD", "AREA_EFFECT_CLOUD"],
                    ["ARMOR STAND", "ARMOR_STAND"],
                    ["END CRYSTAL", "END_CRYSTAL"],
                    ["EXPERIENCE ORB", "EXPERIENCE_ORB"],
                    ["EYE OF ENDER", "EYE_OF_ENDER"],
                    ["FALLING BLOCK", "FALLING_BLOCK"],
                    ["ITEM", "ITEM"],
                    ["ITEM FRAME", "ITEM_FRAME"],
                    ["LEASH KNOT", "LEASH_KNOT"],
                    ["PAINTING", "PAINTING"]
                ]), "ENTITY_ID"); // Use a consistent field name
            this.setOutput(true, "Entity"); // Output a generic "Entity" type
            this.setColour(260); // A color for entity blocks
            this.setTooltip("Select a Utility And Special.");
        }
    };

} // End of defineMinecraftEntityBlocks
