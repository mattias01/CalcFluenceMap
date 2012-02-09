import pyopencl as cl
import numpy
import numpy.linalg as la
from OpenCLUtility import OpenCLUtility as oclu

print 'Start PyOpenCLFirstTest'

a = numpy.random.rand(50000).astype(numpy.float32)
b = numpy.random.rand(50000).astype(numpy.float32)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, b.nbytes)

prg = oclu.loadProgram(ctx, "Program1.cl");

prg.sum(queue, a.shape, None, a_buf, b_buf, dest_buf)

a_plus_b = numpy.empty_like(a)
cl.enqueue_copy(queue, a_plus_b, dest_buf)

print 'Result1 (0.0):', la.norm(a_plus_b - (a+b))

a1 = numpy.array([33]).astype(numpy.float32)
a1_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a1)
dest1_buf = cl.Buffer(ctx, mf.WRITE_ONLY, a1.nbytes)

prg.hej(queue, a1.shape, None, a1_buf, dest1_buf)

result = numpy.empty_like(a1)
cl.enqueue_copy(queue, result, dest1_buf)

print 'Result2 (34):', result[0]


