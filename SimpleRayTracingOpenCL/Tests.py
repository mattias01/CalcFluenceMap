import pyopencl as cl
from OpenCLUtility import OpenCLUtility as oclu
from OpenCLTypes import *
from RayTracing import *

###################### Tests Python ######################
def testIntersectLineTriangle():
    l = Line(float4(1,1,0,0), float4(0,0,1,0))
    t = Triangle(float4(0,0,0,0), float4(3,0,0,0), float4(0,3,0,0))
    i = intersectLineTriangle(l,t)
    if i == float4(1.0,1.0,0.0,0.0):
        return True
    else:
        print "intersectLineTriangle FAILED"
        return False

def testIntersectLineSquare():
    l1 = Line(float4(1,1,0,0), float4(0,0,1,0))
    l2 = Line(float4(2,2,0,0), float4(0,0,1,0))
    s = Square(float4(0,0,0,0), float4(3,0,0,0), float4(0,3,0,0), float4(3,3,0,0))
    i1 = intersectLineSquare(l1,s)
    i2 = intersectLineSquare(l2,s)
    if (i1 == float4(1,1,0,0)) and (i2 == float4(2,2,0,0)):
        return True
    else:
        print "intersectLineSquare FAILED"
        return False

def testIntersectLineDisc():
    l1 = Line(float4(1,1,0,0), float4(0,0,1,0))
    l2 = Line(float4(3,3,0,0), float4(0,0,1,0))
    d = Disc(float4(0,0,0,0), float4(0,0,1,0), 2)
    i1 = intersectLineDisc(l1,d)
    i2 = intersectLineDisc(l2,d)
    if (i1 == float4(1,1,0,0) and i2 == None):
        return True
    else:
        print "intersectLineSquare FAILED"
        return False

def testPython():
    passed = False
    if testIntersectLineTriangle() and testIntersectLineSquare() and testIntersectLineDisc():
        passed = True
    else:
        passed = False

    if passed == True:
        print "Python ray-tracing unit tests PASSED"
    else:
        print "Python ray-tracing unit tests FAILED"

###################### Tests OpenCl ######################

def testOpenCL(ctx, queue):
    passed = numpy.array([0])
    debugTest = Debug()
    mf = cl.mem_flags
    passed_buf = cl.Buffer(ctx, mf.WRITE_ONLY, passed.nbytes)
    debugTest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, sizeof(debugTest))

    program = oclu.loadProgram(ctx, "RayTracingTests.cl")

    # Test in OpenCL
    program.test(queue, (1,), None, passed_buf, debugTest_buf)
    cl.enqueue_copy(queue, passed, passed_buf).wait()
    cl.enqueue_copy(queue, debugTest, debugTest_buf).wait()

    if numpy.allclose(passed, numpy.array([1])):
        print "OpenCL ray-tracing unit tests PASSED"
    else:
        print "OpenCL ray-tracing unit tests FAILED"