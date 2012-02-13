import pyopencl as cl
import numpy
import numpy.linalg as la
from time import time
from OpenCLUtility import OpenCLUtility as oclu
import RayTracing as rt
from matplotlib import pyplot as plt

print 'Start PyOpenCLThirdTestSimpleRayTracing'

# Run tests
rt.test()

#ctx = cl.create_some_context()
#queue = cl.CommandQueue(ctx)

# Build scene objects
rs = rt.SimpleRaySource(rt.Rectangle(numpy.array([0,3,6]), numpy.array([7,3,6]), numpy.array([7,5,6]), numpy.array([0,5,6])))
cls = rt.Rectangle(numpy.array([0,0,3]), numpy.array([7,0,3]), numpy.array([7,3,3]), numpy.array([0,3,3]))
crs = rt.Rectangle(numpy.array([0,4,3]), numpy.array([6,4,3]), numpy.array([7,7,3]), numpy.array([0,7,3]))
cm = rt.SimpleCollimator(cls, crs)
fs = rt.FluencySquare(rt.Rectangle(numpy.array([0,0,0]), numpy.array([7,0,0]), numpy.array([7,7,0]), numpy.array([0,7,0])))
scene = rt.Scene(rs,cm, fs)

# Settings
flx = 128
fly = 128

# Run in Python
time1 = time()
fluency_data = rt.drawScene(scene, flx, fly)
timePython = time()-time1

samplesPerSecondPython = flx*fly/timePython
print "Time Python: ", timePython, " Samples per second: ", samplesPerSecondPython

plt.imshow(fluency_data, interpolation='none')
plt.show()

#resultOpenCL = numpy.empty_like(fl.fluency)
#resultPython = numpy.empty_like(fl.fluency)

#mf = cl.mem_flags
#rs_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=rs)
#cm_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cm)
#flline_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=fl.line)
#resultOpenCL_buf = cl.Buffer(ctx, mf.WRITE_ONLY, resultOpenCL.nbytes)

#program = oclu.loadProgram(ctx, "Program1.cl")

# Run in OpenCL
#time1 = time()
#program.calculate(queue, a.shape, None, a_buf, b_buf, resultOpenCL_buf)
#cl.enqueue_copy(queue, resultOpenCL, resultOpenCL_buf).wait()
#timeOpenCL = time()-time1

# Run in Python
#time1 = time()

#timePython = time()-time1

# Check if result is the same
#if resultOpenCL.data == resultPython.data:
#    print("Results OK")
#else:
#    print("Results doesn't match!!")

#print "OpenCL:", timeOpenCL, " Python:", timePython
