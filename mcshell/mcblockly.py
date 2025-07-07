import xml.etree.ElementTree as ET
import os

from mcshell.constants import *

def make_picker_group(materials,reg_exp):
    _matches = list(filter(lambda x: x is not None, map(lambda x:re.match(reg_exp,x),set(materials))))
    return [_m.group() for _m in _matches]

# Define the patterns and groups for categorization
# This is the primary place to configure how materials are grouped
COLORABLE_BASE_RULES = {
    # Key: The base name for the blockly block (e.g., 'WOOL')
    # Value: A regex pattern to identify variants. The pattern MUST have one
    #        capturing group for the color part of the name.
    'WOOL': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_WOOL$"),
    'TERRACOTTA': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK|LIGHT|LEGACY)_TERRACOTTA$"),
    'STAINED_GLASS': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_STAINED_GLASS$"),
    'STAINED_GLASS_PANE': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_STAINED_GLASS_PANE$"),
    'CONCRETE': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CONCRETE$"),
    'CONCRETE_POWDER': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CONCRETE_POWDER$"),
    'CANDLE': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CANDLE$"),
    'BED': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_BED$"),
    'BANNER': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_(WALL_)?BANNER$"),
    'SHULKER_BOX': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_SHULKER_BOX$"),
    'CARPET': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CARPET$"),
    'GLAZED_TERRACOTTA': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_GLAZED_TERRACOTTA$"),
}

# Define the contents of each picker block you want to generate
MATERIAL_PICKER_GROUPS = {
    "world": ["AIR", "STONE", "GRANITE", "DIORITE", "ANDESITE", "DEEPSLATE", "CALCITE", "TUFF", "DIRT", "COARSE_DIRT", "ROOTED_DIRT", "GRASS_BLOCK", "PODZOL", "MYCELIUM", "DIRT_PATH", "SAND", "RED_SAND", "GRAVEL", "CLAY", "ICE", "PACKED_ICE", "BLUE_ICE", "SNOW", "SNOW_BLOCK", "WATER", "LAVA", "BEDROCK", "OBSIDIAN", "CRYING_OBSIDIAN", "MAGMA_BLOCK"],
    "ores": ["COAL_ORE", "DEEPSLATE_COAL_ORE", "IRON_ORE", "DEEPSLATE_IRON_ORE", "COPPER_ORE", "DEEPSLATE_COPPER_ORE", "GOLD_ORE", "DEEPSLATE_GOLD_ORE", "REDSTONE_ORE", "DEEPSLATE_REDSTONE_ORE", "EMERALD_ORE", "DEEPSLATE_EMERALD_ORE", "LAPIS_ORE", "DEEPSLATE_LAPIS_ORE", "DIAMOND_ORE", "DEEPSLATE_DIAMOND_ORE", "NETHER_GOLD_ORE", "NETHER_QUARTZ_ORE", "ANCIENT_DEBRIS"],
    "wood_planks": ["OAK_PLANKS", "SPRUCE_PLANKS", "BIRCH_PLANKS", "JUNGLE_PLANKS", "ACACIA_PLANKS", "DARK_OAK_PLANKS", "MANGROVE_PLANKS", "CHERRY_PLANKS", "BAMBOO_PLANKS", "CRIMSON_PLANKS", "WARPED_PLANKS", "BAMBOO_MOSAIC"],
    "wood_logs": ["OAK_LOG", "SPRUCE_LOG", "BIRCH_LOG", "JUNGLE_LOG", "ACACIA_LOG", "DARK_OAK_LOG", "MANGROVE_LOG", "CHERRY_LOG", "CRIMSON_STEM", "WARPED_STEM", "STRIPPED_OAK_LOG", "STRIPPED_SPRUCE_LOG", "STRIPPED_BIRCH_LOG", "STRIPPED_JUNGLE_LOG", "STRIPPED_ACACIA_LOG", "STRIPPED_DARK_OAK_LOG", "STRIPPED_MANGROVE_LOG", "STRIPPED_CHERRY_LOG", "STRIPPED_CRIMSON_STEM", "STRIPPED_WARPED_STEM"],
    "wood_full": ["OAK_WOOD", "SPRUCE_WOOD", "BIRCH_WOOD", "JUNGLE_WOOD", "ACACIA_WOOD", "DARK_OAK_WOOD", "MANGROVE_WOOD", "CHERRY_WOOD", "CRIMSON_HYPHAE", "WARPED_HYPHAE", "STRIPPED_OAK_WOOD", "STRIPPED_SPRUCE_WOOD", "STRIPPED_BIRCH_WOOD", "STRIPPED_JUNGLE_WOOD", "STRIPPED_ACACIA_WOOD", "STRIPPED_DARK_OAK_WOOD", "STRIPPED_MANGROVE_WOOD", "STRIPPED_CHERRY_WOOD", "STRIPPED_CRIMSON_HYPHAE", "STRIPPED_WARPED_HYPHAE", "BAMBOO_BLOCK", "STRIPPED_BAMBOO_BLOCK"],
    "stone_bricks": ["BRICKS", "STONE_BRICKS", "MUD_BRICKS", "DEEPSLATE_BRICKS", "DEEPSLATE_TILES", "NETHER_BRICKS", "RED_NETHER_BRICKS", "POLISHED_BLACKSTONE_BRICKS", "END_STONE_BRICKS", "QUARTZ_BRICKS", "CHISELED_STONE_BRICKS", "CRACKED_STONE_BRICKS", "MOSSY_STONE_BRICKS", "CHISELED_NETHER_BRICKS", "CRACKED_NETHER_BRICKS", "CHISELED_POLISHED_BLACKSTONE", "CRACKED_POLISHED_BLACKSTONE_BRICKS", "CHISELED_DEEPSLATE", "CRACKED_DEEPSLATE_BRICKS", "CRACKED_DEEPSLATE_TILES", "CHISELED_TUFF_BRICKS"],
    "glass": ["GLASS", "GLASS_PANE", "TINTED_GLASS"],
    "redstone_components": ["REDSTONE_WIRE", "REDSTONE_BLOCK", "REDSTONE_TORCH", "REPEATER", "COMPARATOR", "PISTON", "STICKY_PISTON", "SLIME_BLOCK", "HONEY_BLOCK", "OBSERVER", "DROPPER", "DISPENSER", "HOPPER", "LECTERN", "LEVER", "DAYLIGHT_DETECTOR", "TRIPWIRE_HOOK", "TARGET", "NOTE_BLOCK", "RAIL", "POWERED_RAIL", "DETECTOR_RAIL", "ACTIVATOR_RAIL", "REDSTONE_LAMP"],
    # Add more groups as needed (stairs, slabs, fences, doors, etc.)
}

def process_materials():
    """
    Reads the full material list and categorizes materials into
    colorable bases, specific picker groups, and single/misc items.
    """
    try:
        _raw_materials_list = pickle.load(MC_MATERIALS_PATH.open('rb'))
    except FileNotFoundError:
        from mcshell.mcscraper import make_materials
        _raw_materials_list = make_materials()

    all_materials = set()
    for mat in _raw_materials_list:
        if mat and not mat.startswith("LEGACY_"):  # Ignore legacy materials
            all_materials.add(mat)

    MATERIAL_PICKER_GROUPS['stairs'] = make_picker_group(all_materials, r".*_STAIRS$")
    MATERIAL_PICKER_GROUPS['slabs'] = make_picker_group(all_materials, r".*_SLAB$")
    MATERIAL_PICKER_GROUPS['fences'] = make_picker_group(all_materials, r".*_FENCE$")
    MATERIAL_PICKER_GROUPS['gates'] = make_picker_group(all_materials, r".*_GATE$")
    MATERIAL_PICKER_GROUPS['doors'] = make_picker_group(all_materials, r".*_DOOR$")
    MATERIAL_PICKER_GROUPS['trapdoors'] = make_picker_group(all_materials, r".*_TRAPDOOR$")
    MATERIAL_PICKER_GROUPS['walls'] = make_picker_group(all_materials, r".*_WALL$")

    colorable_bases = {}  # e.g., {'WOOL': ['WHITE_WOOL', 'BLUE_WOOL', ...]}
    picker_data = {}      # e.g., {'ores': ['COAL_ORE', 'IRON_ORE', ...]}
    processed_materials = set()

    # 1. Identify and categorize colorable materials
    for base_name, pattern in COLORABLE_BASE_RULES.items():
        colorable_bases[base_name] = []
        for mat in list(all_materials):
            if pattern.match(mat):
                colorable_bases[base_name].append(mat)
                processed_materials.add(mat)

    # 2. Identify materials for specific picker groups
    for group_name, material_list in MATERIAL_PICKER_GROUPS.items():
        picker_data[group_name] = []
        for mat_id in material_list:
            if mat_id in all_materials:
                picker_data[group_name].append(mat_id)
                processed_materials.add(mat_id)

    # 3. All remaining materials are singles/miscellaneous
    singles_data = sorted(list(all_materials - processed_materials))


    try:
        # colorable, pickers, singles = process_materials()

        with MC_COLOURABLE_MATERIALS_DATA_PATH.open('w') as f:
            json.dump(colorable_bases, f, indent=4, sort_keys=True)
        # print("Successfully generated colourables.json")

        with MC_PICKER_MATERIALS_DATA_PATH.open('w') as f:
            json.dump(picker_data, f, indent=4,sort_keys=True)
        # print("Successfully generated pickers.json")

        with MC_SINGLE_MATERIALS_DATA_PATH.open('w') as f:
            json.dump(singles_data, f, indent=4, sort_keys=True)
        # print("Successfully generated singles.json")
    except Exception as e:
        print(f"An error occurred: {e}")
    # finally:
    #     return colorable_bases, picker_data, singles_data


# Define the groups for entity picker blocks. The key will be the picker name
# (e.g., 'hostile_mobs') and the value is a list of entity IDs to include.
# You can customize these groups as you see fit.
ENTITY_PICKER_GROUPS = {
    "boats": [
        "ACACIA_BOAT", "BAMBOO_RAFT", "BIRCH_BOAT", "CHERRY_BOAT", "DARK_OAK_BOAT",
        "JUNGLE_BOAT", "MANGROVE_BOAT", "OAK_BOAT", "SPRUCE_BOAT", "PALE_OAK_BOAT"
    ],
    "chest_boats": [
        "ACACIA_CHEST_BOAT", "BAMBOO_CHEST_RAFT", "BIRCH_CHEST_BOAT", "CHERRY_CHEST_BOAT",
        "DARK_OAK_CHEST_BOAT", "JUNGLE_CHEST_BOAT", "MANGROVE_CHEST_BOAT", "OAK_CHEST_BOAT",
        "SPRUCE_CHEST_BOAT", "PALE_OAK_CHEST_BOAT"
    ],
    "minecarts": [
        "MINECART", "CHEST_MINECART", "COMMAND_BLOCK_MINECART", "FURNACE_MINECART",
        "HOPPER_MINECART", "SPAWNER_MINECART", "TNT_MINECART"
    ],
    "passive_mobs": [
        "ALLAY", "ARMADILLO", "AXOLOTL", "BAT", "CAMEL", "CAT", "CHICKEN", "COD", "COW",
        "DONKEY", "FOX", "FROG", "GLOW_SQUID", "HORSE", "MOOSHROOM", "MULE", "OCELOT",
        "PANDA", "PARROT", "PIG", "POLAR_BEAR", "PUFFERFISH", "RABBIT", "SALMON",
        "SHEEP", "SNIFFER", "SQUID", "STRIDER", "TADPOLE", "TROPICAL_FISH", "TURTLE",
        "VILLAGER", "WANDERING_TRADER", "WOLF"
    ],
    "hostile_mobs": [
        "BLAZE", "BOGGED", "BREEZE", "CAVE_SPIDER", "CREAKING", "CREEPER", "DROWNED",
        "ELDER_GUARDIAN", "ENDERMAN", "ENDERMITE", "EVOKER", "GHAST", "GUARDIAN",
        "HOGLIN", "HUSK", "ILLUSIONER", "MAGMA_CUBE", "PHANTOM", "PIGLIN",
        "PIGLIN_BRUTE", "PILLAGER", "RAVAGER", "SHULKER", "SILVERFISH", "SKELETON",
        "SLIME", "SPIDER", "STRAY", "VEX", "VINDICATOR", "WARDEN", "WITCH", "WITHER",
        "WITHER_SKELETON", "ZOGLIN", "ZOMBIE", "ZOMBIE_VILLAGER", "ZOMBIFIED_PIGLIN"
    ],
    "projectiles": [
        "ARROW", "BREEZE_WIND_CHARGE", "DRAGON_FIREBALL", "EGG", "ENDER_PEARL",
        "EXPERIENCE_BOTTLE", "FIREBALL", "FIREWORK_ROCKET", "FISHING_BOBBER",
        "LLAMA_SPIT", "SHULKER_BULLET", "SMALL_FIREBALL", "SNOWBALL",
        "SPECTRAL_ARROW", "SPLASH_POTION", "LINGERING_POTION", "TRIDENT", "WIND_CHARGE", "WITHER_SKULL"
    ],
    "utility_and_special": [
        "AREA_EFFECT_CLOUD", "ARMOR_STAND", "BLOCK_DISPLAY", "END_CRYSTAL",
        "EXPERIENCE_ORB", "EYE_OF_ENDER", "FALLING_BLOCK", "GLOW_ITEM_FRAME",
        "INTERACTION", "ITEM", "ITEM_DISPLAY", "ITEM_FRAME", "LEASH_KNOT",
        "LIGHTNING_BOLT", "MARKER", "OMINOUS_ITEM_SPAWNER", "PAINTING", "PLAYER",
        "TEXT_DISPLAY"
    ]
    # Note: Spawn eggs are typically items, not placeable entities, so they are omitted here.
    # You could create a separate "spawn_eggs" picker if needed.
}

def process_entities(filepath="entity-list.txt"):
    """
    Reads the full entity list and categorizes them into picker groups.
    """

    try:
        _raw_entity_id_map = pickle.load(MC_ENTITY_ID_MAP_PATH.open('rb'))
    except FileNotFoundError:
        from mcshell.mcscraper import make_entity_id_map
        _raw_entity_id_map = make_entity_id_map()

    all_entities = set()
    for _ent,_id in _raw_entity_id_map.items():
        if not _ent.startswith("LEGACY_"):  # Ignore legacy materials
            all_entities.add(_ent)

    picker_data = {}
    processed_entities = set()

    # Populate picker groups from the defined lists
    for group_name, entity_list in ENTITY_PICKER_GROUPS.items():
        picker_data[group_name] = []
        for entity_id in entity_list:
            if entity_id in all_entities:
                picker_data[group_name].append(entity_id)
                processed_entities.add(entity_id)
            else:
                print(f"Warning: Entity ID '{entity_id}' listed in group '{group_name}' not found in master list.")
        if not picker_data[group_name]:
            picker_data.pop(group_name)

    # All remaining entities go into a miscellaneous group
    misc_entities = sorted(list(all_entities - processed_entities))
    if misc_entities:
        picker_data["miscellaneous_entities"] = misc_entities

    try:
        with MC_ENTITY_PICKERS_PATH.open('w') as f:
            json.dump(picker_data, f, indent=4, sort_keys=True)
        # print("Successfully generated pickers.json")
    except Exception as e:
        print(f"An error occurred: {e}")


def build_final_toolbox(final_toolbox_path):
    """
    Loads a toolbox template, injects generated XML category fragments,
    and writes the final toolbox.xml file.
    """

    # Define paths to the input and output files
    template_path = MC_DATA_DIR.joinpath('toolbox_template.xml')
    materials_toolbox_path = MC_DATA_DIR.joinpath('materials/toolbox.xml')
    entities_toolbox_path = MC_DATA_DIR.joinpath('entities/toolbox.xml')

    print("--- Starting Toolbox Build ---")

    # --- Step 1: Parse the main template and fragment files ---
    try:
        # Registering the namespace prevents the parser from adding "ns0:" prefixes
        ET.register_namespace('', "https://developers.google.com/blockly/xml")

        # Parse the main template
        tree = ET.parse(template_path)
        root = tree.getroot()

        # Parse the material and entity category fragments
        materials_category = ET.parse(materials_toolbox_path).getroot()
        entities_category = ET.parse(entities_toolbox_path).getroot()

    except FileNotFoundError as e:
        print(f"Error: Could not find a required XML file. Make sure it exists: {e.filename}")
        return
    except ET.ParseError as e:
        print(f"Error: Could not parse an XML file. Check for syntax errors. Details: {e}")
        return

    # --- Step 2: Find the placeholder comments and replace them ---

    # We need to iterate through a copy of the list because we are modifying it
    for i, child in enumerate(list(root)):
        # ElementTree parses comments as a function-like object.
        # We check if the tag is a function and its text is our placeholder.
        if child.attrib.get('name',None) == 'Materials':
            print("Found materials placeholder. Injecting category...")
            # Insert the new category at the placeholder's position
            root.insert(i, materials_category)
            # Remove the old placeholder comment
            root.remove(child)

        elif child.attrib.get('name',None) == 'Entities':
            print("Found entities placeholder. Injecting category...")
            root.insert(i, entities_category)
            root.remove(child)

    # --- Step 3: Write the new, complete toolbox.xml file ---
    try:
        # ET.indent() is available in Python 3.9+ and makes the output pretty
        if hasattr(ET, 'indent'):
            ET.indent(tree, space="  ")

        tree.write(final_toolbox_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully built final toolbox at: {final_toolbox_path}")

    except Exception as e:
        print(f"Error writing final toolbox file: {e}")


def update_app():
    process_materials()
    _out = os.system(f"node {MC_DATA_DIR.joinpath('materials/generate_material_blocks.mjs')}")

    process_entities()
    os.system(f"node {MC_DATA_DIR.joinpath('entities/generate_entity_blocks.mjs')}")
    build_final_toolbox(MC_APP_SRC_DIR.joinpath('toolbox.xml'))


    os.system(f"cp {MC_DATA_DIR.joinpath('materials/blocks/materials.mjs')} {MC_APP_SRC_DIR.joinpath('blocks')}")
    os.system(f"cp {MC_DATA_DIR.joinpath('materials/python/materials.mjs')} {MC_APP_SRC_DIR.joinpath('generators/python')}")

    os.system(f"cp {MC_DATA_DIR.joinpath('entities/blocks/entities.mjs')} {MC_APP_SRC_DIR.joinpath('blocks')}")
    os.system(f"cp {MC_DATA_DIR.joinpath('entities/python/entities.mjs')} {MC_APP_SRC_DIR.joinpath('generators/python')}")

def build_app():
    os.system(f"cd {MC_APP_SRC_DIR}; npm run build")

if __name__ == '__main__':
    update_app()


