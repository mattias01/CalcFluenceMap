
#include "Primitives.h"

// Intersection calculations. Registers: 1.
void intersectLinePlane(RAY_ASQ const Line *l, const Plane *p, bool *intersect)
{
	if (dot(l->direction, p->normal) != 0.0f) { // Not parallel -> intersect.
		*intersect = true;
	}
	else {
		*intersect = false;
	}
}

void intersectLinePlaneAtDistanceWithIP(RAY_ASQ const Line *l, const Plane *p, bool *intersect, float *distance, float4 *ip)
{
	// Init to not intersect
	*intersect = false;
	if (dot(l->direction, p->normal) != 0.0f) { // Not parallel -> intersect.
		*distance = (dot(p->normal, (p->origin - l->origin))) / (dot(p->normal, l->direction));
		if (*distance >= 0.0f) { // Plane is located in positive ray direction from the ray origin. Avoids hitting same thing it just hit.
			*intersect = true;
			*ip = l->origin + l->direction*(*distance);
		}
	}
}

#if LINE_TRIANGLE_INTERSECTION_ALGORITHM == 0 // SoftSurfer, modified MT
// SoftSurfer.com, modified MT. Registers: 32 + 1.
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 u = t->p1 - t->p0;
    float4 v = t->p2 - t->p0;
    float4 triangleNorm = cross(u, v);
	Plane p = {
		.origin = t->p0,
		.normal = triangleNorm};
	intersectLinePlaneAtDistanceWithIP(l, &p, intersect, distance, ip);
	
	if (*intersect) {
		// Point in triangle plan. Check if in triangle
        float uu = dot(u,u);
        float uv = dot(u,v);
        float vv = dot(v,v);
        float4 w = *ip - t->p0;
        float wu = dot(w,u);
        float wv = dot(w,v);
        float D = uv * uv - uu * vv;
        // Get and test parametric coords
        float s = (uv * wv - vv * wu) / D;
        if (s < 0.0f || s > 1.0f) { // IntersectionPoint is outside triangle
            *intersect = false;
		}
		else {
			float t = (uv * wu - uu * wv) / D;
			if (t < 0.0f || (s + t) > 1.0f) { // IntersectionPoint is outside triangle
				*intersect = false;
			}
		}
	}
}

#elif LINE_TRIANGLE_INTERSECTION_ALGORITHM == 1 // Orig. MT
// Möller/Trombore 97. Registers 24.
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 edge1, edge2, tvec, pvec, qvec;
	float det, inv_det;

	// find vectors for two edges sharing t->p0
	edge1 = t->p1 - t->p0;
	edge2 = t->p2 - t->p0;

	// begin calculating determinant - also used to calculate U parameter
	pvec = cross(l->direction, edge2);

	// if determinant is near zero, ray lies in plane of triangle
	det = dot(edge1, pvec);

	if (det > -EPSILON && det < EPSILON) {
		*intersect = false;
		return;
	}
	inv_det = 1.0f / det;

	// calculate distance from t->p0 to ray origin
	tvec = l->origin - t->p0;

	// calculate U parameter and test bounds
	float u = dot(tvec, pvec) * inv_det;
	if (u < 0.0f || u > 1.0f) {
		*intersect = false;
		return;
	}

	// prepare to test V parameter
	qvec = cross(tvec, edge1);

	// calculate V parameter and test bounds
	float v = dot(l->direction, qvec) * inv_det;
	if (v < 0.0f || u + v > 1.0f) {
		*intersect = false;
		return;
	}

	// calculate distance, ray intersects triangle
	///intersect = true;
	*distance = dot(edge2, qvec) * inv_det;
	if (*distance <= 0.0f) {
		*intersect = false;
		return;
	}
	*intersect = true;
	*ip = l->origin + l->direction*(*distance);
}

#elif LINE_TRIANGLE_INTERSECTION_ALGORITHM == 2 // MT2
// code rewritten to do tests on the sign of the determinant
// the division is at the end in the code  
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 edge1, edge2, tvec, pvec, qvec;
	float det;//, inv_det;

	// find vectors for two edges sharing t->p0
	edge1 = t->p1 - t->p0;
	edge2 = t->p2 - t->p0;

	// begin calculating determinant - also used to calculate U parameter
	pvec = cross(l->direction, edge2);

	// if determinant is near zero, ray lies in plane of triangle
	det = dot(edge1, pvec);

	if (det > EPSILON)
	{
		// calculate distance from t->p0 to ray origin
		tvec = l->origin - t->p0;
      
		// calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u < 0.0f || u > det) {
			*intersect = false;
			return;
		}
      
		// prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		// calculate V parameter and test bounds
		float v = dot(l->direction, qvec);
		if (v < 0.0f || u + v > det) {
			*intersect = false;
			return;
		}
	}
	else if(det < -EPSILON)
	{
		// calculate distance from t->p0 to ray origin
		tvec = l->origin - t->p0;
      
		// calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u > 0.0f || u < det) {
			*intersect = false;
			return;
		}
      
		// prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		// calculate V parameter and test bounds
		float v = dot(l->direction, qvec) ;
		if (v > 0.0f || u + v < det) {
			*intersect = false;
			return;
		}
	}
	else {
		*intersect = false;
		return;
	}  // ray is parallell to the plane of the triangle

	//inv_det = 1.0f / det;

	// calculate t, ray intersects triangle
	*distance = dot(edge2, qvec) / det;//* inv_det;
	if (*distance <= 0.0f) {
		*intersect = false;
		return;
	}
	*intersect = true;
	*ip = l->origin + l->direction*(*distance);
}

#elif LINE_TRIANGLE_INTERSECTION_ALGORITHM == 3 // MT3
// code rewritten to do tests on the sign of the determinant
// the division is before the test of the sign of the det
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 edge1, edge2, tvec, pvec, qvec;
	float det, inv_det;

	//find vectors for two edges sharing t->p0
	edge1 = t->p1 - t->p0;
	edge2 = t->p2 - t->p0;

	//begin calculating determinant - also used to calculate U parameter
	pvec = cross(l->direction, edge2);

	//if determinant is near zero, ray lies in plane of triangle
	det = dot(edge1, pvec);

	//calculate distance from t->p0 to ray origin
	tvec = l->origin - t->p0;
	inv_det = 1.0f / det;
   
	if (det > EPSILON)
	{
		//calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u < 0.0f || u > det) {
			*intersect = false;
			return;
		}
      
		//prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		//calculate V parameter and test bounds
		float v = dot(l->direction, qvec);
		if (v < 0.0f || u + v > det) {
			*intersect = false;
			return;
		}
      
	}
	else if(det < -EPSILON)
	{
		//calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u > 0.0f || u < det) {
			*intersect = false;
			return;
		}
      
		//prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		//calculate V parameter and test bounds
		float v = dot(l->direction, qvec);
		if (v > 0.0f || u + v < det) {
			*intersect = false;
			return;
		}
	}
	else {
		*intersect = false;
		return;
	}  //ray is parallell to the plane of the triangle

	//calculate t, ray intersects triangle
	*distance = dot(edge2, qvec) * inv_det;
	if (*distance <= 0.0f) {
		*intersect = false;
		return;
	}
	*intersect = true;
	*ip = l->origin + l->direction*(*distance);
}
#endif // LINE_TRIANGLE_INTERSECTION_ALGORITHM

// Registers: 8 + 33 + 4.
void intersectLineDisc(RAY_ASQ const Line *l, SCENE_ASQ Disc *d, bool *intersect)
//void intersectLineDisc(RAY_ASQ const Line *l, SCENE_ASQ Disc *d, bool *intersect)
{
	Plane p = {
		.origin = d->origin,
		.normal = d->normal};
	float distance;
	float4 ip;

	intersectLinePlaneAtDistanceWithIP(l, &p, intersect, &distance, &ip);

	if (*intersect){
		float4 D = d->origin - ip;
		if (length(D) > d->radius*d->radius) {
			*intersect = false;
		}
	}
}

// Relies on IEEE 754 floating point arithmetic (div by 0 -> inf). Registers: 6.
void intersectLineBBoxAtDistance(RAY_ASQ const Line *l, SCENE_ASQ BBox *bb, bool *intersect, float *distance)
{
#if PLATFORM == 1 || PLATFORM == 2 || PLATFORM == 4 // Hack to make it work on WIN-INTEL-CPU, WIN-AMD-CPU and OSX-CPU.
    BBox bboxA = *bb;
    BBox* b = &bboxA;
#else
    SCENE_ASQ BBox* b = bb;
#endif

	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	float divx = 1.0f / l->direction.x;
	if (divx >= 0.0f) {
        tmin = (b->min.x - l->origin.x) * divx;
        tmax = (b->max.x - l->origin.x) * divx;
	}
    else {
        tmin = (b->max.x - l->origin.x) * divx;
        tmax = (b->min.x - l->origin.x) * divx;
	}
	float divy = 1.0f / l->direction.y;
    if (divy >= 0.0f) {
        tymin = (b->min.y - l->origin.y) * divy;
        tymax = (b->max.y - l->origin.y) * divy;
	}
    else {
        tymin = (b->max.y - l->origin.y) * divy;
        tymax = (b->min.y - l->origin.y) * divy;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
	float divz = 1.0f / l->direction.z;
    if (divz >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) * divz;
        tzmax = (b->max.z - l->origin.z) * divz;
	}
    else {
        tzmin = (b->max.z - l->origin.z) * divz;
        tzmax = (b->min.z - l->origin.z) * divz;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	*intersect = true;
	*distance = tmin;
	// Could give the outgoing distance (tmax) and point here as well.
}

// Relies on IEEE 754 floating point arithmetic (div by 0 -> inf). Registers: 6.
void intersectLineBBox(RAY_ASQ const Line *l, SCENE_ASQ BBox *b, bool *intersect, float *distance, float4 *ip)
{
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	float divx = 1.0f / l->direction.x;
	if (divx >= 0.0f) {
        tmin = (b->min.x - l->origin.x) * divx;
        tmax = (b->max.x - l->origin.x) * divx;
	}
    else {
        tmin = (b->max.x - l->origin.x) * divx;
        tmax = (b->min.x - l->origin.x) * divx;
	}
	float divy = 1.0f / l->direction.y;
    if (divy >= 0.0f) {
        tymin = (b->min.y - l->origin.y) * divy;
        tymax = (b->max.y - l->origin.y) * divy;
	}
    else {
        tymin = (b->max.y - l->origin.y) * divy;
        tymax = (b->min.y - l->origin.y) * divy;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
	float divz = 1.0f / l->direction.z;
    if (divz >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) * divz;
        tzmax = (b->max.z - l->origin.z) * divz;
	}
    else {
        tzmin = (b->max.z - l->origin.z) * divz;
        tzmax = (b->min.z - l->origin.z) * divz;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	if (tmax <= 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}
	*intersect = true;
	*distance = tmin;
	*ip = l->origin + l->direction*tmin;
	// Could give the outgoing distance (tmax) and point here as well.
}

void intersectLineBBoxInOut(RAY_ASQ const Line *l, SCENE_ASQ BBox *bb, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp)
{
#if PLATFORM == 1 || PLATFORM == 2 || PLATFORM == 4 // Hack to make it work on WIN-INTEL-CPU, WIN-AMD-CPU and OSX-CPU.
    BBox bboxA = *bb;
    BBox* b = &bboxA;
#else
    SCENE_ASQ BBox* b = bb;
#endif
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	float divx = 1.0f / l->direction.x;
	if (divx >= 0.0f) {
        tmin = (b->min.x - l->origin.x) * divx;
        tmax = (b->max.x - l->origin.x) * divx;
	}
    else {
        tmin = (b->max.x - l->origin.x) * divx;
        tmax = (b->min.x - l->origin.x) * divx;
	}
	float divy = 1.0f / l->direction.y;
    if (divy >= 0.0f) {
        tymin = (b->min.y - l->origin.y) * divy;
        tymax = (b->max.y - l->origin.y) * divy;
	}
    else {
        tymin = (b->max.y - l->origin.y) * divy;
        tymax = (b->min.y - l->origin.y) * divy;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
	float divz = 1.0f / l->direction.z;
    if (divz >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) * divz;
        tzmax = (b->max.z - l->origin.z) * divz;
	}
    else {
        tzmin = (b->max.z - l->origin.z) * divz;
        tzmax = (b->min.z - l->origin.z) * divz;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	/*if (tmax < 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}*/
	*intersect = true;
	*inDistance = tmin;
	*outDistance = tmax;
	*inIp = l->origin + l->direction*tmin;
	*outIp = l->origin + l->direction*tmax;
}

// Relies on IEEE 754 floating point arithmetic (div by 0 -> inf). Registers: 6.
void intersectLineBBoxColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *distance, float4 *ip)
{
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	float divx = 1.0f / l->direction.x;
	if (divx >= 0.0f) {
        tmin = (b->min.x - l->origin.x) * divx;
        tmax = (b->max.x - l->origin.x) * divx;
	}
    else {
        tmin = (b->max.x - l->origin.x) * divx;
        tmax = (b->min.x - l->origin.x) * divx;
	}
	float divy = 1.0f / l->direction.y;
    if (divy >= 0.0f) {
        tymin = (b->min.y - l->origin.y) * divy;
        tymax = (b->max.y - l->origin.y) * divy;
	}
    else {
        tymin = (b->max.y - l->origin.y) * divy;
        tymax = (b->min.y - l->origin.y) * divy;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
	float divz = 1.0f / l->direction.z;
    if (divz >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) * divz;
        tzmax = (b->max.z - l->origin.z) * divz;
	}
    else {
        tzmin = (b->max.z - l->origin.z) * divz;
        tzmax = (b->min.z - l->origin.z) * divz;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	if (tmax <= 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}
	*intersect = true;
	*distance = tmin;
	*ip = l->origin + l->direction*tmin;
	// Could give the outgoing distance (tmax) and point here as well.
}

// Registers: 6.
void intersectLineBBoxInOutColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp)
{
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	float divx = 1.0f / l->direction.x;
	if (divx >= 0.0f) {
        tmin = (b->min.x - l->origin.x) * divx;
        tmax = (b->max.x - l->origin.x) * divx;
	}
    else {
        tmin = (b->max.x - l->origin.x) * divx;
        tmax = (b->min.x - l->origin.x) * divx;
	}
	float divy = 1.0f / l->direction.y;
    if (divy >= 0.0f) {
        tymin = (b->min.y - l->origin.y) * divy;
        tymax = (b->max.y - l->origin.y) * divy;
	}
    else {
        tymin = (b->max.y - l->origin.y) * divy;
        tymax = (b->min.y - l->origin.y) * divy;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
	float divz = 1.0f / l->direction.z;
    if (divz >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) * divz;
        tzmax = (b->max.z - l->origin.z) * divz;
	}
    else {
        tzmin = (b->max.z - l->origin.z) * divz;
        tzmax = (b->min.z - l->origin.z) * divz;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	if (tmax <= 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}
	*intersect = true;
	*inDistance = tmin;
	*outDistance = tmax;
	*inIp = l->origin + l->direction*tmin;
	*outIp = l->origin + l->direction*tmax;
}

// Registers 7 + 33.
void intersectLineBox(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *distance, float4 *ip) {
	int counter = 0;
	*intersect = false;
	bool intersectTmp;
	float distanceTmp;
	float4 ipTmp;
	for (int i = 0; i < 10/*12*/; i++) {
		intersectLineTriangle(l, &(b->triangles[i]), &intersectTmp, &distanceTmp, &ipTmp);
		if (intersectTmp) {
			if (counter == 0) {
				*distance = distanceTmp;
				*ip = ipTmp;
				counter = counter + 1;
			}
			else {
				if (distanceTmp < *distance - EPSILON) {
					*distance = distanceTmp;
					*ip = ipTmp;
					counter = counter + 1;
				}
				else if (distanceTmp > *distance + EPSILON) {
					counter = counter + 1;
				}
				if (counter == 2) {
					*intersect = true;
					return;
				}
			}
		}
	}
}

// Registers 7 + 33.
void intersectLineBoxInOut(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp) {
	int counter = 0;
	*intersect = false;
	bool intersectTmp;
	float distanceTmp;
	float4 ipTmp;
	for (int i = 0; i < 10/*12*/; i++) {
		intersectLineTriangle(l, &(b->triangles[i]), &intersectTmp, &distanceTmp, &ipTmp);
		if (intersectTmp) {
			if (counter == 0) { // First intersection initializes in and out.
				*inDistance = distanceTmp;
				*inIp = ipTmp;
				*outDistance = distanceTmp;
				*outIp = ipTmp;
				counter = counter + 1;
			}
			else {
				if (distanceTmp < *inDistance - EPSILON) {
					*inDistance = distanceTmp;
					*inIp = ipTmp;
					counter = counter + 1;
				}
				else if (distanceTmp > *outDistance + EPSILON) {
					*outDistance = distanceTmp;
					*outIp = ipTmp;
					counter = counter + 1;
				}
				if (counter == 2) {
					*intersect = true;
					return;
				}
			}
		}
	}
}

