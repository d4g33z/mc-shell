from rcon import Client
from aiomcrcon import Client as AioClient

from rcon.errorhandler import WrongPassword
from aiomcrcon.errors import IncorrectPasswordError

import re
import json
import asyncio
import pathlib
import urlpath
import pickle
import sys
import uuid
from rich import print
from rich.pretty import pprint

MC_DOC_URL = urlpath.URL("https://minecraft.fandom.com/wiki/Commands")

MC_DATA_DIR = pathlib.Path(__file__).parent.joinpath('data')
MC_DOC_PATH = MC_DATA_DIR.joinpath('command_docs.pkl')
MC_CREDS_PATH = pathlib.Path('~').expanduser().joinpath('.mcshell.pkl')

# SERVER_DATA = {
#     'host': 'azeus.local',
#     'port': '25575',
#     # 'password': 'BnmHhjN',
#     'password': '',
# }


RE_NON_JSON_VALUE = r"(?<!\")\b(?:[0-9]+[a-zA-Z]+|[0-9]+(?:\.[0-9]+)?[a-zA-Z]+|true|false|null)\b(?!\")"
RE_NON_JSON_ARRAY = r"\[[BISL];\s*[^\]]+\]"


# these are used with complete raw output of /data get entity @p to discover NBT quirks
def find_non_json_values(raw_data_str):
    return re.findall(rf"\w+:\s*{RE_NON_JSON_VALUE}",raw_data_str)
def find_non_json_arrays(raw_data_str):
    return re.findall(rf"\w+:\s*{RE_NON_JSON_ARRAY}",raw_data_str)

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
    # 'recipeBook',
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
    'isBlastingFurnaceFilteringCraftable',
    'isSmokerGuiOpen',
    'isFilteringCraftable',
    'toBeDisplayed',
    'isFurnaceGuiOpen',
    'isGuiOpen',
    'isFurnaceFilteringCraftable',
    'isBlastingFurnaceGuiOpen',
    'isSmokerFilteringCraftable'
]

