from mcshell import MCPlayer
from mcshell.constants import BLOCK_ID_MAP

class MCActionBase:
    def __init__(self,mcplayer:MCPlayer):
        self.mcplayer = mcplayer

        self.block_id_map = BLOCK_ID_MAP
        self.reverse_block_id_map = {v: k for k, v in self.block_id_map.items() if k is not None}
        # Ensure TINTED_GLASS_BLOCK correctly reverses if it was also in the color picker
        if "minecraft:tinted_glass" in self.reverse_block_id_map and self.block_id_map.get("TINTED_GLASS_BLOCK") == "minecraft:tinted_glass":
            self.reverse_block_id_map["minecraft:tinted_glass"] = "TINTED_GLASS_BLOCK"

    def _parse_block_type(self, blockly_id):
        if isinstance(blockly_id, str):
            # Direct lookup from our map (this will now include *_STAINED_GLASS IDs)
            mc_id = self.block_id_map.get(blockly_id)
            if mc_id:
                return mc_id

            # If it already looks like a Minecraft ID
            if ":" in blockly_id:
                return blockly_id

            # Fallback for unmapped simple strings (e.g., 'STONE' directly)
            print(f"Warning: Unmapped Blockly ID string '{blockly_id}'. Attempting 'minecraft:{blockly_id.lower()}'.")
            return f"minecraft:{blockly_id.lower()}"

        # The dictionary handling for {'type': 'GLASS', ...} is no longer needed for glass blocks
        # if minecraft_block_glass always outputs a string ID.
        # You might keep dictionary handling if other blocks generate such structures.
        elif isinstance(blockly_id, dict) and 'type' in blockly_id:
            block_spec_type = blockly_id['type']
            # This section would now be for *other* blocks that might output dictionaries,
            # but NOT for how minecraft_block_glass works anymore.
            print(f"Warning: Received a dictionary structure for block type: {blockly_id}. Handling as generic type.")
            return f"minecraft:{block_spec_type.lower()}" # Generic handling for other dict types

        print(f"Warning: Unexpected block_type_val format: {blockly_id}. Defaulting to minecraft:stone.")
        return "minecraft:stone"

    def get_minecraft_id_from_blockly_id(self, blockly_id_or_struct): # Renamed to match user's intent
        """ Alias for _parse_block_type for clarity in tests """
        return self._parse_block_type(blockly_id_or_struct)

    def get_blockly_id_from_minecraft_id(self, minecraft_id_to_find):
        """
        Takes a Minecraft ID (e.g., "minecraft:oak_planks") and returns the
        corresponding Blockly-generated string ID (e.g., "OAK_PLANKS").
        Returns None if no direct mapping is found.
        """
        # Direct lookup in the pre-computed reverse map
        blockly_id = self.reverse_block_id_map.get(minecraft_id_to_find)
        if blockly_id:
            return blockly_id

        # Fallback for unmapped IDs: if "minecraft:SOMETHING" -> try "SOMETHING"
        if minecraft_id_to_find and minecraft_id_to_find.startswith("minecraft:"):
            potential_blockly_id = minecraft_id_to_find.split(":", 1)[1].upper()
            # Check if this derived ID would correctly map back
            if self.block_id_map.get(potential_blockly_id) == minecraft_id_to_find:
                return potential_blockly_id

        print(f"Warning: Could not find a Blockly ID for Minecraft ID '{minecraft_id_to_find}'.")
        return None

    def translate_by_n(self,v, direction, n):
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

class MCActionsGeometric(MCActionBase):
    def create_column(self,position, width, height, block_type, axis, filled):
        _current_position = position.clone()
        _direction, _face = self.mcplayer.cardinal_direction

        # block_type is Blockly ID like constants.BLOCK_ID_MAP
        if block_type.get('type') == 'GENERIC_MINECRAFT_BLOCK':
            _mc_block_id = self.mcplayer.pc.getBlock(*_current_position)
        else:
            _mc_block_id = self.get_minecraft_id_from_blockly_id(block_type)


        while True:
            _v0 = _current_position.clone()
            for _i in range(height):
                _v0.y += 1
                _v1 = self.translate_by_n(_v0,_direction,width)
                self.mcplayer.pc.setBlocks(*_v0, *_v1, _mc_block_id)



    def create_cube(self,position, block_type,filled,size):
        ...

    def create_pyramid(self,position, block_type, filled, base_size):
        ...
