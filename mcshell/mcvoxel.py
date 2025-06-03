import numpy as np
import math
import voxelmap as vxm # Make sure voxelmap is installed: pip install voxelmap

# --- Helper functions (from previous turns, included for completeness) ---

def create_dgtal_digital_set_from_coords(coords):
    """
    Creates a DGtal DigitalSet from a list of (x, y, z) integer coordinates.
    This demonstrates DGtal's capability to represent discrete sets of points.

    Args:
        coords (list): A list of (x, y, z) tuples.

    Returns:
        dgtal.kernel.DigitalSetZ3i: A DGtal DigitalSet containing the voxels.
    """
    if not coords:
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0
        min_z, max_z = 0, 0
    else:
        min_x = min(p[0] for p in coords)
        max_x = max(p[0] for p in coords)
        min_y = min(p[1] for p in coords)
        max_y = max(p[1] for p in coords)
        min_z = min(p[2] for p in coords)
        max_z = max(p[2] for p in coords)

    try:
        import dgtal
        lower_bound = dgtal.kernel.Point3D(min_x, min_y, min_z)
        upper_bound = dgtal.kernel.Point3D(max_x, max_y, max_z)
        domain = dgtal.kernel.DomainZ3i(lower_bound, upper_bound)
        digital_set = dgtal.kernel.DigitalSetZ3i(domain)
        for x, y, z in coords:
            digital_set.insert(dgtal.kernel.Point3D(x, y, z))
        return digital_set
    except ImportError:
        print("DGtal not installed. Cannot create DigitalSet.")
        return None

def create_voxelmap_array_from_coords(coords, grid_shape=None):
    """
    Creates a 3D NumPy array (dense voxel grid) suitable for voxelmap.
    This function calculates the bounding box of the points and creates a
    dense 3D array, marking occupied voxels.
    """
    if not coords:
        return np.array([])

    coords_np = np.array(coords)

    min_bounds = coords_np.min(axis=0)
    max_bounds = coords_np.max(axis=0)

    if grid_shape is None:
        dims = (max_bounds - min_bounds + 1).astype(int)
    else:
        dims = np.array(grid_shape).astype(int)
        min_bounds = np.array([0,0,0])

    voxel_array = np.zeros(dims, dtype=int







)

    for x, y, z in coords:
        local_x = x - min_bounds[0]
        local_y = y - min_bounds[1]
        local_z = z - min_bounds[2]
        if 0 <= local_x < dims[0] and 0 <= local_y < dims[1] and 0 <= local_z < dims[2]:
            voxel_array[local_x, local_y, local_z] = 1

    return voxel_array

# --- NEW: Function to add coordinates to an existing voxelmap.Model ---
def add_coordinates_to_voxelmap_model(model: vxm.Model, coords: list[tuple[int, int, int]], material_id: int, offset: tuple[int, int, int] = (0, 0, 0)):
    """
    Adds a list of (x, y, z) coordinates to an existing voxelmap.Model's array,
    applying an offset and clamping to the model's array dimensions.

    Args:
        model: The Voxelmap Model instance with its array already initialized.
        coords: A list of (x, y, z) integer coordinates to add.
        material_id: The non-zero integer value to use for the voxels.
        offset: An (x, y, z) integer tuple to offset the coordinates before placing them.
                Useful for placing shapes at specific positions within the model's grid.
    """
    if not coords:
        return # Nothing to add

    array_shape = model.array.shape

    for x, y, z in coords:
        # Apply offset
        display_x = x + offset[0]
        display_y = y + offset[1]
        display_z = z + offset[2]

        # Clamp to model's array bounds
        if 0 <= display_x < array_shape[0] and \
           0 <= display_y < array_shape[1] and \
           0 <= display_z < array_shape[2]:
            model.array[display_x, display_y, display_z] = material_id

# --- Geometric Construction Functions (Refactored to remove domain_min/max) ---

def generate_digital_ball_coordinates(center: tuple[float, float, float], radius: float, inner_radius: float = 0.0):
    """
    Generates integer XYZ coordinates for a solid or hollow digital ball.
    """
    cx, cy, cz = center
    outer_r_squared = radius ** 2
    inner_r_squared = inner_radius ** 2

    digital_ball_coords = set()

    if inner_radius >= radius and radius > 0: # Allow radius=0 for a single point if desired, though not typical for ball
        print(f"Warning: inner_radius ({inner_radius}) is greater than or equal to outer_radius ({radius}). "
              "This will result in an empty or very thin ball, and no voxels will be generated.")
        return []

    x_min = int(math.floor(cx - radius))
    y_min = int(math.floor(cy - radius))
    z_min = int(math.floor(cz - radius))
    x_max = int(math.ceil(cx + radius))
    y_max = int(math.ceil(cy + radius))
    z_max = int(math.ceil(cz + radius))

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            for z in range(z_min, z_max + 1):
                voxel_center_x = x + 0.5
                voxel_center_y = y + 0.5
                voxel_center_z = z + 0.5
                distance_squared = (voxel_center_x - cx)**2 + \
                                   (voxel_center_y - cy)**2 + \
                                   (voxel_center_z - cz)**2

                if inner_r_squared < distance_squared <= outer_r_squared:
                    digital_ball_coords.add((x, y, z))

    return sorted(list(digital_ball_coords))

# --- Helper for point-to-segment distance (needed for thick lines) ---
def distance_point_to_segment(p, a, b):
    p_np = np.array(p)
    a_np = np.array(a)
    b_np = np.array(b)

    ab = b_np - a_np
    ap = p_np - a_np

    denominator = np.dot(ab, ab)
    if denominator < 1e-9: # Handle zero-length segment
        return np.linalg.norm(p_np - a_np)

    t = np.dot(ap, ab) / denominator
    t = max(0.0, min(1.0, t))

    closest_point = a_np + t * ab
    return np.linalg.norm(p_np - closest_point)

def generate_digital_tube_voxels(p1, p2, outer_thickness: float, inner_thickness: float = 0.0):
    """
    Generates integer XYZ coordinates for a digital line segment with a specified thickness,
    creating a solid cylinder (tube) or a hollow cylindrical shell.
    """
    if inner_thickness >= outer_thickness and outer_thickness > 0:
        print(f"Warning: inner_thickness ({inner_thickness}) is >= outer_thickness ({outer_thickness}). "
              "This will result in an empty or invalid tube.")
        return []

    tube_voxels = set()

    x_min = int(math.floor(min(p1[0], p2[0]) - outer_thickness))
    x_max = int(math.ceil(max(p1[0], p2[0]) + outer_thickness))
    y_min = int(math.floor(min(p1[1], p2[1]) - outer_thickness))
    y_max = int(math.ceil(max(p1[1], p2[1]) + outer_thickness))
    z_min = int(math.floor(min(p1[2], p2[2]) - outer_thickness))
    z_max = int(math.ceil(max(p1[2], p2[2]) + outer_thickness))

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            for z in range(z_min, z_max + 1):
                voxel_center = (x + 0.5, y + 0.5, z + 0.5)
                dist_to_segment = distance_point_to_segment(voxel_center, p1, p2)

                if inner_thickness < dist_to_segment <= outer_thickness:
                    tube_voxels.add((x, y, z))
    return sorted(list(tube_voxels))

# --- Helper to get orthonormal basis for a plane, given its normalized normal vector ---
def get_plane_basis(normal_vec_norm_tuple_or_array):
    normal_vec_norm = np.array(normal_vec_norm_tuple_or_array) # Ensure it's an array

    if np.linalg.norm(normal_vec_norm) < 1e-9: # Handle zero normal vector
        # Default basis if normal is zero (though this shouldn't happen with valid inputs)
        return np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])


    # Try to pick a non-parallel vector to normal_vec_norm to form cross product
    if np.isclose(np.linalg.norm(np.cross(normal_vec_norm, [1,0,0])), 0):
        temp_vec = np.array([0.0, 1.0, 0.0])
    else:
        temp_vec = np.array([1.0, 0.0, 0.0])

    u_vec = np.cross(normal_vec_norm, temp_vec)
    u_vec_norm = np.linalg.norm(u_vec)
    if u_vec_norm < 1e-9: # Should not happen if normal_vec_norm is not parallel to temp_vec choice logic is sound
        # Fallback if somehow u_vec became zero (e.g. normal_vec_norm was [0,1,0] and temp_vec was [0,1,0])
        # This case should be covered by the temp_vec selection logic.
        # If normal is (0,1,0), cross with (1,0,0) is (0,0,-1) - fine.
        # If normal is (1,0,0), cross with (0,1,0) is (0,0,1) - fine.
        # Adding safety for robustness, though theoretically covered.
        temp_vec = np.array([0.0,0.0,1.0]) # Try z-axis
        u_vec = np.cross(normal_vec_norm, temp_vec)
        u_vec_norm = np.linalg.norm(u_vec)
        if u_vec_norm < 1e-9: # Extremely unlikely pathological case
             # If normal was z-axis, cross with x is y, cross with y is -x
             # This implies normal_vec_norm itself might be an issue or all axes are parallel.
             # Default to arbitrary orthogonal vectors if all else fails.
             return np.array([1.,0.,0.]), np.array([0.,1.,0.]) if not np.allclose(normal_vec_norm, [0,0,1]) else np.array([1.,0.,0.]), np.array([0.,0.,1.])


    u_vec = u_vec / u_vec_norm


    v_vec = np.cross(normal_vec_norm, u_vec)
    # v_vec should already be normalized because normal_vec_norm and u_vec are orthogonal unit vectors.
    # v_vec_norm = np.linalg.norm(v_vec)
    # if v_vec_norm > 1e-9: v_vec = v_vec / v_vec_norm

    return u_vec, v_vec

def generate_digital_plane_voxels(normal, point_on_plane,
                                  plane_thickness: float = 1.0,
                                  outer_radius_in_plane: float = float('inf'),
                                  inner_radius_in_plane: float = 0.0,
                                  outer_rect_dims: tuple[float, float] = None, # (width, height)
                                  inner_rect_dims: tuple[float, float] = None, # (width, height)
                                  rect_center_offset: tuple[float, float, float] = (0.0, 0.0, 0.0)):
    """
    Generates integer XYZ coordinates for a digital plane.
    """
    nx, ny, nz = normal
    px, py, pz = point_on_plane

    plane_coords = set()

    norm_val = math.sqrt(nx**2 + ny**2 + nz**2)
    if norm_val < 1e-9: # Changed from == 0 for float comparison
        print("Error: Normal vector cannot be zero.")
        return []

    normal_vec_norm = np.array([nx / norm_val, ny / norm_val, nz / norm_val])
    D_plane = -np.dot(normal_vec_norm, np.array([px, py, pz]))

    outer_radius_in_plane_sq = outer_radius_in_plane**2
    inner_radius_in_plane_sq = inner_radius_in_plane**2

    u_vec, v_vec = get_plane_basis(normal_vec_norm)
    rect_center_on_plane = np.array(point_on_plane) + np.array(rect_center_offset)

    # Determine the effective extent for iteration bounds
    extent_for_iteration = 0.0
    has_defined_extent = False

    if outer_rect_dims:
        extent_for_iteration = math.sqrt((outer_rect_dims[0]/2)**2 + (outer_rect_dims[1]/2)**2)
        has_defined_extent = True

    if outer_radius_in_plane != float('inf'):
        if has_defined_extent:
            extent_for_iteration = max(extent_for_iteration, outer_radius_in_plane)
        else:
            extent_for_iteration = outer_radius_in_plane
        has_defined_extent = True

    if not has_defined_extent: # This means outer_radius_in_plane was inf and no outer_rect_dims
        # Iteration extent is conceptually infinite. Fallback to a large finite extent.
        # This value should ideally be related to the overall scene size if known.
        # For the example grid_size=50, a value like 50-100 from point_on_plane is reasonable.
        extent_for_iteration = 75.0 # Default large extent for "infinite" planes
        print(f"Warning: Generating an 'infinite' plane (outer_radius_in_plane=inf and no outer_rect_dims). "
              f"Using a fallback iteration extent of {extent_for_iteration} units around point_on_plane. "
              f"Consider providing outer_rect_dims for very large scenes or if clipping is unexpected.")


    x_min = int(math.floor(px - extent_for_iteration - plane_thickness))
    x_max = int(math.ceil(px + extent_for_iteration + plane_thickness))
    y_min = int(math.floor(py - extent_for_iteration - plane_thickness))
    y_max = int(math.ceil(py + extent_for_iteration + plane_thickness))
    z_min = int(math.floor(pz - extent_for_iteration - plane_thickness))
    z_max = int(math.ceil(pz + extent_for_iteration + plane_thickness))

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            for z in range(z_min, z_max + 1):
                voxel_center = np.array([x + 0.5, y + 0.5, z + 0.5])
                signed_perpendicular_dist = np.dot(normal_vec_norm, voxel_center) + D_plane

                if not (abs(signed_perpendicular_dist) <= plane_thickness / 2.0):
                    continue

                projected_point = voxel_center - signed_perpendicular_dist * normal_vec_norm
                is_within_boundary = False

                if outer_rect_dims:
                    half_width_outer = outer_rect_dims[0] / 2.0
                    half_height_outer = outer_rect_dims[1] / 2.0
                    local_point = projected_point - rect_center_on_plane
                    local_u = np.dot(local_point, u_vec)
                    local_v = np.dot(local_point, v_vec)

                    is_within_outer_rect = (abs(local_u) <= half_width_outer and
                                            abs(local_v) <= half_height_outer)
                    if not is_within_outer_rect:
                        continue

                    if inner_rect_dims:
                        half_width_inner = inner_rect_dims[0] / 2.0
                        half_height_inner = inner_rect_dims[1] / 2.0
                        is_outside_inner_rect = (abs(local_u) > half_width_inner or
                                                 abs(local_v) > half_height_inner)
                        if is_outside_inner_rect:
                            is_within_boundary = True
                    else: # No inner rect means solid rect
                        is_within_boundary = True
                # Check circular bounds ONLY if outer_rect_dims were NOT specified
                # (as per problem description, rect takes precedence if given)
                elif outer_radius_in_plane != float('inf') or inner_radius_in_plane > 0.0:
                    dist_in_plane_sq = np.linalg.norm(projected_point - np.array(point_on_plane))**2
                    is_within_outer_circle = (dist_in_plane_sq <= outer_radius_in_plane_sq)
                    is_outside_inner_circle = (dist_in_plane_sq > inner_radius_in_plane_sq)

                    if is_within_outer_circle and is_outside_inner_circle:
                        is_within_boundary = True
                else: # No rectangular boundary, and no finite circular boundary specified -> effectively infinite plane part
                    is_within_boundary = True

                if is_within_boundary:
                    plane_coords.add((x, y, z))
    return sorted(list(plane_coords))

# --- Helper for Oriented Cube / Tetrahedron ---
def is_point_inside_polyhedron(point_np, polyhedron_vertices):
    raise NotImplementedError("is_point_inside_polyhedron needs specific face definitions per polyhedron type.")

# --- Helper function to get cube vertices (ADDED) ---
def get_oriented_cube_vertices(center: np.ndarray, side_length: float, rotation_matrix: np.ndarray) -> list[tuple[float, float, float]]:
    """
    Calculates the 8 vertices of an oriented cube.
    Args:
        center: Numpy array (x, y, z) of the cube's center.
        side_length: The side length of the cube.
        rotation_matrix: A 3x3 NumPy array for rotation.
    Returns:
        A list of 8 (x,y,z) tuples representing the cube's vertices.
    """
    h = side_length / 2.0
    # Local vertices (around origin)
    local_vertices = [
        np.array([-h, -h, -h]), np.array([h, -h, -h]),
        np.array([-h, h, -h]), np.array([h, h, -h]),
        np.array([-h, -h, h]), np.array([h, -h, h]),
        np.array([-h, h, h]), np.array([h, h, h])
    ]

    world_vertices = []
    for lv in local_vertices:
        rotated_vertex = rotation_matrix @ lv
        world_vertex = center + rotated_vertex
        world_vertices.append(tuple(world_vertex))
    return world_vertices

# This helper is specific to a cube, so it belongs with the cube generation.
def _is_point_inside_oriented_cube_helper(point_np, cube_vertices_np_list_of_arrays):
    """
    Internal helper for generate_digital_cube_coordinates to check point interiority.
    Expects cube_vertices_np_list_of_arrays to be a list of numpy arrays (vertices).
    """
    # Convert list of vertex arrays/tuples to a single Nx3 numpy array if it's not already
    if not isinstance(cube_vertices_np_list_of_arrays, np.ndarray) or cube_vertices_np_list_of_arrays.ndim != 2:
         cube_vertices_np = np.array([list(v) for v in cube_vertices_np_list_of_arrays])
    else:
         cube_vertices_np = cube_vertices_np_list_of_arrays

    centroid = np.mean(cube_vertices_np, axis=0)

    faces_vertex_indices = [
        (0, 2, 3, 1), # Bottom face (-z if original local coords had z up/down)
        (4, 5, 7, 6), # Top face (+z)
        (0, 1, 5, 4), # One side face
        (2, 6, 7, 3), # Opposite side face
        (0, 4, 6, 2), # Another side face
        (1, 3, 7, 5)  # Opposite of that
    ]
    # The exact face orientation (e.g. "Bottom") depends on how get_oriented_cube_vertices maps local to world.
    # The important part is that these are the 6 faces.

    for indices in faces_vertex_indices:
        v0, v1, v2 = cube_vertices_np[indices[0]], cube_vertices_np[indices[1]], cube_vertices_np[indices[2]]
        normal = np.cross(v1 - v0, v2 - v0)
        norm_mag = np.linalg.norm(normal)
        if norm_mag < 1e-9: continue # Degenerate face normal

        normal /= norm_mag # Normalize

        # Ensure normal points inwards (towards centroid)
        # If dot(normal, vector_from_face_to_centroid) is negative, normal is outward, so flip it.
        if np.dot(normal, centroid - v0) < 0:
            normal = -normal

        D = -np.dot(normal, v0) # Plane equation: normal.x + D = 0

        # If point is on the "positive" side of the plane (i.e., outside for an inward normal)
        if np.dot(normal, point_np) + D > 1e-6: # Use a small epsilon for floating point
            return False
    return True


def generate_digital_cube_coordinates(center: tuple[float, float, float], side_length: float, rotation_matrix: np.ndarray,
                                      inner_offset_factor: float = 0.0):
    """
    Generates integer XYZ coordinates for a solid or hollow digital cube with arbitrary orientation.
    """
    cube_coords = set()
    center_np = np.array(center)

    if inner_offset_factor >= 1.0 and inner_offset_factor != 0.0: # inner_offset_factor = 0 means solid
        print(f"Warning: inner_offset_factor ({inner_offset_factor}) is >= 1.0. This will result in an empty cube.")
        return []
    if side_length <= 0:
        return []


    outer_cube_vertices_list_tuples = get_oriented_cube_vertices(center_np, side_length, rotation_matrix)
    # _is_point_inside_oriented_cube_helper expects a list of np.arrays or a 2D np.array
    outer_cube_vertices_for_check = [np.array(v) for v in outer_cube_vertices_list_tuples]


    # Create a bounding box for iteration from the actual outer vertices
    if not outer_cube_vertices_for_check: return [] # Should not happen if side_length > 0

    outer_vertices_np_array = np.array(outer_cube_vertices_for_check)
    min_coords_bb = np.floor(outer_vertices_np_array.min(axis=0)).astype(int)
    max_coords_bb = np.ceil(outer_vertices_np_array.max(axis=0)).astype(int)

    min_x_bb, min_y_bb, min_z_bb = min_coords_bb
    max_x_bb, max_y_bb, max_z_bb = max_coords_bb

    inner_cube_vertices_for_check = None
    if inner_offset_factor > 0.0: # Hollow cube
        # Scale towards centroid for inner vertices
        # The centroid of the outer cube is simply center_np
        inner_verts_temp = []
        for v_outer_tuple in outer_cube_vertices_list_tuples:
            v_outer_np = np.array(v_outer_tuple)
            # Vector from centroid to outer vertex
            vec_to_outer = v_outer_np - center_np
            # Scale this vector by (1.0 - shell_thickness_factor_related_to_side)
            # Or, more directly, inner vertices are closer to centroid
            # inner_side_length = side_length * (1.0 - some_thickness_param)
            # For inner_offset_factor: if 0.8, inner cube is 80% of outer, centered.
            # No, the original logic was: v_inner = centroid + (v_outer_np - centroid) * inner_offset_factor
            # This means inner_offset_factor is a scale factor for the *vertices relative to centroid*.
            # If inner_offset_factor = 0.8, vertices are 80% of the distance from centroid.
            # This implies an inner side length of side_length * inner_offset_factor IF it was axis aligned scaling.
            # For a rotated cube, this scales each vertex towards the centroid along the line connecting them.
            # This creates a smaller, similarly oriented cube inside.
            v_inner = center_np + (v_outer_np - center_np) * inner_offset_factor
            inner_verts_temp.append(tuple(v_inner))
        inner_cube_vertices_for_check = [np.array(v) for v in inner_verts_temp]


    for x in range(min_x_bb, max_x_bb + 1):
        for y in range(min_y_bb, max_y_bb + 1):
            for z in range(min_z_bb, max_z_bb + 1):
                voxel_center = np.array([x + 0.5, y + 0.5, z + 0.5])
                is_inside_outer = _is_point_inside_oriented_cube_helper(voxel_center, outer_cube_vertices_for_check)

                if is_inside_outer:
                    if inner_offset_factor == 0.0: # Solid cube
                        cube_coords.add((x, y, z))
                    else: # Hollow cube, check if outside inner cube
                        if inner_cube_vertices_for_check: # Should always be true if inner_offset_factor > 0
                            is_inside_inner = _is_point_inside_oriented_cube_helper(voxel_center, inner_cube_vertices_for_check)
                            if not is_inside_inner:
                                cube_coords.add((x, y, z))
                        else: # Should not happen due to checks, but as a fallback treat as solid if inner def failed
                             cube_coords.add((x, y, z))


    return sorted(list(cube_coords))

# --- This helper is specific to a tetrahedron, so it belongs with the tetrahedron generation.
def _is_point_inside_tetrahedron_helper(point_np, tetra_vertices_np_list_of_arrays):
    """
    Internal helper for generate_digital_tetrahedron_voxels to check point interiority.
    """
    if not isinstance(tetra_vertices_np_list_of_arrays, np.ndarray) or tetra_vertices_np_list_of_arrays.ndim != 2:
        # Ensure tetra_vertices_np is a 2D NumPy array of floats for consistent calculations
        tetra_vertices_np = np.array([list(v) for v in tetra_vertices_np_list_of_arrays], dtype=np.float64)
    else:
        # If it's already a NumPy array, ensure it's float
        tetra_vertices_np = tetra_vertices_np_list_of_arrays.astype(np.float64, copy=False)


    if tetra_vertices_np.shape[0] != 4:
        print("Error: Tetrahedron helper needs exactly 4 vertices.")
        return False

    centroid_t = np.mean(tetra_vertices_np, axis=0)

    faces_defs = [
        ( (tetra_vertices_np[0], tetra_vertices_np[1], tetra_vertices_np[2]), tetra_vertices_np[3] ),
        ( (tetra_vertices_np[0], tetra_vertices_np[1], tetra_vertices_np[3]), tetra_vertices_np[2] ),
        ( (tetra_vertices_np[0], tetra_vertices_np[2], tetra_vertices_np[3]), tetra_vertices_np[1] ),
        ( (tetra_vertices_np[1], tetra_vertices_np[2], tetra_vertices_np[3]), tetra_vertices_np[0] )
    ]

    for (v0, v1, v2), v_opposite in faces_defs:
        # Ensure v0, v1, v2 are float for cross product to yield float normal
        # This is handled by ensuring tetra_vertices_np is float at the start.
        normal = np.cross(v1 - v0, v2 - v0) # Now normal should be float

        norm_mag = np.linalg.norm(normal)
        if norm_mag < 1e-9: continue

        normal /= norm_mag # In-place division is now safe as normal is float

        vec_to_opposite = v_opposite - v0
        if np.dot(normal, vec_to_opposite) < 0:
            normal = -normal

        D_face = -np.dot(normal, v0)

        if np.dot(normal, point_np) + D_face > 1e-6:
            return False

    return True

def generate_digital_tetrahedron_voxels(vertices: list[tuple[float,float,float]], inner_offset_factor: float = 0.0):
    """
    Generates integer XYZ coordinates for a solid or hollow digital tetrahedron.
    """
    if len(vertices) != 4:
        print("Error: Tetrahedron requires exactly 4 vertices.")
        return []

    outer_tetra_vertices_tuples = vertices
    outer_tetra_vertices_for_check = [np.array(v) for v in outer_tetra_vertices_tuples]


    tetra_coords = set()

    if inner_offset_factor >= 1.0 and inner_offset_factor != 0.0:
        print(f"Warning: inner_offset_factor ({inner_offset_factor}) is >= 1.0. This will result in an empty tetrahedron.")
        return []

    outer_vertices_np_array = np.array(outer_tetra_vertices_for_check)
    min_coords_bb = np.floor(outer_vertices_np_array.min(axis=0)).astype(int)
    max_coords_bb = np.ceil(outer_vertices_np_array.max(axis=0)).astype(int)
    min_x_bb, min_y_bb, min_z_bb = min_coords_bb
    max_x_bb, max_y_bb, max_z_bb = max_coords_bb


    inner_tetra_vertices_for_check = None
    if inner_offset_factor > 0.0: # Hollow
        centroid_outer = np.mean(outer_vertices_np_array, axis=0)
        inner_verts_temp = []
        for v_outer_np in outer_tetra_vertices_for_check:
            v_inner = centroid_outer + (v_outer_np - centroid_outer) * inner_offset_factor
            inner_verts_temp.append(v_inner) # Keep as np.array
        inner_tetra_vertices_for_check = inner_verts_temp


    for x in range(min_x_bb, max_x_bb + 1):
        for y in range(min_y_bb, max_y_bb + 1):
            for z in range(min_z_bb, max_z_bb + 1):
                voxel_center = np.array([x + 0.5, y + 0.5, z + 0.5])
                is_inside_outer = _is_point_inside_tetrahedron_helper(voxel_center, outer_tetra_vertices_for_check)

                if is_inside_outer:
                    if inner_offset_factor == 0.0: # Solid
                        tetra_coords.add((x, y, z))
                    else: # Hollow
                        if inner_tetra_vertices_for_check:
                            is_inside_inner = _is_point_inside_tetrahedron_helper(voxel_center, inner_tetra_vertices_for_check)
                            if not is_inside_inner:
                                tetra_coords.add((x, y, z))
                        else: # Fallback if inner definition failed
                            tetra_coords.add((x, y, z))
    return sorted(list(tetra_coords))

def generate_digital_sphere_coordinates(center: tuple[float,float,float],radius: float, is_solid=False):
    # def generate_digital_sphere_coordinates(center_x, center_y, center_z, radius, is_solid=False):
    """
    Generates integer XYZ coordinates for a digital sphere's surface or solid.

    This algorithm works by iterating through Z-slices of the sphere. For each Z-slice,
    it calculates the radius of the 2D circle at that slice and then uses the
    Midpoint Circle Algorithm to find the integer points on that circle.
    Symmetry is exploited to efficiently generate all points.

    If is_solid is True, it fills all points within each 2D circle slice.

    Args:
        center: The (x, y, z) coordinates of the sphere's center (can be float).
        radius (int): Integer radius of the sphere.
        is_solid (bool): If True, generates a solid sphere; otherwise, generates a surface sphere.

    Returns:
        list: A list of (x, y, z) tuples representing the integer coordinates
              of the voxels forming the digital sphere's surface or solid.
    """

    center_x,center_y,center_z = center

    sphere_coords = set()  # Use a set to automatically handle duplicate points

    # Iterate through Z-slices from bottom to top of the sphere
    # The z_offset determines the vertical distance from the sphere's center
    for z_offset in range(-radius, radius + 1):
        z = center_z + z_offset

        # Calculate the squared radius of the 2D circle slice at this Z-level.
        # This is derived from the sphere equation: r_sphere^2 = x^2 + y^2 + z_offset^2
        # So, r_slice^2 = r_sphere^2 - z_offset^2
        r_slice_squared = radius ** 2 - z_offset ** 2

        # If r_slice_squared is negative, it means this Z-slice is outside the sphere's bounds.
        if r_slice_squared < 0:
            continue

        # Calculate the integer radius for the current 2D circle slice.
        # We round to the nearest integer to get the discrete radius.
        r_slice = int(round(math.sqrt(r_slice_squared)))

        # Apply the Midpoint Circle Algorithm for the current 2D slice
        x = r_slice
        y = 0
        p = 1 - r_slice  # Initial decision parameter for the Midpoint Circle Algorithm

        while x >= y:
            # Add points for all 8 octants of the current circle slice, translated to the sphere's center
            # and current Z-level.
            if is_solid:
                # Fill horizontal lines for the current (x, y) and its symmetric counterparts
                for i in range(center_x - x, center_x + x + 1):
                    sphere_coords.add((i, center_y + y, z))
                    sphere_coords.add((i, center_y - y, z))
                # Fill horizontal lines for the transposed (y, x) and its symmetric counterparts
                for i in range(center_x - y, center_x + y + 1):
                    sphere_coords.add((i, center_y + x, z))
                    sphere_coords.add((i, center_y - x, z))
            else:
                # Add only the perimeter points for surface sphere
                sphere_coords.add((center_x + x, center_y + y, z))
                sphere_coords.add((center_x - x, center_y + y, z))
                sphere_coords.add((center_x + x, center_y - y, z))
                sphere_coords.add((center_x - x, center_y - y, z))
                sphere_coords.add((center_x + y, center_y + x, z))
                sphere_coords.add((center_x - y, center_y + x, z))
                sphere_coords.add((center_x + y, center_y - x, z))
                sphere_coords.add((center_x - y, center_y - x, z))

            y += 1  # Move to the next y-coordinate
            # Update the decision parameter based on whether the midpoint is inside or outside the circle
            if p < 0:
                p = p + 2 * y + 1
            else:
                x -= 1  # Move to the next x-coordinate (closer to the center)
                p = p + 2 * y - 2 * x + 1

    # Convert the set of coordinates to a sorted list for consistent output
    return sorted(list(sphere_coords))

# --- Main execution block ---
if __name__ == "__main__":
    # Initialize a Voxelmap Model with a sufficiently large empty array
    grid_size = 50
    model = vxm.Model()
    model.array = np.zeros((grid_size, grid_size, grid_size), dtype=int)

    # Define material colors for visualization
    model.hashblocks = {
        1: ['#FF0000', 1.0], # Red
        2: ['#0000FF', 1.0], # Blue
        3: ['#00FF00', 1.0], # Green
        4: ['#FFFF00', 1.0], # Yellow
        5: ['#FFA500', 1.0], # Orange
        6: ['#800080', 1.0], # Purple
        7: ['#FFC0CB', 1.0], # Pink
        8: ['#00FFFF', 1.0], # Cyan
        9: ['#FF00FF', 1.0]  # Magenta
    }

    # --- 1. Digital Ball Construction ---
    print("--- Generating Digital Balls ---")
    solid_ball_coords = generate_digital_ball_coordinates(center=(10.0, 10.0, 10.0), radius=8.0, inner_radius=0.0)
    print(f"Generated {len(solid_ball_coords)} voxels for the solid ball.")
    add_coordinates_to_voxelmap_model(model, solid_ball_coords, 1)

    hollow_ball_coords = generate_digital_ball_coordinates(center=(35.0, 10.0, 10.0), radius=8.0, inner_radius=6.0)
    print(f"Generated {len(hollow_ball_coords)} voxels for the hollow ball.")
    add_coordinates_to_voxelmap_model(model, hollow_ball_coords, 2)

    # --- 2. Digital Tube Construction ---
    print("\n--- Generating Digital Tubes ---")
    solid_tube_voxels = generate_digital_tube_voxels(p1=(5, 5, 25), p2=(20, 20, 30), outer_thickness=2.5, inner_thickness=0.0)
    print(f"Generated {len(solid_tube_voxels)} voxels for the solid tube.")
    add_coordinates_to_voxelmap_model(model, solid_tube_voxels, 3) # Placed a bit higher in Z for less overlap

    hollow_tube_voxels = generate_digital_tube_voxels(p1=(25, 5, 25), p2=(40, 20, 30), outer_thickness=3.0, inner_thickness=2.0)
    print(f"Generated {len(hollow_tube_voxels)} voxels for the hollow tube.")
    add_coordinates_to_voxelmap_model(model, hollow_tube_voxels, 4)

    # --- 3. Digital Plane Construction ---
    print("\n--- Generating Digital Planes ---")
    annular_plane_voxels = generate_digital_plane_voxels(
        normal=(1, 1, 1), point_on_plane=(25, 25, 25),
        plane_thickness=1.5, # Made slightly thicker
        outer_radius_in_plane=12.0, inner_radius_in_plane=8.0
    )
    print(f"Generated {len(annular_plane_voxels)} voxels for the annular plane.")
    add_coordinates_to_voxelmap_model(model, annular_plane_voxels, 5)

    # Solid Plane (will span based on extent_for_iteration and then be clipped by model bounds)
    solid_plane_voxels = generate_digital_plane_voxels(
        normal=(0, 0, 1), point_on_plane=(25, 25, 5), # At z=5
        plane_thickness=1.0, outer_radius_in_plane=float('inf'), inner_radius_in_plane=0.0
    )
    print(f"Generated {len(solid_plane_voxels)} voxels for the solid plane (pre-clipping by model).")
    # These coordinates will be numerous but add_coordinates_to_voxelmap_model will clip them to the 50x50x50 grid.
    add_coordinates_to_voxelmap_model(model, solid_plane_voxels, 6)


    punched_plane_voxels = generate_digital_plane_voxels(
        normal=(1, 0, 0), point_on_plane=(5, 25, 25), # At x=5
        plane_thickness=1.0,
        outer_rect_dims=(20.0, 20.0), inner_rect_dims=(10.0, 10.0) # Made larger
    )
    print(f"Generated {len(punched_plane_voxels)} voxels for the rectangular punched plane.")
    add_coordinates_to_voxelmap_model(model, punched_plane_voxels, 7)

    # --- 4. Digital Tetrahedron Construction ---
    print("\n--- Generating Digital Tetrahedrons ---")
    solid_tetra_vertices = [
        (10, 10, 40), (20, 10, 40), (15, 20, 40), (15, 15, 30)
    ]
    solid_tetra_voxels = generate_digital_tetrahedron_voxels(solid_tetra_vertices, inner_offset_factor=0.0)
    print(f"Generated {len(solid_tetra_voxels)} voxels for the solid tetrahedron.")
    add_coordinates_to_voxelmap_model(model, solid_tetra_voxels, 8)

    hollow_tetra_vertices = [
        (30, 10, 40), (40, 10, 40), (35, 20, 40), (35, 15, 30)
    ]
    # Make inner_offset_factor smaller for a thicker shell, e.g. 0.5
    hollow_tetra_voxels = generate_digital_tetrahedron_voxels(hollow_tetra_vertices, inner_offset_factor=0.6)
    print(f"Generated {len(hollow_tetra_voxels)} voxels for the hollow tetrahedron.")
    add_coordinates_to_voxelmap_model(model, hollow_tetra_voxels, 9)

    # --- 5. Digital Cube Construction ---
    print("\n--- Generating Digital Cubes ---")
    center_cube1 = (15, 35, 15) # Adjusted Y to reduce overlap
    side_length_cube1 = 10.0
    rotation_identity = np.eye(3)
    solid_cube_voxels = generate_digital_cube_coordinates(
        center=center_cube1, side_length=side_length_cube1, rotation_matrix=rotation_identity, inner_offset_factor=0.0
    )
    print(f"Generated {len(solid_cube_voxels)} voxels for the solid cube.")
    add_coordinates_to_voxelmap_model(model, solid_cube_voxels, 1)

    center_cube2 = (35, 35, 35)
    side_length_cube2 = 12.0
    inner_factor_cube2 = 0.7 # Thicker shell
    angle_rad_z = math.radians(30) # Adjusted angle
    angle_rad_y = math.radians(20)
    rotation_z = np.array([
        [math.cos(angle_rad_z), -math.sin(angle_rad_z), 0],
        [math.sin(angle_rad_z),  math.cos(angle_rad_z), 0],
        [0, 0, 1]
    ])
    rotation_y = np.array([
        [math.cos(angle_rad_y), 0, math.sin(angle_rad_y)],
        [0, 1, 0],
        [-math.sin(angle_rad_y), 0, math.cos(angle_rad_y)]
    ])
    combined_rotation = rotation_z @ rotation_y

    hollow_cube_voxels = generate_digital_cube_coordinates(
        center=center_cube2, side_length=side_length_cube2, rotation_matrix=combined_rotation, inner_offset_factor=inner_factor_cube2
    )
    print(f"Generated {len(hollow_cube_voxels)} voxels for the hollow cube.")
    add_coordinates_to_voxelmap_model(model, hollow_cube_voxels, 2)


    # --- Visualize All Constructions ---
    print("\nDisplaying voxel constructions using voxelmap...")
    print("A new window should open. Close it to terminate the script.")

    try:
        model.draw(coloring='custom', background_color='w')
        print("\nVoxel constructions display closed.")
    except Exception as e:
        print(f"\nError: Could not display voxelmap model. Ensure you have a compatible display environment (e.g., a graphical desktop) and 'voxelmap' is installed and working.")
        print(f"Details: {e}")

    # --- Demonstrate DGtal DigitalSet usage (for programmatic inspection) ---
    try:
        import dgtal
        if solid_cube_voxels:
            dgtal_solid_cube_set = create_dgtal_digital_set_from_coords(solid_cube_voxels)
            if dgtal_solid_cube_set is not None:
                print(f"\nDGtal DigitalSet for solid cube created with {dgtal_solid_cube_set.size()} points.")
                test_point_coords = (int(center_cube1[0]), int(center_cube1[1]), int(center_cube1[2]))
                # Ensure the point is actually one of the generated voxels for a meaningful True,
                # or pick a voxel known to be in solid_cube_voxels.
                # The center of a voxel cell might be what test_point refers to, while generate_digital_cube_coordinates returns integer voxel indices.
                # Let's test one of the actual generated voxels if the set is not empty.
                if dgtal_solid_cube_set.size() > 0:
                    example_voxel_in_set = next(iter(solid_cube_voxels)) # Get an actual voxel from the list
                    test_point_dgtal = dgtal.kernel.Point3D(example_voxel_in_set[0], example_voxel_in_set[1], example_voxel_in_set[2])
                    print(f"Is voxel {test_point_dgtal} (an actual member) in DGtal solid cube set? {dgtal_solid_cube_set.isInside(test_point_dgtal)}")

                    # Test a point that should be the integer center if the side length is even and it's perfectly centered.
                    # For side_length=10, center=(15,35,15), voxels are [10-19], [30-39], [10-19] approx.
                    # The integer center (15,35,15) should be in the set.
                    center_voxel_dgtal = dgtal.kernel.Point3D(int(center_cube1[0]), int(center_cube1[1]), int(center_cube1[2]))
                    print(f"Is voxel at integer center {center_voxel_dgtal} in DGtal solid cube set? {dgtal_solid_cube_set.isInside(center_voxel_dgtal)}")


    except ImportError:
        print("\nDGtal not found. Skipping DGtal DigitalSet demonstration.")
    except Exception as e:
        print(f"\nError using DGtal: {e}")
        print("This might indicate issues with DGtal's Python bindings or environment.")