#include "OpenCL/Misc.cl"
#include "OpenCL/CollimatorTest.cl"
#include "OpenCL/PrimitivesTest.cl"

// Tests

/*void testTraceRay(int *passed, __global Debug *debug) Does not work. Scene not in __constant.
{
	Disc rsd = {
		.origin = (float4) (3.5,3.5,6,0),
		.normal = (float4) (0,0,1,0),
		.radius = (float) 3};
	SimpleRaySourceDisc rs = {
		.disc = rsd};
	Rectangle cls = {
		.p0 = (float4) (0,0,3,0),
		.p1 = (float4) (7,0,3,0),
		.p2 = (float4) (7,3,3,0),
		.p3 = (float4) (0,3,3,0)};
	Rectangle crs = {
		.p0 = (float4) (0,4,3,0),
		.p1 = (float4) (7,4,3,0),
		.p2 = (float4) (7,7,3,0),
		.p3 = (float4) (0,7,3,0)};
	SimpleCollimator cm = {
		.leftRectangle = cls,
		.rightRectangle = crs};
	Rectangle flss = {
		.p0 = (float4) (0,0,0,0),
		.p1 = (float4) (7,0,0,0),
		.p2 = (float4) (7,7,0,0),
		.p3 = (float4) (0,7,0,0)};
	FluencyRectangle fs = {
		.rectangle = flss};
	Scene source = {
		.raySource = rs,
		.collimator = cm,
		.fluencyRectangle = fs};
	Line l1 = {
		.origin = (float4) (1.0f,1.0f,0.0f,0),
		.direction = (float4) (0.0f,0.0f,1.0f,0)};
	Line l2 = {
		.origin = (float4) (3.5f,3.5f,0.0f,0),
		.direction = (float4) (0.0f,0.0f,1.0f,0)};
	float intensity1 = 0.0f;
	float intensity2 = 0.0f;
	traceRay(&scene,&l1,&intensity1);
	traceRay(&scene,&l2,&intensity2);

	debug->f0 = intensity1;
	debug->f1 = intensity2;

	if (intensity1 == 0.0f && intensity2 == 1.0f) {
		*passed = 1;
	}
	else {
		*passed = 0;
	}
}*/

__kernel void test(__global int *passed, __global Debug *debug)
{
	int passedTmp = 0; // init to false

	testPrimitives(&passedTmp, debug);
	if (passedTmp == 0) {
		*passed = 0; return;
	}

	testCollimator(&passedTmp, debug);
	if (passedTmp == 0) {
		*passed = 0; return;
	}
					
	*passed = 1; // Return positive result
}