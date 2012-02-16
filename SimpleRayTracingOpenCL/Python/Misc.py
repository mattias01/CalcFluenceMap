from ctypes import *
from OpenCLTypes import *

class Debug(Structure):
    _fields_ = [("i0", c_int),
                ("i1", c_int),
                ("i2", c_int),
                ("i3", c_int),
                ("i4", c_int),
                ("i5", c_int),
                ("f0", c_float),
                ("f1", c_float),
                ("f2", c_float),
                ("f3", c_float),
                ("f4", c_float),
                ("f5", c_float),
                ("v0", float4),
                ("v1", float4),
                ("v2", float4),
                ("v3", float4),
                ("v4", float4),
                ("v5", float4)]