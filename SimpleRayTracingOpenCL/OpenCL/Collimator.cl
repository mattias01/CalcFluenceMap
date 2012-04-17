
#include "Collimator.h"

// Collimator generation
/*void calculateCollimatorBoundingBox(Collimator *collimator, BBox *bbox) {
    float maxPosition = 0;
    for (int i = 0; i < collimator->numberOfLeaves; i++) {
        if (maxPosition < collimator->leafPositions[i]) {
            maxPosition = collimator->leafPositions[i];
		}
	}

    float4 x = normalize(collimator->xdir) * maxPosition;
    float4 y = normalize(collimator->ydir) * collimator->numberOfLeaves * collimator->leafWidth;
    float4 down = normalize(cross(collimator->xdir, collimator->ydir))*collimator->height;

    float4 p0 = collimator->position;
    float4 p1 = p0 + down;
    float4 p2 = p0 + down + y;
    float4 p3 = p0 + y;
    float4 p4 = p0 + x;
    float4 p5 = p4 + down;
    float4 p6 = p4 + down + y;
    float4 p7 = p4 + y;

	BBox box;
	boundingBox(&p0, &p1, &p2, &p3, &p4, &p5, &p6, &p7, &box);
    *bbox = box;
}

void createRectangles(float4 *position, float4 *xdir, float4 *ydir, float *rectangleWidth, int *numberOfRect, float *rectangleLength, Rectangle *rectangles) {
    float4 x = normalize(*xdir);
    float4 y = normalize(*ydir)*(*rectangleWidth);
    for (int i = 0; i < (*numberOfRect); i++) {
		Rectangle rect = {
			.p0 = *position + y*i,
			.p1 = *position + y*(i+1),
			.p2 = *position + x*rectangleLength[i] + y*(i+1),
			.p3 = *position + y*i + x*rectangleLength[i]};
        rectangles[i] = rect;
    }
}*/

/*void createFlatCollimator(Collimator *collimator, FlatCollimator *fc) {
    Plane plane = {
		.origin = collimator->position,
		.normal = cross(collimator->xdir, collimator->ydir)}; // Plane perpendicular to xdir and ydir.
    BBox bbox;
	float4 oldMin = collimator->boundingBox.min;
	float4 oldMax = collimator->boundingBox.max;
	float4 min, max;
	projectPointOntoPlane(&oldMin, &plane, &min);
	projectPointOntoPlane(&oldMax, &plane, &max);
    // Set all properties of the FlatCollimator.
	fc->boundingBox = bbox;
    fc->position = collimator->position;
    fc->xdir = collimator->xdir;
    fc->ydir = collimator->ydir;
    fc->absorptionCoeff = collimator->absorptionCoeff;
    fc->numberOfLeaves = collimator->numberOfLeaves;
	Rectangle leaves[40];
	createRectangles(&(collimator->position), &(collimator->xdir), &(collimator->ydir), &(collimator->leafWidth), &(collimator->numberOfLeaves), (float *) &(collimator->leafPositions), leaves);
	for (int i = 0; i < collimator->numberOfLeaves; i++) {
		fc->leaves[i] = leaves[i];
	}
}*/

// Intersection calculations
void intersectLineFlatCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t1, LEAF_ASQ const Triangle *t2, bool *intersect, float *distance, float4 *ip) {
	//intersectLineRectangle(l, c, intersect, distance, ip);
	
	intersectLineTriangle(l, t1, intersect, distance, ip);
	if (!(*intersect)) { // Try to find intersection in second triangle
		intersectLineTriangle(l, t2, intersect, distance, ip);
	}
}

void intersectLineBBoxCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp) {
	//BBox bbox = *b;
	//intersectLineBBoxInOut(l, &bbox, intersect, inDistance, outDistance, inIp, outIp);
	intersectLineBBoxInOutColLeaf(l, b, intersect, inDistance, outDistance, inIp, outIp);
}

void intersectLineBoxCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp) {
	intersectLineBoxInOut(l, b, intersect, inDistance, outDistance, inIp, outIp);
}

