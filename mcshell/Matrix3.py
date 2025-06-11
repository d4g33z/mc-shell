# This would also be part of the generated Python code or a utility file
import numpy as np # Make sure numpy is available in the student's Python environment
import math

# from pyncraft.minecraft import Vec3
from mcshell.Vec3 import Vec3

class Matrix3:
    def __init__(self, elements=None):
        """
        Initializes a 3x3 matrix.
        Args:
            elements (list of lists or np.ndarray, optional):
                A 3x3 list of lists or a NumPy array.
                Defaults to identity matrix if None.
        """
        if elements is not None:
            self.matrix = np.array(elements, dtype=np.float64)
            if self.matrix.shape != (3, 3):
                raise ValueError("Matrix3 elements must be a 3x3 array or list of lists.")
        else:
            self.matrix = np.identity(3, dtype=np.float64)

    def __repr__(self):
        return f"Matrix3(\n{self.matrix}\n)"

    def __matmul__(self, other):
        """
        Matrix multiplication using the @ operator.
        Supports: Matrix @ Vector -> Vector
                  Matrix @ Matrix -> Matrix
        """
        if isinstance(other, Vec3):
            # Matrix @ Vector -> returns a new transformed Vec3
            result_np = self.matrix @ np.array([other.x, other.y, other.z])
            return Vec3(result_np[0], result_np[1], result_np[2])
        if isinstance(other, Matrix3):
            # Matrix @ Matrix -> returns a new combined Matrix3
            return Matrix3(self.matrix @ other.matrix)
        return NotImplemented

    def to_numpy(self):
        return self.matrix

    @staticmethod
    def from_euler_angles(yaw_degrees, pitch_degrees, roll_degrees):
        """
        Creates a rotation matrix from Euler angles (yaw, pitch, roll) in degrees.
        Order of rotation: Z (yaw), then Y (pitch), then X (roll) - common convention.
        Adjust if your low-level functions expect a different order.
        """
        yaw = math.radians(yaw_degrees)
        pitch = math.radians(pitch_degrees)
        roll = math.radians(roll_degrees)

        # Rotation matrix around Z (Yaw)
        Rz = np.array([
            [math.cos(yaw), -math.sin(yaw), 0],
            [math.sin(yaw), math.cos(yaw), 0],
            [0, 0, 1]
        ])
        # Rotation matrix around Y (Pitch)
        Ry = np.array([
            [math.cos(pitch), 0, math.sin(pitch)],
            [0, 1, 0],
            [-math.sin(pitch), 0, math.cos(pitch)]
        ])
        # Rotation matrix around X (Roll)
        Rx = np.array([
            [1, 0, 0],
            [0, math.cos(roll), -math.sin(roll)],
            [0, math.sin(roll), math.cos(roll)]
        ])
        # Combined rotation: R = Rz * Ry * Rx (or Rx * Ry * Rz depending on convention)
        # Common aerospace/robotics: Yaw (Z), Pitch (Y), Roll (X) -> R = Rz @ Ry @ Rx
        # Game development often uses a different order. Check your library's expectation.
        # Let's assume ZYX order for now.
        return Matrix3(Rz @ Ry @ Rx)

    @staticmethod
    def identity():
        return Matrix3(np.identity(3))

    # You can add matrix multiplication, etc., if needed
    def multiply_vector(self, vec3_instance):
        if not isinstance(vec3_instance, Vec3):
            raise TypeError("Can only multiply Matrix3 by a Vec3 instance.")
        # result_np = self.matrix @ np.array(vec3_instance.to_tuple())
        result_np = self.matrix @ np.array(tuple(vec3_instance))
        return Vec3(result_np[0], result_np[1], result_np[2])