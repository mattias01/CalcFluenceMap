import pyopencl as cl
import numpy
from OpenCLUtility import OpenCLUtility as oclu
from time import time

print 'Start PyOpenCLSecondTest'

problemSize = 20000000

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

a = numpy.array(range(problemSize), dtype=numpy.int32)
b = numpy.array(range(problemSize), dtype=numpy.int32)
resultOpenCL = numpy.empty_like(a)
resultPython = numpy.empty_like(a)

mf = cl.mem_flags
a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
resultOpenCL_buf = cl.Buffer(ctx, mf.WRITE_ONLY, a.nbytes)

program = oclu.loadProgram(ctx, "Program1.cl")

# Run in OpenCL
time1 = time()
program.calculate(queue, a.shape, None, a_buf, b_buf, resultOpenCL_buf)
cl.enqueue_copy(queue, resultOpenCL, resultOpenCL_buf).wait()
timeOpenCL = time()-time1

# Run in Python
time1 = time()
resultPython = a * 2 + b * 2
resultPython += a * 2 + b * 2
resultPython -= a * 3 + b * 3
#for i in range(problemSize):
#    resultPython[i] = a[i] * 2 + b[i] * 2
#    resultPython[i] += a[i] * 2 + b[i] * 2
#    resultPython[i] -= a[i] * 3 + b[i] * 3

timePython = time()-time1

# Check if result is the same
if resultOpenCL.data == resultPython.data:
    print("Results OK")
else:
    print("Results doesn't match!!")

print "OpenCL:", timeOpenCL, " Python:", timePython
