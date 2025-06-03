from mcshell import MCPlayer
from mcshell.constants import BLOCK_ID_MAP,Vec3

from mcshell.mcvoxel import (generate_digital_tetrahedron_voxels,
                             generate_digital_tube_voxels,
                             generate_digital_plane_voxels,
                             generate_digital_ball_coordinates,
                             generate_digital_cube_coordinates,
                             generate_digital_sphere_coordinates)

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

# This would be part of the student's environment or a library you provide.
# It uses your low-level geometry functions.

# --- Import your low-level geometry functions ---
# Assume your geometry functions are in a file named `digital_geometry.py`
# from .digital_geometry import ( # Use relative import if in the same package
#     generate_digital_ball_coordinates,
#     generate_digital_tube_voxels,
#     generate_digital_plane_voxels,
#     generate_digital_cube_coordinates,
#     generate_digital_tetrahedron_voxels
# )
# For this example, I'll assume they are globally available or defined above.

# Assume MCActionBase is defined as we discussed previously,
# with _parse_block_type, _initialize_block_id_maps, etc.
# class MCActionBase: ... (from previous responses)

class MCActions(MCActionBase): # Inherits from MCActionBase
    def __init__(self, mc_player_instance):
        super().__init__(mc_player_instance) # Call parent constructor
        self.default_material_id = 1 # Example: material ID for stone in voxelmap
                                     # Or map block_type to material_id

    def _place_blocks_from_coords(self, coords_list, block_type_from_blockly,
                                  placement_offset_vec3=None):
        """
        Helper method to take a list of coordinates and a Blockly block type,
        parse the block type, and set the blocks.
        """
        if not coords_list:
            print("No coordinates generated, nothing to place.")
            return

        # TODO Block IDs are deeply confused
        # minecraft_block_id = self._parse_block_type(block_type_from_blockly)
        minecraft_block_id = block_type_from_blockly

        _cardinal_direction, _face = self.mcplayer.cardinal_direction
        print(f"Attempting to place {len(coords_list)} blocks of type '{minecraft_block_id}' facing {_cardinal_direction} looking at a {_face}")

        offset_x, offset_y, offset_z = (0,0,0)
        if placement_offset_vec3: # If a Vec3 object is given for overall placement
            offset_x, offset_y, offset_z = int(placement_offset_vec3.x), int(placement_offset_vec3.y), int(placement_offset_vec3.z)

        for x, y, z in coords_list:
            # The coordinates from generate_digital_* are often relative to their shape's center.
            # The 'position' input to the Blockly block (which becomes center for many shapes)
            # should define the world offset.
            # Here, we assume coords_list are already in world space if 'center' was used
            # correctly in the generate_digital_* calls.
            # If generate_digital_* functions return coords relative to (0,0,0),
            # then the 'center' or 'position' from Blockly needs to be added here.
            # Let's assume the generate_digital_* functions ALREADY incorporate their 'center' argument.
            final_x = x + offset_x
            final_y = y + offset_y
            final_z = z + offset_z
            # print(f"Setting block: ({final_x}, {final_y}, {final_z}) to {minecraft_block_id}")
            self.mcplayer.pc.setBlock(int(final_x), int(final_y), int(final_z), minecraft_block_id,_face,_cardinal_direction)
            # block ids are screwed up
            # self.mcplayer.pc.setBlock(int(final_x), int(final_y), int(final_z), block_type_from_blockly)
        print(f"Placed {len(coords_list)} blocks.")


    # --- Methods matching Blockly generated calls ---

    def create_digital_ball(self, center_vec3, radius, block_type, inner_radius=0.0):
        """
        Blockly action to create a digital ball.
        center_vec3: A Vec3 instance.
        radius: float
        block_type: string (Blockly ID like 'STONE' or dict for colored glass)
        inner_radius: float (for hollow ball)
        """
        print(f"MCActions: create_digital_ball request at {center_vec3} with radius {radius}, inner {inner_radius}")
        coords = generate_digital_ball_coordinates(
            center=tuple(center_vec3),
            radius=float(radius),
            inner_radius=float(inner_radius)
        )
        self._place_blocks_from_coords(coords, block_type) # No additional offset needed if center is world coord

    def create_digital_tube(self, point1_vec3, point2_vec3, outer_thickness, block_type, inner_thickness=0.0):
        """
        Blockly action to create a digital tube.
        point1_vec3, point2_vec3: Vec3 instances for start and end points.
        outer_thickness: float
        block_type: string (Blockly ID)
        inner_thickness: float (for hollow tube)
        """
        print(f"MCActions: create_digital_tube request from {point1_vec3} to {point2_vec3}, thickness {outer_thickness}, inner {inner_thickness}")
        coords = generate_digital_tube_voxels(
            p1=tuple(point1_vec3),
            p2=tuple(point2_vec3),
            outer_thickness=float(outer_thickness),
            inner_thickness=float(inner_thickness)
        )
        self._place_blocks_from_coords(coords, block_type)

    # def create_digital_plane(self, normal_vec3, point_on_plane_vec3, block_type,
    #                            plane_thickness=1.0,
    #                            outer_radius_in_plane=float('inf'),
    #                            inner_radius_in_plane=0.0,
    #                            outer_rect_dims_tuple=None, # e.g., (10, 20)
    #                            inner_rect_dims_tuple=None,
    #                            rect_center_offset_vec3=None): # Vec3 for offset of rect center from point_on_plane
    #     """
    #     Blockly action to create a digital plane.
    #     normal_vec3, point_on_plane_vec3: Vec3 instances.
    #     outer_rect_dims_tuple, inner_rect_dims_tuple: tuple[float, float] or None
    #     rect_center_offset_vec3: Vec3 instance or None
    #     """
    #     print(f"MCActions: create_digital_plane request")
    #     offset_tuple = rect_center_offset_vec3.to_tuple() if rect_center_offset_vec3 else (0.0,0.0,0.0)
    #     coords = generate_digital_plane_voxels(
    #         normal=normal_vec3.to_tuple(),
    #         point_on_plane=point_on_plane_vec3.to_tuple(),
    #         plane_thickness=float(plane_thickness),
    #         outer_radius_in_plane=float(outer_radius_in_plane),
    #         inner_radius_in_plane=float(inner_radius_in_plane),
    #         outer_rect_dims=outer_rect_dims_tuple, # Already a tuple
    #         inner_rect_dims=inner_rect_dims_tuple, # Already a tuple
    #         rect_center_offset=offset_tuple
    #     )
    #     self._place_blocks_from_coords(coords, block_type)

    def create_digital_cube(self, center_vec3, side_length, rotation_matrix3, block_type, inner_offset_factor=0.0):
        """
        Blockly action to create a digital cube.
        center_vec3: Vec3 instance.
        side_length: float
        rotation_matrix3: Matrix3 instance.
        block_type: string (Blockly ID)
        inner_offset_factor: float (0 for solid, >0 for hollow shell thickness relative to centroid distances)
        """
        print(f"MCActions: create_digital_cube request at {center_vec3}, side {side_length}, factor {inner_offset_factor}")
        coords = generate_digital_cube_coordinates(
            center=tuple(center_vec3), # Your func expects tuple
            side_length=float(side_length),
            rotation_matrix=rotation_matrix3.to_numpy(), # Your func expects np.ndarray
            inner_offset_factor=float(inner_offset_factor)
        )
        self._place_blocks_from_coords(coords, block_type)

    def create_digital_tetrahedron(self, vertices_list_of_vec3, block_type, inner_offset_factor=0.0):
        """
        Blockly action to create a digital tetrahedron.
        vertices_list_of_vec3: A list of 4 Vec3 instances.
        block_type: string (Blockly ID)
        inner_offset_factor: float
        """
        if not isinstance(vertices_list_of_vec3, list) or len(vertices_list_of_vec3) != 4:
            print("Error: create_digital_tetrahedron expects a list of 4 Vec3 vertices.")
            return

        # Convert list of Vec3 objects to list of tuples for your geometry function
        vertex_tuples = [tuple(v) for v in vertices_list_of_vec3]

        print(f"MCActions: create_digital_tetrahedron request with {len(vertex_tuples)} vertices, factor {inner_offset_factor}")
        coords = generate_digital_tetrahedron_voxels(
            vertices=vertex_tuples,
            inner_offset_factor=float(inner_offset_factor)
        )
        self._place_blocks_from_coords(coords, block_type)

    def create_digital_plane(self, normal_vec3, point_on_plane_vec3, block_type,
                                   plane_thickness=1.0,
                                   outer_radius_in_plane=float('inf'), # Default in Python signature
                                   inner_radius_in_plane=0.0,    # Default in Python signature
                                   outer_rect_dims_tuple=None,     # Default in Python signature
                                   inner_rect_dims_tuple=None,     # Default in Python signature
                                   rect_center_offset_vec3=None):  # Default in Python signature
            """
            Blockly action to create a digital plane.
            normal_vec3, point_on_plane_vec3, rect_center_offset_vec3: Vec3 instances.
            outer_rect_dims_tuple, inner_rect_dims_tuple: tuple[float, float] or None.
            """
            print(f"MCActions: create_digital_plane request with normal {normal_vec3}, point {point_on_plane_vec3}")

            # Convert Vec3 inputs to tuples for your geometry library function
            normal_tuple = tuple(normal_vec3)
            point_on_plane_tuple = tuple(point_on_plane_vec3)

            # Handle rect_center_offset: if it's a Vec3, convert; if None from generator, use default for geometry function
            rect_center_offset_tuple = \
                tuple(rect_center_offset_vec3) \
                    if rect_center_offset_vec3 and isinstance(rect_center_offset_vec3,Vec3) else (0.0, 0.0, 0.0)

            # outer_rect_dims_tuple and inner_rect_dims_tuple are already expected as tuples or None
            # The generator provides "None" (string) which will become None object by ast.literal_eval
            # if your Vec3 generator returns a string. If Vec3 generator returns a Vec3 object,
            # then you might need to adjust how 'None' is handled for these tuple types.
            # For now, assuming the generator gives Python code that results in tuple or None.

            # Ensure numeric types are float
            try:
                plane_thickness_float = float(plane_thickness)
                outer_radius_float = float(outer_radius_in_plane) # float('inf') is already a float
                inner_radius_float = float(inner_radius_in_plane)
            except ValueError:
                print("Error: Thickness or radius values are not valid numbers.")
                return

            coords = generate_digital_plane_voxels(
                normal=normal_tuple,
                point_on_plane=point_on_plane_tuple,
                plane_thickness=plane_thickness_float,
                outer_radius_in_plane=outer_radius_float,
                inner_radius_in_plane=inner_radius_float,
                outer_rect_dims=outer_rect_dims_tuple, # Pass directly
                inner_rect_dims=inner_rect_dims_tuple, # Pass directly
                rect_center_offset=rect_center_offset_tuple
            )
            self._place_blocks_from_coords(coords, block_type)

#     # Add your existing methods like create_column, set_block etc. here,
#     # ensuring they also call self._parse_block_type and self._parse_position (if still needed for them)
#     # or directly expect Vec3 for positions.
#     def create_column(self, position, width, height, block_type, axis, filled):
#         # Assuming position is already a Vec3 from the generator for this block
#         parsed_block_type_id = self._parse_block_type(block_type)
#         width_val = int(width)
#         height_val = int(height)
#         print(f"ACTION: Creating COLUMN: pos={position}, w={width_val}, h={height_val}, type={parsed_block_type_id}, axis='{axis}', filled={filled}")
#         # Your column building logic using self.mc_player.setBlock(int(pos.x), int(pos.y), ... parsed_block_type_id)
#         # Example:
#         x_start, y_start, z_start = int(position.x), int(position.y), int(position.z)
#         if axis.lower() == 'y':
#             for dy in range(height_val):
#                 for dx_offset in range(-(width_val // 2), width_val // 2 + (width_val % 2)):
#                     for dz_offset in range(-(width_val // 2), width_val // 2 + (width_val % 2)):
#                         if filled:
#                              self.mc_player.setBlock(x_start + dx_offset, y_start + dy, z_start + dz_offset, parsed_block_type_id)
#         # ... Implement other axes
#         pass
#
# class MCActionsGeometric(MCActionBase):
#     def create_column(self,position, width, height, block_type, axis, filled):
#         _current_position = position.clone()
#         _direction, _face = self.mcplayer.cardinal_direction
#
#         # block_type is Blockly ID like constants.BLOCK_ID_MAP
#         if block_type.get('type') == 'GENERIC_MINECRAFT_BLOCK':
#             _mc_block_id = self.mcplayer.pc.getBlock(*_current_position)
#         else:
#             _mc_block_id = self.get_minecraft_id_from_blockly_id(block_type)
#
#
#         while True:
#             _v0 = _current_position.clone()
#             for _i in range(height):
#                 _v0.y += 1
#                 _v1 = self.translate_by_n(_v0,_direction,width)
#                 self.mcplayer.pc.setBlocks(*_v0, *_v1, _mc_block_id)
#
#
#
#     def create_cube(self,position, block_type,filled,size):
#         ...
#
