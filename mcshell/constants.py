from rcon import Client
from aiomcrcon import Client as AioClient

from rcon.errorhandler import WrongPassword
from aiomcrcon.errors import IncorrectPasswordError

import os
import re
import json
import copy
import math
import random
import asyncio
import requests
import shutil
import pathlib
import urlpath
import zipfile
import io
import pickle
import time
import sys
import uuid
from typing import List,Optional,Dict,Any

import numpy as np

from rich import print
from rich.pretty import pprint

from mcshell.Matrix3 import Matrix3
from mcshell.Vec3 import Vec3


class PowerCancelledException(Exception):
    pass

try:
    from icecream import ic
    ic.configureOutput(includeContext=True)
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

FJ_SERVER_PORT = 4711

MC_SERVER_PORT = 25575
MC_SERVER_HOST = 'localhost'
MC_SERVER_TYPE = 'paper'

MC_CREDS_PATH = pathlib.Path('~').expanduser().joinpath('.mcshell.pkl')

MC_DATA_DIR = pathlib.Path(__file__).parent.joinpath('data')

FJ_JAR_PATH = MC_DATA_DIR.joinpath('FruitJuice-0.3.0.jar')

MC_DOC_URL = urlpath.URL("https://minecraft.fandom.com/wiki/Commands")
MC_DOC_DIR = MC_DATA_DIR.joinpath('doc')
MC_DOC_PATH = MC_DOC_DIR.joinpath('command_docs.pkl')

MC_MATERIAL_URL = urlpath.URL('https://hub.spigotmc.org/javadocs/spigot/org/bukkit/Material.html')
MC_MATERIALS_PATH = MC_DATA_DIR.joinpath('materials/materials.pkl')
MC_COLOURABLE_MATERIALS_DATA_PATH = MC_DATA_DIR.joinpath('materials/colourables.json')
MC_PICKER_MATERIALS_DATA_PATH = MC_DATA_DIR.joinpath('materials/pickers.json')
MC_SINGLE_MATERIALS_DATA_PATH = MC_DATA_DIR.joinpath('materials/singles.json')

# here is the source of truth for Entity IDs like in pyncraft.entity
MC_ENTITY_TYPE_URL = urlpath.URL("https://raw.githubusercontent.com/PaperMC/Paper/refs/heads/main/paper-api/src/main/java/org/bukkit/entity/EntityType.java")
MC_ENTITY_ID_MAP_PATH = MC_DATA_DIR.joinpath('entities/entity_id_map.pkl')
MC_ENTITY_PICKERS_PATH = MC_DATA_DIR.joinpath('entities/pickers.json')

MC_APP_DIR = MC_DATA_DIR.joinpath('app')

MC_APP_STATIC_DIR = MC_DATA_DIR.joinpath('static')
MC_APP_SRC_DIR = pathlib.Path(__file__).parent.parent.joinpath('mced/src')

MC_POWER_LIBRARY_DIR = MC_DATA_DIR.joinpath('powers')
MC_CONTROL_LAYOUT_PATH = MC_DATA_DIR.joinpath('control_layout.json')

PP_JAR_DIR = os.path.expanduser("~/mc-worlds/server-jars/")


#No, we scrape the actual paper sources to get EntityTypes
# this is a pure html source of entity  names without IDS
#MC_ENTITY_URL = urlpath.URL('https://hub.spigotmc.org/javadocs/spigot/org/bukkit/entity/EntityType.html')
#MC_ENTITIES_PATH = MC_DATA_DIR.joinpath('entities/entities.pkl')

SERVER_DATA = {
    'host': MC_SERVER_HOST,
    'port': MC_SERVER_PORT,
    'server_type': MC_SERVER_TYPE
}

RE_NON_JSON_VALUE = r"(?<!\")\b(?:[0-9]+[a-zA-Z]+|[0-9]+(?:\.[0-9]+)?[a-zA-Z]+|true|false|null)\b(?!\")"
RE_NON_JSON_ARRAY = r"\[[BISL];\s*[^\]]+\]"

DATA_TYPES ={
    'SleepTimer': 's',
    'Base': 'd',
    'Invulnerable': 'b',
    'FallFlying': 'b',
    'AbsorptionAmount': 'f',
    'invulnerable': 'b',
    'mayfly': 'b',
    'instabuild': 'b',
    'walkSpeed': 'f',
    'mayBuild': 'b',
    'flying': 'b',
    'flySpeed': 'f',
    'FallDistance': 'f',
    'isBlastingFurnaceFilteringCraftable': 'b',
    'isSmokerGuiOpen': 'b',
    'isFilteringCraftable': 'b',
    'isFurnaceGuiOpen': 'b',
    'isGuiOpen': 'b',
    'isFurnaceFilteringCraftable': 'b',
    'isBlastingFurnaceGuiOpen': 'b',
    'isSmokerFilteringCraftable': 'b',
    'DeathTime': 's',
    'seenCredits': 'b',
    'Health': 'f',
    'foodSaturationLevel': 'f',
    'Air': 's',
    'OnGround': 'b',
    'XpP': 'f',
    'foodExhaustionLevel': 'f',
    'HurtTime': 's',
    'Slot': 'b',
    'Count': 'b',
    'Charged': 'b',
}

ARRAY_DATA_TYPES = {
    'UUID': 'I',
}

# TODO: these cause response truncation from rcon server
FORBIDDEN_DATA_PATHS = [
    'recipeBook',
    'recipes',
    'toBeDisplayed',
]

DATA_PATHS = [
    'Brain',
    'HurtByTimestamp',
    'SleepTimer',
    'Attributes',
    'Invulnerable',
    'FallFlying',
    'PortalCooldown',
    'AbsorptionAmount',
    'abilities',
    'FallDistance',
    'recipeBook',
    'DeathTime',
    'XpSeed',
    'XpTotal',
    'UUID',
    'playerGameType',
    'seenCredits',
    'Motion',
    'Health',
    'foodSaturationLevel',
    'Air',
    'OnGround',
    'Dimension',
    'Rotation',
    'XpLevel',
    'Score',
    'Pos',
    'previousPlayerGameType',
    'Fire',
    'XpP',
    'EnderItems',
    'DataVersion',
    'foodLevel',
    'foodExhaustionLevel',
    'HurtTime',
    'SelectedItemSlot',
    'Inventory',
    'foodTickTimer'
]

RECIPE_BOOK_DATA_PATHS = [
    'recipes',
    'toBeDisplayed',
    'isBlastingFurnaceFilteringCraftable',
    'isSmokerGuiOpen',
    'isFilteringCraftable',
    'isFurnaceGuiOpen',
    'isGuiOpen',
    'isFurnaceFilteringCraftable',
    'isBlastingFurnaceGuiOpen',
    'isSmokerFilteringCraftable'
]

# TODO: this is deprecated; use Bukkit Material IDs now
BLOCK_ID_MAP = {
            # World Blocks
            "DIRT": "minecraft:dirt",
            "GRASS": "minecraft:grass_block",
            "SAND": "minecraft:sand",
            "GRAVEL": "minecraft:gravel",
            "STONE": "minecraft:stone",
            "COBBLESTONE": "minecraft:cobblestone",
            "SANDSTONE": "minecraft:sandstone",
            "BEDROCK": "minecraft:bedrock",
            # "WOOD_PLANKS" from minecraft_block_world was generic, handled by specific planks now

            # Material Blocks
            "WOOD": "minecraft:oak_log", # Default to oak, or require more specific blocks
            "LOG": "minecraft:oak_log",   # Default to oak
            "LEAVES": "minecraft:oak_leaves", # Default to oak
            "SPONGE": "minecraft:sponge",
            "TNT": "minecraft:tnt",
            "BOOKSHELF": "minecraft:bookshelf",
            "MOSSY_COBBLESTONE": "minecraft:mossy_cobblestone",
            "OBSIDIAN": "minecraft:obsidian",

            # Ore Blocks (from minecraft_block_block and minecraft_block_ore)
            "COAL_ORE": "minecraft:coal_ore",
            "DEEPSLATE_COAL_ORE": "minecraft:deepslate_coal_ore",
            "IRON_ORE": "minecraft:iron_ore",
            "DEEPSLATE_IRON_ORE": "minecraft:deepslate_iron_ore",
            "COPPER_ORE": "minecraft:copper_ore",
            "DEEPSLATE_COPPER_ORE": "minecraft:deepslate_copper_ore",
            "GOLD_ORE": "minecraft:gold_ore", # Ore block itself
            "DEEPSLATE_GOLD_ORE": "minecraft:deepslate_gold_ore",
            "REDSTONE_ORE": "minecraft:redstone_ore",
            "DEEPSLATE_REDSTONE_ORE": "minecraft:deepslate_redstone_ore",
            "EMERALD_ORE": "minecraft:emerald_ore",
            "DEEPSLATE_EMERALD_ORE": "minecraft:deepslate_emerald_ore",
            "LAPIS_ORE": "minecraft:lapis_ore",
            "DEEPSLATE_LAPIS_ORE": "minecraft:deepslate_lapis_ore",
            "DIAMOND_ORE": "minecraft:diamond_ore",
            "DEEPSLATE_DIAMOND_ORE": "minecraft:deepslate_diamond_ore",
            "NETHER_GOLD_ORE": "minecraft:nether_gold_ore",
            "NETHER_QUARTZ_ORE": "minecraft:nether_quartz_ore",

            # Metal/Gem Blocks (from minecraft_block_block)
            "GOLD": "minecraft:gold_block", # The full block, not ore
            "IRON": "minecraft:iron_block",
            "COAL": "minecraft:coal_block",
            "DIAMOND": "minecraft:diamond_block",
            "EMERALD": "minecraft:emerald_block",
            "LAPIS_LAZULI": "minecraft:lapis_block", # Lapis Lazuli Block

            # Lamp Blocks
            "GLOWSTONE": "minecraft:glowstone",
            "SEA_LANTERN": "minecraft:sea_lantern",
            "REDSTONE_LAMP": "minecraft:redstone_lamp",

            # Stairs
            "COBBLESTONE_STAIRS": "minecraft:cobblestone_stairs",
            "BRICK_STAIRS": "minecraft:brick_stairs",
            "STONE_BRICK_STAIRS": "minecraft:stone_brick_stairs",
            "NETHER_BRICK_STAIRS": "minecraft:nether_brick_stairs",
            "SANDSTONE_STAIRS": "minecraft:sandstone_stairs",
            "QUARTZ_STAIRS": "minecraft:quartz_stairs",
            "WOOD_STAIRS": "minecraft:oak_stairs", # Default to oak
            "ACACIA_STAIRS": "minecraft:acacia_stairs",

            # Slabs
            "COBBLESTONE_SLAB": "minecraft:cobblestone_slab",
            "BRICK_SLAB": "minecraft:brick_slab",
            "STONE_BRICK_SLAB": "minecraft:stone_brick_slab",
            "NETHER_BRICK_SLAB": "minecraft:nether_brick_slab",
            "SANDSTONE_SLAB": "minecraft:sandstone_slab",
            "QUARTZ_SLAB": "minecraft:quartz_slab",
            "WOOD_SLAB": "minecraft:oak_slab", # Default to oak

            # Fences
            "OAK_FENCE": "minecraft:oak_fence",
            "SPRUCE_FENCE": "minecraft:spruce_fence",
            "BIRCH_FENCE": "minecraft:birch_fence",
            "JUNGLE_FENCE": "minecraft:jungle_fence",
            "ACACIA_FENCE": "minecraft:acacia_fence",
            "DARK_OAK_FENCE": "minecraft:dark_oak_fence",
            "MANGROVE_FENCE": "minecraft:mangrove_fence",
            "CHERRY_FENCE": "minecraft:cherry_fence",
            "BAMBOO_FENCE": "minecraft:bamboo_fence",
            "CRIMSON_FENCE": "minecraft:crimson_fence",
            "WARPED_FENCE": "minecraft:warped_fence",
            "NETHER_BRICK_FENCE": "minecraft:nether_brick_fence",

            # Fence Gates (if you have a separate block/IDs for them)
            "OAK_FENCE_GATE": "minecraft:oak_fence_gate",
            "SPRUCE_FENCE_GATE": "minecraft:spruce_fence_gate",
            # ... add all other fence gate types ...
            "MANGROVE_FENCE_GATE": "minecraft:mangrove_fence_gate",
            "CHERRY_FENCE_GATE": "minecraft:cherry_fence_gate",
            "BAMBOO_FENCE_GATE": "minecraft:bamboo_fence_gate",
            "CRIMSON_FENCE_GATE": "minecraft:crimson_fence_gate",
            "WARPED_FENCE_GATE": "minecraft:warped_fence_gate",

            # Doors
            "OAK_DOOR": "minecraft:oak_door",
            "SPRUCE_DOOR": "minecraft:spruce_door",
            "BIRCH_DOOR": "minecraft:birch_door",
            "JUNGLE_DOOR": "minecraft:jungle_door",
            "ACACIA_DOOR": "minecraft:acacia_door",
            "DARK_OAK_DOOR": "minecraft:dark_oak_door",
            "MANGROVE_DOOR": "minecraft:mangrove_door",
            "CHERRY_DOOR": "minecraft:cherry_door",
            "BAMBOO_DOOR": "minecraft:bamboo_door",
            "CRIMSON_DOOR": "minecraft:crimson_door",
            "WARPED_DOOR": "minecraft:warped_door",
            "IRON_DOOR": "minecraft:iron_door",

            # Trapdoors
            "OAK_TRAPDOOR": "minecraft:oak_trapdoor",
            "SPRUCE_TRAPDOOR": "minecraft:spruce_trapdoor",
            "BIRCH_TRAPDOOR": "minecraft:birch_trapdoor",
            "JUNGLE_TRAPDOOR": "minecraft:jungle_trapdoor",
            "ACACIA_TRAPDOOR": "minecraft:acacia_trapdoor",
            "DARK_OAK_TRAPDOOR": "minecraft:dark_oak_trapdoor",
            "MANGROVE_TRAPDOOR": "minecraft:mangrove_trapdoor",
            "CHERRY_TRAPDOOR": "minecraft:cherry_trapdoor",
            "BAMBOO_TRAPDOOR": "minecraft:bamboo_trapdoor",
            "CRIMSON_TRAPDOOR": "minecraft:crimson_trapdoor",
            "WARPED_TRAPDOOR": "minecraft:warped_trapdoor",
            "IRON_TRAPDOOR": "minecraft:iron_trapdoor",

            # Liquids
            "WATER": "minecraft:water",
            "LAVA": "minecraft:lava",

            # Falling Blocks (from minecraft_block_falling)
            # "SAND" and "GRAVEL" are already in World Blocks, ensure consistency or handle here if different context

            # Redstone Components
            "REDSTONE": "minecraft:redstone_wire", # or minecraft:redstone_block? Clarify intent.
            "REDSTONE_TORCH": "minecraft:redstone_torch",
            "STONE_BUTTON": "minecraft:stone_button",
            "LEVER": "minecraft:lever",
            "PRESSURE_PLATE": "minecraft:stone_pressure_plate", # Default to stone
            # Add other button/pressure plate types if they have distinct IDs from Blockly
            "ACACIA_BUTTON": "minecraft:acacia_button",
            "BIRCH_BUTTON": "minecraft:birch_button",
            "CRIMSON_BUTTON": "minecraft:crimson_button",
            "DARK_OAK_BUTTON": "minecraft:dark_oak_button",
            "JUNGLE_BUTTON": "minecraft:jungle_button",
            "MANGROVE_BUTTON": "minecraft:mangrove_button",
            "OAK_BUTTON": "minecraft:oak_button",
            "POLISHED_BLACKSTONE_BUTTON": "minecraft:polished_blackstone_button",
            "SPRUCE_BUTTON": "minecraft:spruce_button",
            "WARPED_BUTTON": "minecraft:warped_button",
            "CHERRY_BUTTON": "minecraft:cherry_button",
            "BAMBOO_BUTTON": "minecraft:bamboo_button",


            # Rails
            "RAIL": "minecraft:rail",
            "POWERED_RAIL": "minecraft:powered_rail",
            "DETECTOR_RAIL": "minecraft:detector_rail",
            "ACTIVATOR_RAIL": "minecraft:activator_rail",

            # Planks
            "ACACIA_PLANKS": "minecraft:acacia_planks",
            "BIRCH_PLANKS": "minecraft:birch_planks",
            "CRIMSON_PLANKS": "minecraft:crimson_planks",
            "DARK_OAK_PLANKS": "minecraft:dark_oak_planks",
            "JUNGLE_PLANKS": "minecraft:jungle_planks",
            "MANGROVE_PLANKS": "minecraft:mangrove_planks",
            "OAK_PLANKS": "minecraft:oak_planks",
            "SPRUCE_PLANKS": "minecraft:spruce_planks",
            "WARPED_PLANKS": "minecraft:warped_planks",
            "CHERRY_PLANKS": "minecraft:cherry_planks",
            "BAMBOO_PLANKS": "minecraft:bamboo_planks",

            # From FieldMinecraftColour (minecraft_coloured_block_picker)
            "WHITE_WOOL": "minecraft:white_wool", # Example: Defaulting colored blocks to wool
            "ORANGE_WOOL": "minecraft:orange_wool",
            "MAGENTA_WOOL": "minecraft:magenta_wool",
            "LIGHT_BLUE_WOOL": "minecraft:light_blue_wool",
            "YELLOW_WOOL": "minecraft:yellow_wool",
            "LIME_WOOL": "minecraft:lime_wool",
            "PINK_WOOL": "minecraft:pink_wool",
            "GRAY_WOOL": "minecraft:gray_wool",
            "LIGHT_GRAY_WOOL": "minecraft:light_gray_wool",
            "CYAN_WOOL": "minecraft:cyan_wool",
            "AZURE_WOOL": "minecraft:light_blue_wool", # Azure might map to light blue wool or a specific flower-based block
            "PURPLE_WOOL": "minecraft:purple_wool",
            "BLUE_WOOL": "minecraft:blue_wool",
            "BROWN_WOOL": "minecraft:brown_wool",
            "GREEN_WOOL": "minecraft:green_wool",
            "RED_WOOL": "minecraft:red_wool",
            "BLACK_WOOL": "minecraft:black_wool",

            "WHITE_STAINED_GLASS": "minecraft:white_stained_glass",
            "ORANGE_STAINED_GLASS": "minecraft:orange_stained_glass",
            "MAGENTA_STAINED_GLASS": "minecraft:magenta_stained_glass",
            "LIGHT_BLUE_STAINED_GLASS": "minecraft:light_blue_stained_glass",
            "YELLOW_STAINED_GLASS": "minecraft:yellow_stained_glass",
            "LIME_STAINED_GLASS": "minecraft:lime_stained_glass",
            "PINK_STAINED_GLASS": "minecraft:pink_stained_glass",
            "GRAY_STAINED_GLASS": "minecraft:gray_stained_glass",
            "LIGHT_GRAY_STAINED_GLASS": "minecraft:light_gray_stained_glass",
            "CYAN_STAINED_GLASS": "minecraft:cyan_stained_glass",
            "AZURE_STAINED_GLASS": "minecraft:light_blue_stained_glass", # Or specific azure stained glass if it exists
            "PURPLE_STAINED_GLASS": "minecraft:purple_stained_glass",
            "BLUE_STAINED_GLASS": "minecraft:blue_stained_glass",
            "BROWN_STAINED_GLASS": "minecraft:brown_stained_glass",
            "GREEN_STAINED_GLASS": "minecraft:green_stained_glass",
            "RED_STAINED_GLASS": "minecraft:red_stained_glass",
            "BLACK_STAINED_GLASS": "minecraft:black_stained_glass",

            # TINTED_GLASS_BLOCK is already in your map from minecraft_coloured_block_picker:
            "TINTED_GLASS_BLOCK": "minecraft:tinted_glass",

            # Plain glass if needed as a fallback or separate block
            "GLASS": "minecraft:glass",
            # Generic Block (from the simplified 'minecraft_block')
    
            # this is interpreted as whatever block the action gets
            # from the player's environment via a getBlock() call
            "GENERIC_MINECRAFT_BLOCK": None # Default for the generic block
        }

