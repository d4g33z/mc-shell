import collections
from mcshell.constants import *

import re
# # these are used with complete raw output of /data get entity @p to discover NBT quirks
# def find_non_json_values(raw_data_str):
#     return re.findall(rf"\w+:\s*{RE_NON_JSON_VALUE}",raw_data_str)
# def find_non_json_arrays(raw_data_str):
#     return re.findall(rf"\w+:\s*{RE_NON_JSON_ARRAY}",raw_data_str)

def translate_by_n(v, direction, n):
    print(direction)
    _v = v.clone()
    if direction == 'NORTH':
        _v.z -= n
    elif direction == 'SOUTH':
        _v.z += n
    elif direction == 'EAST':
        _v.x += n
    elif direction == 'WEST':
        _v.x -= n
    return _v

def flatten(l):
    for e in l:
        if isinstance(e, collections.Iterable) and not isinstance(e, str):
            for ee in flatten(e): yield ee
        else: yield e

def flatten_parameters_to_string(l):
    return ",".join(map(str, flatten(l)))

def test_async_data_size(player_name,**server_data):
    async def _test_data_size(print_values=False):
        _player = MCPlayer(player_name,**server_data)
        for _data_path in DATA_PATHS:
            try:
                _data = await _player.get_data_async(_data_path)
                # if print_values:
                print('-' * 20)
                print(_data_path)
                print(_data)
            except Exception as e:
                print(e)
                print(f"{_data_path} is too long")
                continue

        for _data_path in RECIPE_BOOK_DATA_PATHS:
            try:
                _data = await _player.get_data_async(f"recipeBook.{_data_path}")
                # if print_values:
                print('-' * 20)
                print(_data_path)
                print(_data)
            except Exception as e:
                print(e)
                print(f"{_data_path} is too long")
                continue

    asyncio.run(_test_data_size())

def test_data_size(player_name,**server_data):
    _player = MCPlayer(player_name,**server_data)
    for _data_path in DATA_PATHS:
        try:
            _data = _player.get_data(_data_path)
            # if print_values:
            print('-' * 20)
            print(_data_path)
            print(_data)
        except Exception as e:
            print(e)
            print(f"{_data_path} is too long")
            continue

    for _data_path in RECIPE_BOOK_DATA_PATHS:
        try:
            _data = _player.get_data(f"recipeBook.{_data_path}")
            # if print_values:
            print('-' * 20)
            print(_data_path)
            print(_data)
        except Exception as e:
            print(e)
            print(f"{_data_path} is too long")
            continue

