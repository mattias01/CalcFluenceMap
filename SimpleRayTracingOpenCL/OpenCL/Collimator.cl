#include "Primitives.cl"

#ifndef __Collimator__
#define __Collimator__

// Data types
typedef struct SimpleCollimator {
	Rectangle leftRectangle;
	Rectangle rightRectangle;
} __attribute__((packed)) SimpleCollimator;

// Intersection calculations
void intersectSimpleCollimator(const Line *l, __constant const SimpleCollimator *c, bool *intersect, float *distance, float4 *ip)
{
	Rectangle ls = c->leftRectangle; // Copy from constant memory to private
	intersectLineRectangle(l, &ls, intersect, distance, ip);

	if (!(*intersect)) { // Check the other rectangle of the SimpleCollimator
		Rectangle rs = c->rightRectangle; // Copy from constant memory to private
		intersectLineRectangle(l, &rs, intersect, distance, ip);
	}
}

#endif //__Collimator__
