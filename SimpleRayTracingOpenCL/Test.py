import pyopencl as cl
from OpenCLUtility import OpenCLUtility as oclu
from OpenCLTypes import *
from Python.RayTracing import *
from Python.RayTracingTests import *

###################### Test Python ######################

def testPython():
    passed = False
    if testIntersectLineTriangle() and testIntersectLineRectangle() and testIntersectLineDisc():
        passed = True
    else:
        passed = False

    if passed == True:
        print "Python ray-tracing unit tests PASSED"
    else:
        print "Python ray-tracing unit tests FAILED"

###################### Test OpenCl ######################

def testOpenCL(ctx, queue):
    passed = numpy.array([0])
    debugTest = Debug()
    mf = cl.mem_flags
    passed_buf = cl.Buffer(ctx, mf.WRITE_ONLY, passed.nbytes)
    debugTest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, sizeof(debugTest))

    program = oclu.loadProgram(ctx, "OpenCL/RayTracingTests.cl")

    # Test in OpenCL
    program.test(queue, (1,), None, passed_buf, debugTest_buf)
    cl.enqueue_copy(queue, passed, passed_buf).wait()
    cl.enqueue_copy(queue, debugTest, debugTest_buf).wait()

    if numpy.allclose(passed, numpy.array([1])):
        print "OpenCL ray-tracing unit tests PASSED"
    else:
        print "OpenCL ray-tracing unit tests FAILED"