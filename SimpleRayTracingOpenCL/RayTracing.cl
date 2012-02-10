// Data types
typedef struct Line {
	float4 origin;
	float4 direction;
} __attribute__((packed)) Line;

typedef struct Plane {
	float4 origin;
	float4 normal;
} __attribute__((packed)) Plane;

typedef struct Triangle {
	float4 p0;
	float4 p1;
	float4 p2;
} __attribute__((packed)) Triangle;

typedef struct Square {
	float4 p0;
	float4 p1;
	float4 p2;
	float4 p3;
} __attribute__((packed)) Square;

typedef struct Disc {
	float4 origin;
	float4 normal;
	float radius;
} __attribute__((packed)) Disc;

typedef struct SimpleRaySourceSquare {
	Square square;
} __attribute__((packed)) SimpleRaySourceSquare;

typedef struct SimpleRaySourceDisc {
	Disc disc;
} __attribute__((packed)) SimpleRaySourceDisc;

typedef struct SimpleCollimator {
	Square leftSquare;
	Square rightSquare;
} __attribute__((packed)) SimpleCollimator;

typedef struct FluenceMap {
	Square square;
} __attribute__((packed)) FluenceMap;

typedef struct Scene {
	SimpleRaySourceDisc raySource;
	SimpleCollimator collimator;
	FluenceMap fluenceMap;
} __attribute((packed)) Scene;

typedef struct Render {
	int flx, fly;
	float xstep, ystep, xoffset, yoffset;
	int lsamples;
	float lstep;
} __attribute((packed)) Render;

typedef struct Debug {
	int i0, i1, i2, i3, i4, i5;
	float f0, f1, f2, f3, f4, f5;
	float4 v0, v1, v2, v3, v4, v5;
} __attribute((packed)) Debug;

// Intersections

void intersectLinePlane(const Line *l, const Plane *p, bool *intersect, float4 *ip)
{
	if (dot(l->direction, p->normal) == 0.0f) {
		*intersect = false; // Parallel -> does not intersect.
	}
	else {
		float t = (dot(p->normal, (p->origin - l->origin))) / (dot(p->normal, l->direction));
		*ip = l->origin + l->direction*t;
		*intersect = true;
	}
}

void intersectLineTriangle(const Line *l, const Triangle *t, bool *intersect, float4 *ip)
{
	float4 u = t->p1 - t->p0;
    float4 v = t->p2 - t->p0;
    float4 triangleNorm = cross(u, v);
	Plane p = {
		.origin = t->p0,
		.normal = triangleNorm};
	bool intersection;
    float4 intersectionPoint;
	intersectLinePlane(l, &p, &intersection, &intersectionPoint);

	if (intersection) {
		// Point in triangle plan. Check if in triangle
        float uu = dot(u,u);
        float uv = dot(u,v);
        float vv = dot(v,v);
        float4 w = intersectionPoint - t->p0;
        float wu = dot(w,u);
        float wv = dot(w,v);
        float D = uv * uv - uu * vv;
        // Get and test parametric coords
        float s = (uv * wv - vv * wu) / D;
        if (s < 0.0f || s > 1.0f) { // IntersectionPoint is outside triangle
            *intersect = false;
			return;
		}
        float t = (uv * wu - uu * wv) / D;
        if (t < 0.0 || (s + t) > 1.0) { // IntersectionPoint is outside triangle
            *intersect = false;
			return;
		}
		// IntersectionPoint is in triangle
		*intersect = true;
        *ip = intersectionPoint; 
	}
	else {
		*intersect = false;
	}
}

void intersectLineSquare(const Line *l, const Square *s, bool *intersect, float4 *ip)
{
	Triangle t1 = {
		.p0 = s->p0,
		.p1 = s->p1,
		.p2 = s->p2};
	Triangle t2 = {
		.p0 = s->p2,
		.p1 = s->p3,
		.p2 = s->p0};

	float4 intersectionPoint;
	bool intersection;
	intersectLineTriangle(l,&t1,&intersection,&intersectionPoint);

	if (!intersection) { // Try to find intersection in second triangle
		intersectLineTriangle(l,&t2,&intersection,&intersectionPoint);
	}
	*ip = intersectionPoint;
	*intersect = intersection;
}

void intersectLineDisc(const Line *l, const Disc *d, bool *intersect, float4 *ip)
{
	Plane p = {
		.origin = d->origin,
		.normal = d->normal};
	float4 intersectionPoint;
	bool intersection;
	intersectLinePlane(l,&p,&intersection,&intersectionPoint);

	if (intersection){
		float4 D = d->origin - intersectionPoint;
		if (dot(D,D) <= d->radius*d->radius) {
			*intersect = true;
			*ip = intersectionPoint;
		}
		else {
			*intersect = false;
		}
	}
	else {
		*intersect = false;
	}
}

void intersectSimpleCollimator(const Line *l, __constant const SimpleCollimator *c, bool *intersect, float4 *ip)
{
	float4 intersectionPoint;
	bool intersection;
	Square ls = c->leftSquare; // Copy from constant memory to private
	intersectLineSquare(l,&ls,&intersection,&intersectionPoint);

	if (!intersection) {
		Square rs = c->rightSquare; // Copy from constant memory to private
		intersectLineSquare(l,&rs,&intersection,&intersectionPoint);
	}
	*ip = intersectionPoint;
	*intersect = intersection;
}

void intersectSimpleRaySourceSquare(const Line *l, __constant const SimpleRaySourceSquare *rs, bool *intersect, float4 *ip) {
	float4 intersectionPoint;
	bool intersection;
	Square s = rs->square; // Copy from constant memory to private
	intersectLineSquare(l,&s,&intersection,&intersectionPoint);

	*ip = intersectionPoint;
	*intersect = intersection;
}

void intersectSimpleRaySourceDisc(const Line *l, __constant const SimpleRaySourceDisc *rs, bool *intersect, float4 *ip) {
	float4 intersectionPoint;
	bool intersection;
	Disc d = rs->disc; // Copy from constant memory to private
	intersectLineDisc(l,&d,&intersection,&intersectionPoint);

	*ip = intersectionPoint;
	*intersect = intersection;
}

// Ray tracing

void traceRay(__constant const Scene *s, const Line *r, float *i) {
	float4 intersectionPointCollimator;
	bool intersectCollimator;
	intersectSimpleCollimator(r,&(s->collimator),&intersectCollimator,&intersectionPointCollimator);
	if (intersectCollimator) {
		*i = 0;
	}
	else {
		float4 intersectionPointRaySource;
		bool intersectRaySource;
		intersectSimpleRaySourceDisc(r,&(s->raySource),&intersectRaySource,&intersectionPointRaySource);
		if (intersectRaySource) {
			*i = 1;
		}
		else {
			*i = 0; // To infinity
		}
	}
}

void calculateFluenceElementLightStraightUp(__constant const Scene *scene, __constant const Render *render, __global float *fluence_data, __global Debug *debug){
	unsigned int i = get_global_id(0);
    unsigned int j = get_global_id(1);

	Line ray = {
		.origin = (float4) ((scene->fluenceMap.square.p0.x + i*render->xstep + render->xoffset), (scene->fluenceMap.square.p0.y + j*render->ystep + render->yoffset), 0, 0), 
		.direction = (float4) (0,0,1,0)};
	
	float intensity;
	traceRay(scene, &ray, &intensity);
	fluence_data[i*render->flx+j] = intensity;
}

void calcFluenceElementLightAllAngles(__constant const Scene *scene, __constant const Render *render, __global float *fluence_data, __global Debug *debug){
	unsigned int i = get_global_id(0);
    unsigned int j = get_global_id(1);

	float4 rayOrigin = (float4) (scene->fluenceMap.square.p0.x + i*render->xstep + render->xoffset, 
								 scene->fluenceMap.square.p0.y + j*render->ystep + render->yoffset, 
								 scene->fluenceMap.square.p0.z, 0);

	float4 v0 = (float4) (scene->raySource.disc.origin.x - scene->raySource.disc.radius, 
						  scene->raySource.disc.origin.y - scene->raySource.disc.radius, 
                          scene->raySource.disc.origin.z,
                          scene->raySource.disc.origin.w) - rayOrigin;
    float4 vi = (float4) (v0.x + scene->raySource.disc.radius*2, v0.y, v0.z, v0.w) - rayOrigin;
    float4 vj = (float4) (v0.x, v0.y + scene->raySource.disc.radius*2, v0.z, v0.w) - rayOrigin;
	float anglei = acos(dot(normalize(v0),normalize(vi)));
    float anglej = acos(dot(normalize(v0),normalize(vj)));
	float ratio = anglei*anglej/M_PI_F*2; // The ratio of a half sphere that are covering the light source. => Things that are further away recieves less photons.

	float fluenceSum = 0;
	for (int li = 0; li < render->lsamples; li++) {
		for (int lj = 0; lj < render->lsamples; lj++) {
			float4 lPoint =  (float4) (scene->raySource.disc.origin.x - scene->raySource.disc.radius + li*render->lstep, 
									   scene->raySource.disc.origin.y - scene->raySource.disc.radius + lj*render->lstep, 
                                       scene->raySource.disc.origin.z,
                                       scene->raySource.disc.origin.w);
			float4 rayDirection = lPoint - rayOrigin;

			Line ray = {
				.origin = rayOrigin, 
				.direction = normalize(rayDirection)};

			float intensity;
			traceRay(scene, &ray, &intensity);
			
			fluenceSum += intensity*ratio; // Add intensity from ray
		}
	}

	fluence_data[i*render->flx+j] = fluenceSum;
}

__kernel void drawScene(__constant const Scene *scene, __constant const Render *render, __global float *fluence_data, __global Debug *debug)
{
	//unsigned int i = get_global_id(0);
    //unsigned int j = get_global_id(1);

	calculateFluenceElementLightStraightUp(scene, render, fluence_data, debug);
}

__kernel void drawScene2(__constant const Scene *scene, __constant const Render *render, __global float *fluence_data, __global Debug *debug)
{
	//unsigned int i = get_global_id(0);
    //unsigned int j = get_global_id(1);

	calcFluenceElementLightAllAngles(scene, render, fluence_data, debug);
}