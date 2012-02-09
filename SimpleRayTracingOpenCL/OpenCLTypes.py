from ctypes import *
from math import sqrt

class float4(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float),
                ("w", c_float)]

    # Methods for Python. Vector operations already defined in OpenCL.
    def __add__(self, other):
        return float4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        return float4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, other):
        if type(other) == type(self):
            return float4(self.x * other.x, self.y * other.y, self.z * other.z, self.w * other.w)
        elif type(other) == float:
            return float4(self.x * other, self.y * other, self.z * other, self.w * other)
        else: #Undefined
            return None

    def __div__(self, other):
        if type(other) == type(self):
            return float4(self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w)
        elif type(other) == float:
            return float4(self.x / other, self.y / other, self.z / other, self.w / other)
        else: #Undefined
            return None

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z and self.w == other.w:
            return True
        else:
            return False

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + "," + str(self.w) + ")"

def dot(v1, v2):
    return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z + v1.w*v2.w

def cross(v1, v2):
    x = v1.y*v2.z - v1.z*v2.y;
    y = v1.z*v2.x - v1.x*v2.z;
    z = v1.x*v2.y - v1.y*v2.x;
    return float4(x,y,z,0.0) # w component is 0.0. Same as in OpenCL.

def length(v):
    return sqrt(v.x*v.x + v.y*v.y + v.z*v.z + v.w*v.w)

def normalize(v):
    return v/length(v)


