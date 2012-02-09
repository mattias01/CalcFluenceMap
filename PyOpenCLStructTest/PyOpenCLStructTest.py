import struct
from ctypes import *
import pyopencl as cl
import numpy
from OpenCLUtility import OpenCLUtility as oclu

print('Starting pyOpenCLStructTest')

class Hej:
    def __init__(self, b, c):
        self.b = b
        self.c = c

    def pack(self):
        return struct.pack('=if',self.b,self.c)

class Hej2:
    def __init__(self, b, c):
        self.b = b
        self.c = c

    def pack(self):
        return struct.pack('=4i4f',self.b[0],self.b[1],self.b[2],self.b[3],
                                   self.c[0],self.c[1],self.c[2],self.c[3])

class Child(Structure):
    _fields_ = [("x", c_int),
                ("y", c_int)]

class Parent(Structure):
    _fields_ = [("c", Child),
                ("z", c_int)]

a = Hej(8,9).pack()

x = numpy.array([1,2,3,4])
y = numpy.array([4.0,5.0,6.0,7.0])
a2 = Hej2(x,y).pack()

a3 = Parent(Child(1,2))

a3.c.x = 2

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

b = numpy.array([0], dtype=numpy.int32)
c = numpy.array([0.0], dtype=numpy.float32)
b2 = numpy.array([0,0,0,0], dtype=numpy.int32)
c2 = numpy.array([0.0,0.0,0.0,0.0], dtype=numpy.float32)
b3 = numpy.array([0], dtype=numpy.int32)

mf = cl.mem_flags
a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
b_buf = cl.Buffer(ctx, mf.WRITE_ONLY, b.nbytes)
c_buf = cl.Buffer(ctx, mf.WRITE_ONLY, c.nbytes)

#a2_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a2)
a2_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a2)
b2_buf = cl.Buffer(ctx, mf.WRITE_ONLY, b2.nbytes)
c2_buf = cl.Buffer(ctx, mf.WRITE_ONLY, c2.nbytes)

a3_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a3)
b3_buf = cl.Buffer(ctx, mf.WRITE_ONLY, b3.nbytes)

program = oclu.loadProgram(ctx, "Program1.cl")
program.test(queue, (1,), None, a_buf, b_buf, c_buf)
cl.enqueue_copy(queue, b, b_buf).wait()
cl.enqueue_copy(queue, c, c_buf).wait()

program.test2(queue, (1,), None, a2_buf, b2_buf, c2_buf)
cl.enqueue_copy(queue, b2, b2_buf).wait()
cl.enqueue_copy(queue, c2, c2_buf).wait()

program.test3(queue, (1,), None, a3_buf, b3_buf)
cl.enqueue_copy(queue, b3, b3_buf).wait()

print "Test1: b:", b, " c:", c
print "Test2: b2:", b2, " c2:", c2
print "Test2: b3:", b3