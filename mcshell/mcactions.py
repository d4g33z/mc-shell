import ast
from mcshell.mcplayer import MCPlayer
from mcshell.constants import *

from mcshell.mcvoxel import (
    generate_digital_tetrahedron_coordinates,
    generate_digital_tube_coordinates,
    generate_digital_plane_coordinates,
    generate_digital_ball_coordinates,
    generate_digital_cube_coordinates,
    generate_digital_disc_coordinates,
    generate_digital_line_coordinates,
    generate_digital_sphere_coordinates)

class MCActionBase:
    def __init__(self, mc_player_instance:MCPlayer,delay_between_blocks:float): # Added mc_version parameter
        """
        Initializes the action base.

        Args:
            mc_player_instance: An instance of a player connection class (e.g., MCPlayer).
            mc_version (str): The Minecraft version to load data for. This should match
                              the version of the server you are connecting to.
        """
        self.mcplayer = mc_player_instance

        # Initialize mapping dictionaries
        self.bukkit_to_entity_id_map = {}
        self._initialize_entity_id_map()

        # allow a delay for between visuals
        self.delay_between_blocks = delay_between_blocks

    def _place_blocks_from_coords(self, coords_list, block_type_from_blockly,
                                  placement_offset_vec3=None):
        """
        Helper method to take a list of coordinates and a Blockly block type,
        parse the block type, and set the blocks.
        """
        if not coords_list:
            print("No coordinates generated, nothing to place.")
            return

        # we use Bukkit IDs which are output in mc-ed
        minecraft_block_id = block_type_from_blockly

        print(f"Attempting to place {len(coords_list)} blocks of type '{minecraft_block_id}'")

        offset_x, offset_y, offset_z = (0,0,0)
        if placement_offset_vec3: # If a Vec3 object is given for overall placement
            offset_x, offset_y, offset_z = int(placement_offset_vec3.x), int(placement_offset_vec3.y), int(placement_offset_vec3.z)

        for x, y, z in coords_list:

            final_x = x + offset_x
            final_y = y + offset_y
            final_z = z + offset_z
            self.mcplayer.pc.setBlock(int(final_x), int(final_y), int(final_z), minecraft_block_id)

            # Pause execution for a fraction of a second
            if self.delay_between_blocks > 0:
                time.sleep(self.delay_between_blocks)

        print(f"Placed {len(coords_list)} blocks.")


    def _initialize_entity_id_map(self):
        self.bukkit_to_entity_id_map = pickle.load(MC_ENTITY_ID_MAP_PATH.open('rb'))

    def _get_entity_id_from_bukkit_name(self, bukkit_enum_string: str) -> Optional[int]:
        """
        Converts a Bukkit enum string (e.g., 'WITHER_SKELETON') to its Minecraft numeric ID.

        Args:
            bukkit_enum_string: The uppercase, underscore-separated entity name.

        Returns:
            The integer ID of the entity, or None if not found.
        """
        # Use .get() for a safe lookup that returns None if the key doesn't exist
        return self.bukkit_to_entity_id_map.get(bukkit_enum_string)

class MCActions(MCActionBase): # Inherits from MCActionBase
    def __init__(self, mc_player_instance,delay_between_blocks=0.01):
        super().__init__(mc_player_instance,delay_between_blocks) # Call parent constructor
        self.default_material_id = 1 # Example: material ID for stone in voxelmap
                                     # Or map block_type to material_id

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
            center=center_vec3.to_tuple(),
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
        coords = generate_digital_tube_coordinates(
            p1=point1_vec3.to_tuple(),
            p2=point2_vec3.to_tuple(),
            outer_thickness=float(outer_thickness),
            inner_thickness=float(inner_thickness)

        )
        self._place_blocks_from_coords(coords, block_type)

    def create_digital_line(self, point1_vec3, point2_vec3, block_type):
        """
        Blockly action to create a 1-voxel thick digital line.
        point1_vec3, point2_vec3: Vec3 instances.
        block_type: string (Blockly ID like 'STONE')
        """
        print(f"MCActions: create_digital_line request from {point1_vec3} to {point2_vec3}")

        # Convert Vec3 inputs to integer tuples for the geometry function
        p1_tuple = (int(round(point1_vec3.x)), int(round(point1_vec3.y)), int(round(point1_vec3.z)))
        p2_tuple = (int(round(point2_vec3.x)), int(round(point2_vec3.y)), int(round(point2_vec3.z)))

        # Call the low-level coordinate generation function
        coords = generate_digital_line_coordinates(
            p1=p1_tuple,
            p2=p2_tuple
        )

        # Use the existing helper to place the blocks
        self._place_blocks_from_coords(coords, block_type)

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
            center=center_vec3.to_tuple(), # Your func expects tuple
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
        vertex_tuples = [v.to_tuple() for v in vertices_list_of_vec3]

        print(f"MCActions: create_digital_tetrahedron request with {len(vertex_tuples)} vertices, factor {inner_offset_factor}")
        coords = generate_digital_tetrahedron_coordinates(
            vertices=vertex_tuples,
            inner_offset_factor=float(inner_offset_factor)
        )
        self._place_blocks_from_coords(coords, block_type)
    def create_digital_plane(self, normal_vec3, point_on_plane_vec3, block_type,
                               outer_rect_dims_tuple, # Now mandatory in Blockly block
                               plane_thickness=1.0,
                               inner_rect_dims_tuple=None,
                               rect_center_offset_vec3=None): # Default to Vec3(0,0,0) if None in generator
        print(f"MCActions: create_digital_plane request with normal {normal_vec3}, point {point_on_plane_vec3}")

        normal_tuple = (normal_vec3.x, normal_vec3.y, normal_vec3.z)
        point_on_plane_tuple = (point_on_plane_vec3.x, point_on_plane_vec3.y, point_on_plane_vec3.z)

        rect_center_offset_actual_tuple = (0.0, 0.0, 0.0)
        if rect_center_offset_vec3 and hasattr(rect_center_offset_vec3, 'x'): # Check if it's Vec3-like
            rect_center_offset_actual_tuple = (rect_center_offset_vec3.x, rect_center_offset_vec3.y, rect_center_offset_vec3.z)

        # outer_rect_dims_tuple comes as a Python tuple string e.g. "(10, 10)" from the generator if minecraft_vector_2d is used.
        # It needs to be parsed if it's a string. If it's already a tuple (e.g. from direct Python call), use as is.
        final_outer_rect_dims = None
        if isinstance(outer_rect_dims_tuple, str):
            try:
                final_outer_rect_dims = ast.literal_eval(outer_rect_dims_tuple)
                if not (isinstance(final_outer_rect_dims, tuple) and len(final_outer_rect_dims) == 2):
                    print(f"Warning: outer_rect_dims_tuple '{outer_rect_dims_tuple}' not a valid 2D tuple. Using None.")
                    final_outer_rect_dims = None # Or a default like (10,10)
            except:
                print(f"Warning: Could not parse outer_rect_dims_tuple '{outer_rect_dims_tuple}'. Using None.")
                final_outer_rect_dims = None
        elif isinstance(outer_rect_dims_tuple, tuple) and len(outer_rect_dims_tuple) == 2:
            final_outer_rect_dims = outer_rect_dims_tuple
        else:
            print(f"Warning: outer_rect_dims type unexpected ({type(outer_rect_dims_tuple)}). Must be tuple or string rep. of tuple. Using (10,10) default.")
            final_outer_rect_dims = (10,10) # Fallback default if no valid outer_rect_dims provided

        final_inner_rect_dims = None
        if isinstance(inner_rect_dims_tuple, str) and inner_rect_dims_tuple.lower() != 'none':
            try:
                final_inner_rect_dims = ast.literal_eval(inner_rect_dims_tuple)
                if not (isinstance(final_inner_rect_dims, tuple) and len(final_inner_rect_dims) == 2):
                    final_inner_rect_dims = None
            except:
                final_inner_rect_dims = None
        elif isinstance(inner_rect_dims_tuple, tuple) and len(inner_rect_dims_tuple) == 2:
            final_inner_rect_dims = inner_rect_dims_tuple


        coords = generate_digital_plane_coordinates( # Call your refactored function
            normal=normal_tuple,
            point_on_plane=point_on_plane_tuple,
            outer_rect_dims=final_outer_rect_dims, # Pass the parsed/validated tuple
            plane_thickness=float(plane_thickness),
            inner_rect_dims=final_inner_rect_dims, # Pass the parsed/validated tuple
            rect_center_offset=rect_center_offset_actual_tuple
        )
        self._place_blocks_from_coords(coords, block_type)

    def create_digital_disc(self, normal_vec3, center_point_vec3, outer_radius,
                              block_type, disc_thickness=1.0, inner_radius=0.0):
        print(f"MCActions: create_digital_disc request with normal {normal_vec3}, center {center_point_vec3}")

        normal_tuple = (normal_vec3.x, normal_vec3.y, normal_vec3.z)
        center_point_tuple = (center_point_vec3.x, center_point_vec3.y, center_point_vec3.z)

        coords = generate_digital_disc_coordinates( # Call your new function
            normal=normal_tuple,
            center_point=center_point_tuple,
            outer_radius=float(outer_radius),
            disc_thickness=float(disc_thickness),
            inner_radius=float(inner_radius)
        )
        self._place_blocks_from_coords(coords, block_type)

    def spawn_entity(self, position_vec3, entity_type):
        """
        Blockly action to spawn a Minecraft entity. It now uses the helper method
        to convert the Blockly entity ID string to a numerical ID.

        Args:
            position_vec3 (Vec3): A Vec3 instance for the spawn location.
            entity_type (str): The Blockly-generated Bukkit enum string (e.g., 'PIG', 'ZOMBIE').
        """
        # Convert the Bukkit enum string to its required integer ID
        entity_id_int = self._get_entity_id_from_bukkit_name(entity_type)

        if entity_id_int is None:
            print(f"Warning: Could not find a numerical ID for entity type '{entity_type}'. Cannot spawn.")
            return

        print(f"ACTION: Spawning entity '{entity_type}' (ID: {entity_id_int}) at position {position_vec3}")

        # Now call pyncraft with the correct integer ID 1 unit above the requested position for safety
        self.mcplayer.pc.spawnEntity(position_vec3.x, position_vec3.y + 1, position_vec3.z, entity_id_int)

    def set_block(self, position_vec3, block_type):
        """
        Blockly action to set a single block in the Minecraft world.

        Args:
            position_vec3 (Vec3): A Vec3 instance for the block's location.
            block_type (str): The Blockly-generated ID for the block (e.g., 'STONE', 'OAK_FENCE').
        """
        # The position is already a Vec3 object.
        # The block_type is a string ID that needs to be parsed into a Minecraft ID.
        # parsed_block_type_id = self._parse_block_type(block_type)
        parsed_block_type_id = block_type

        # Access coordinates directly from the Vec3 object
        x, y, z = (int(position_vec3.x), int(position_vec3.y), int(position_vec3.z))

        print(f"ACTION: Setting block at ({x},{y},{z}) to {parsed_block_type_id} "
              f"for player {getattr(self.mcplayer, 'name', 'N/A')}")

        # This is where you would call the actual pyncraft or Minecraft API method
        self.mcplayer.pc.setBlock(x, y, z, parsed_block_type_id)