#include "RayTracing.cl"

// Tests

void testIntersectLinePlane(int *passed)
{
	Line l = {
		.origin = (float4) (1.0f,1.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Plane p = {
		.origin = (float4) (0.0f,0.0f,0.0f,0.0f),
		.normal = (float4) (0.0f,0.0f,1.0f,0.0f)};

	float4 p0;
	bool intersection;
	intersectLinePlane(&l,&p,&intersection,&p0);

	if (all(p0 == ((float4) (1.0f,1.0f,0.0f,0.0f)))) {
		*passed = 1;
	}
	else {
		*passed = 0;
	}
}

void testIntersectLineTriangle(int *passed, __global Debug *debug)
{
	Line l1 = {
		.origin = (float4) (1.0f,1.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Line l2 = {
		.origin = (float4) (-1.0f,-1.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Triangle t = {
		.p0 = (float4) (0.0f,0.0f,0.0f,0.0f),
		.p1 = (float4) (3.0f,0.0f,0.0f,0.0f),
		.p2 = (float4) (0.0f,3.0f,0.0f,0.0f)};

	float4 p0;
	float4 p1;
	bool intersection1;
	bool intersection2;
	intersectLineTriangle(&l1,&t,&intersection1,&p0);
	intersectLineTriangle(&l2,&t,&intersection2,&p1);

	debug->f0 = intersection1;
	debug->f1 = intersection2;
	debug->f2 = all(p0 == ((float4) (1.0f,1.0f,0.0f,0.0f)));
	debug->v0 = p0;
	debug->v1 = p1;

	if (all(p0 == ((float4) (1.0f,1.0f,0.0f,0.0f))) &&
		intersection1 == true && 
		intersection2 == false)
	{
		*passed = 1;
	}
	else {
		*passed = 0;
	}
}

void testIntersectLineSquare(int *passed, __global Debug *debug)
{
	Line l1 = { // Intersects first triangle
		.origin = (float4) (1.0f,1.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Line l2 = { // Intersects second triangle
		.origin = (float4) (2.0f,2.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Line l3 = { // Does not intersect
		.origin = (float4) (-2.0f,-2.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Square s = {
		.p0 = (float4) (0.0f,0.0f,0.0f,0.0f),
		.p1 = (float4) (3.0f,0.0f,0.0f,0.0f),
		.p2 = (float4) (3.0f,3.0f,0.0f,0.0f),
		.p3 = (float4) (0.0f,3.0f,0.0f,0.0f)};

	float4 p0;
	float4 p1;
	float4 p2;
	bool intersection1;
	bool intersection2;
	bool intersection3;
	intersectLineSquare(&l1,&s,&intersection1,&p0);
	intersectLineSquare(&l2,&s,&intersection2,&p1);
	intersectLineSquare(&l3,&s,&intersection3,&p2);

	debug->f0 = intersection1;
	debug->f1 = intersection2;
	debug->f2 = intersection3;
	debug->f3 = all(p0 == ((float4) (1.0f,1.0f,0.0f,0.0f)));
	debug->f4 = all(p1 == ((float4) (2.0f,2.0f,0.0f,0.0f)));
	debug->v0 = p0;
	debug->v1 = p1;
	debug->v2 = p2;

	if (all(p0 == ((float4) (1.0f,1.0f,0.0f,0.0f))) &&
		all(p1 == ((float4) (2.0f,2.0f,0.0f,0.0f))) && 
		intersection1 == true &&
		intersection2 == true &&
		intersection3 == false )
	{
		*passed = 1;
	}
	else {
		*passed = 0;
	}
}

void testIntersectLineDisc(int *passed, __global Debug *debug)
{
	Line l1 = { // Intersects disc
		.origin = (float4) (1.0f,1.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Line l2 = { // Does not intersect
		.origin = (float4) (3.0f,3.0f,0.0f,0.0f),
		.direction = (float4) (0.0f,0.0f,1.0f,0.0f)};
	Disc d = {
		.origin = (float4) (0.0f,0.0f,0.0f,0.0f),
		.normal = (float4) (0.0f,0.0f,1.0f,0.0f),
		.radius = 2.0f};

	float4 p0;
	float4 p1;
	bool intersection1;
	bool intersection2;
	intersectLineDisc(&l1,&d,&intersection1,&p0);
	intersectLineDisc(&l2,&d,&intersection2,&p1);

	debug->f0 = intersection1;
	debug->f1 = intersection2;
	debug->f2 = all(p0 == ((float4) (1.0f,1.0f,0.0f,0.0f)));
	debug->v0 = p0;
	debug->v1 = p1;

	if (all(p0 == ((float4) (1.0f,1.0f,0.0f,0.0f))) &&
		intersection1 == true &&
		intersection2 == false) {
		*passed = 1;
	}
	else {
		*passed = 0;
	}
}

/*void testTraceRay(int *passed, __global Debug *debug) Does not work. Scene not in __constant.
{
	Disc rsd = {
		.origin = (float4) (3.5,3.5,6,0),
		.normal = (float4) (0,0,1,0),
		.radius = (float) 3};
	SimpleRaySourceDisc rs = {
		.disc = rsd};
	Square cls = {
		.p0 = (float4) (0,0,3,0),
		.p1 = (float4) (7,0,3,0),
		.p2 = (float4) (7,3,3,0),
		.p3 = (float4) (0,3,3,0)};
	Square crs = {
		.p0 = (float4) (0,4,3,0),
		.p1 = (float4) (7,4,3,0),
		.p2 = (float4) (7,7,3,0),
		.p3 = (float4) (0,7,3,0)};
	SimpleCollimator cm = {
		.leftSquare = cls,
		.rightSquare = crs};
	Square flss = {
		.p0 = (float4) (0,0,0,0),
		.p1 = (float4) (7,0,0,0),
		.p2 = (float4) (7,7,0,0),
		.p3 = (float4) (0,7,0,0)};
	FluencySquare fs = {
		.square = flss};
	Scene source = {
		.raySource = rs,
		.collimator = cm,
		.fluencySquare = fs};
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

	testIntersectLinePlane(&passedTmp);
	if (passedTmp == 0) {
		*passed = 0; return;
	}

	testIntersectLineTriangle(&passedTmp, debug);
	if (passedTmp == 0) {
		*passed = 0; return;
	}

	testIntersectLineSquare(&passedTmp, debug);
	if (passedTmp == 0) {
		*passed = 0; return;
	}

	testIntersectLineDisc(&passedTmp, debug);
	if (passedTmp == 0) {
		*passed = 0; return;
	}

	//testTraceRay(&passedTmp, debug);
	if (passedTmp == 0) {
		*passed = 0; return;
	}
					
	*passed = 1; // Return result
}