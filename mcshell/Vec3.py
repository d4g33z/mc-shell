import numpy as np

class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        try:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
        except (ValueError, TypeError):
            print(f"Warning: Invalid input for Vec3({x}, {y}, {z}). Defaulting to (0,0,0).")
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0

    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"

    # --- NEW METHODS FOR VECTOR ARITHMETIC ---

    def __add__(self, other):
        """Vector addition: self + other"""
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented

    def __sub__(self, other):
        """Vector subtraction: self - other"""
        if isinstance(other, Vec3):
            return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented

    def __mul__(self, scalar):
        """Scalar multiplication: self * scalar"""
        try:
            s = float(scalar)
            return Vec3(self.x * s, self.y * s, self.z * s)
        except (ValueError, TypeError):
            return NotImplemented

    def __rmul__(self, scalar):
        """Reflected scalar multiplication: scalar * self"""
        return self.__mul__(scalar)

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def to_tuple(self):
        return self.x,self.y,self.z

    def dot(self, other):
        """Dot product of two vectors"""
        if isinstance(other, Vec3):
            return self.x * other.x + self.y * other.y + self.z * other.z
        raise TypeError("Dot product requires another Vec3 instance.")

    def cross(self, other):
        """Cross product of two vectors"""
        # TODO: this type check is failing due to the redefinition of Vec3 in mcshell.Vec (somehow)
        if isinstance(other, Vec3):
            # Using numpy for the cross product calculation is clean and reliable
            # np.cross will be available because we import numpy at the top
            cross_product = np.cross([self.x, self.y, self.z], [other.x, other.y, other.z])
            return Vec3(cross_product[0], cross_product[1], cross_product[2])
        raise TypeError("Cross product requires another Vec3 instance.")