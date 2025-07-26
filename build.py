import os
from mcshell.mcblockly import build_final_toolbox
from mcshell.constants import MC_DATA_DIR,MC_APP_SRC_DIR


if __name__ == '__main__':
    build_final_toolbox()
    os.system(f"cp {MC_DATA_DIR.joinpath('materials/blocks/materials.mjs')} {MC_APP_SRC_DIR.joinpath('blocks')}")
    os.system(f"cp {MC_DATA_DIR.joinpath('materials/python/materials.mjs')} {MC_APP_SRC_DIR.joinpath('generators/python')}")

    os.system(f"cp {MC_DATA_DIR.joinpath('entities/blocks/entities.mjs')} {MC_APP_SRC_DIR.joinpath('blocks')}")
    os.system(f"cp {MC_DATA_DIR.joinpath('entities/python/entities.mjs')} {MC_APP_SRC_DIR.joinpath('generators/python')}")
