
#include "Collimator.h"

// Intersection calculations
void intersectLineFlatCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t1, LEAF_ASQ const Triangle *t2, bool *intersect, float *distance, float4 *ip) {
	intersectLineTriangle(l, t1, intersect, distance, ip);
	if (!(*intersect)) { // Try to find intersection in second triangle
		intersectLineTriangle(l, t2, intersect, distance, ip);
	}
}

void intersectLineBBoxCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp) {
	intersectLineBBoxInOutColLeaf(l, b, intersect, inDistance, outDistance, inIp, outIp);
}

void intersectLineBoxCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp) {
	intersectLineBoxInOut(l, b, intersect, inDistance, outDistance, inIp, outIp);
}

