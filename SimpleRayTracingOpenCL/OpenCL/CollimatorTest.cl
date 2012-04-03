#ifndef __CollimatorTest__
#define __CollimatorTest__

#include "Collimator.h"
#include "Primitives.h"

void testCreateFlatCollimator(int *passed) {
    Collimator collimator = {
		.boundingBox = (BBox) {
			.min = (float4) (-3.5,-3.5,-91,0),
			.max = (float4) (3.5,-2.5,-90,0)},
		.position = (float4) (-3.5,-3.5,-90,0),
		.xdir = (float4) (0,1,0,0),
		.ydir = (float4) (1,0,0,0),
		.absorptionCoeff = 0.5,
		.height = 1,
		.leafWidth = 3.5,
		.numberOfLeaves = 2,
		.leafPositions = {0.5, 1}};

	FlatCollimator fc;
    createFlatCollimator(&collimator, &fc);
    if (all(fc.leaves[0].p0 == (float4) (-3.5,-3.5,-90,0)) &&
		all(fc.leaves[1].p2 == (float4) (3.5,-2.5,-90,0))) {
		*passed = 1;
	}
    else {
        *passed = 0;
	}
}

void testCollimator(int *passed, __global Debug *debug)
{
	int passedTmp = 0; // init to false

	testCreateFlatCollimator(&passedTmp);
	if (passedTmp == 0) {
		*passed = 0; return;
	}

	*passed = 1;
}

#endif // __CollimatorTest__