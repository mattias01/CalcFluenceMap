#include "OpenCL/Collimator.cl"
#include "OpenCL/Misc.cl"
#include "OpenCL/Primitives.cl"

// Data types
typedef struct SimpleRaySourceRectangle {
	Rectangle rectangle;
} __attribute__((packed)) SimpleRaySourceRectangle;

typedef struct SimpleRaySourceDisc {
	Disc disc;
} __attribute__((packed)) SimpleRaySourceDisc;

typedef struct FluenceMap {
	Rectangle rectangle;
} __attribute__((packed)) FluenceMap;

typedef struct Scene {
	SimpleRaySourceDisc raySource;
	SimpleCollimator collimator;
	FluenceMap fluenceMap;
} __attribute((packed)) Scene;

typedef struct Scene2 {
	SimpleRaySourceDisc raySource;
	int collimators;
	FluenceMap fluenceMap;
} __attribute((packed)) Scene2;

typedef struct Render {
	int flx, fly;
	float xstep, ystep, xoffset, yoffset;
	int lsamples;
	float lstep;
	int mode;
} __attribute((packed)) Render;

// Intersections

void intersectSimpleRaySourceRectangle(const Line *l, __constant const SimpleRaySourceRectangle *rs, bool *intersect, float *distance, float4 *ip) {
	Rectangle s = rs->rectangle; // Copy from constant memory to private
	intersectLineRectangle(l, &s, intersect, distance, ip);
}

void intersectSimpleRaySourceDisc(const Line *l, __constant const SimpleRaySourceDisc *rs, bool *intersect, float *distance, float4 *ip) {
	Disc d = rs->disc; // Copy from constant memory to private
	intersectLineDisc(l, &d, intersect, distance, ip);
}

// Ray tracing

void firstHitCollimator(__constant const Scene2 *s, __constant const Render *render, const Line *r, const Collimator *collimators, bool *intersect, float *distance, float4 *ip, float *attenuation, __global Debug *debug) {
	*intersect = false;
	float minDistance = MAXFLOAT;
	*ip = (NAN, NAN, NAN, NAN);
	for (int i = 0; i < s->collimators; i++) {
		bool intersectTmp;
		float distanceTmp;
		float4 ipTmp;
		//intersectSimpleCollimator(r, &(collimators[i]), &intersectTmp, &distanceTmp, &ipTmp);
		if (render->mode == 0) {
			FlatCollimator fc = collimators[i].flatCollimator;
			intersectLineFlatCollimator(r, &fc, &intersectTmp, &distanceTmp, &ipTmp);
			*attenuation = fc.attenuation;
		}

		if (intersectTmp && (distanceTmp < minDistance)) {
			minDistance = distanceTmp;
            *intersect = true;
            *ip = ipTmp;
            //*attenuation = collimators[i].attenuation;
		}
	}
}

void traceRayFirstHit(__constant const Scene2 *s, __constant const Render *render, const Line *r, const Collimator *collimators, float *i, __global Debug *debug) {
	float intensity = 1;
	bool intersectCollimator = true;
	float distanceCollimator;
	float4 ipCollimator;
	float attenuation;
	firstHitCollimator(s, render, r, collimators, &intersectCollimator, &distanceCollimator, &ipCollimator, &attenuation, debug);
	while (intersectCollimator) {
		intensity = intensity * attenuation;
		Line newRay = {
			.origin = ipCollimator+r->direction*0.0000000001, // Cast a new ray just after the collimator. TODO: Figure out good offset value.
			.direction = r->direction};
		firstHitCollimator(s, render, &newRay, collimators, &intersectCollimator, &distanceCollimator, &ipCollimator, &attenuation, debug);
	}

	bool intersectRaySource;
	float distanceRaySource;
	float4 ipRaySource;
	intersectSimpleRaySourceDisc(r, &(s->raySource), &intersectRaySource, &distanceRaySource, &ipRaySource);
	if (intersectRaySource) {
		*i = intensity;
	}
	else {
		*i = 0; // To infinity
	}
}

void traceRay(__constant const Scene *s, const Line *r, float *i) {
	bool intersectCollimator;
	float distanceCollimator;
	float4 ipCollimator;
	intersectSimpleCollimator(r, &(s->collimator), &intersectCollimator, &distanceCollimator, &ipCollimator);
	if (intersectCollimator) {
		*i = 0;
	}
	else {
		bool intersectRaySource;
		float distanceRaySource;
		float4 ipRaySource;
		intersectSimpleRaySourceDisc(r, &(s->raySource), &intersectRaySource, &distanceRaySource, &ipRaySource);
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
		.origin = (float4) (scene->fluenceMap.rectangle.p0.x + i*render->xstep + render->xoffset, 
							scene->fluenceMap.rectangle.p0.y + j*render->ystep + render->yoffset, 
							scene->fluenceMap.rectangle.p0.z, 0), 
		.direction = (float4) (0,0,1,0)};
	
	float intensity;
	traceRay(scene, &ray, &intensity);
	fluence_data[i*render->flx+j] = intensity;
}

void calcFluenceElementLightAllAngles(__constant const Scene2 *scene, __constant const Render *render, const Collimator *collimators, __global float *fluence_data, __global Debug *debug){
	unsigned int i = get_global_id(0);
    unsigned int j = get_global_id(1);

	float4 rayOrigin = (float4) (scene->fluenceMap.rectangle.p0.x + i*render->xstep + render->xoffset, 
								 scene->fluenceMap.rectangle.p0.y + j*render->ystep + render->yoffset, 
								 scene->fluenceMap.rectangle.p0.z, 0);

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
			traceRayFirstHit(scene, render, &ray, collimators, &intensity, debug);
			//traceRay(scene, &ray, &intensity);
			
			fluenceSum += intensity*ratio; // Add intensity from ray
		}
	}

	fluence_data[i*render->flx+j] = fluenceSum;
}

void initCollimators(__constant const Scene2 *scene, __constant const Render *render, __global const Collimator *collimators, Collimator *collimators_new) {
	// First copy all properties
	for (int i = 0; i < scene->collimators; i++) {
		collimators_new[i].boundingBox = collimators[i].boundingBox;
		collimators_new[i].position = collimators[i].position;
		collimators_new[i].xdir = collimators[i].xdir;
		collimators_new[i].ydir = collimators[i].ydir;
		collimators_new[i].attenuation = collimators[i].attenuation;
		collimators_new[i].numberOfLeaves = collimators[i].numberOfLeaves;
		for (int l = 0; l < collimators[i].numberOfLeaves; l++) {
			collimators_new[i].leafPositions[l] = collimators[i].leafPositions[l];
		}
	}
	// Copy simplified model according to mode.
	if (render->mode == 0) { 
		for (int i = 0; i < scene->collimators; i++) {
			FlatCollimator flatCollimator;
			Collimator col = collimators[i]; // Copy from constant to private memory.
			createFlatCollimator(&col, &flatCollimator);
			collimators_new[i].flatCollimator = flatCollimator;
		}
	}
}

__kernel void drawScene(__constant const Scene *scene, __constant const Render *render, __global float *fluence_data, __global Debug *debug)
{
	//unsigned int i = get_global_id(0);
    //unsigned int j = get_global_id(1);

	calculateFluenceElementLightStraightUp(scene, render, fluence_data, debug);
}

__kernel void drawScene2(__constant const Scene2 *scene, __constant const Render *render, __global float *fluence_data, __global const Collimator *collimators, __global Debug *debug)
{
	//unsigned int i = get_global_id(0);
    //unsigned int j = get_global_id(1);
	
	Collimator collimators_new[2];
	collimators_new[0] = collimators[0];
	collimators_new[1] = collimators[1];
	//Collimator collimators_new[2];
	//if (i < 30 && j < 30) {
		//initCollimators(scene, render, collimators, (Collimator *) collimators_new);
	//}
	//barrier(CLK_LOCAL_MEM_FENCE && CLK_GLOBAL_MEM_FENCE);

	/*if (i == 0) {
		debug->v0 = collimators_new[0].flatCollimator.position;
		debug->v1 = collimators_new[1].flatCollimator.leaves[1].p3;
	}*/

	calcFluenceElementLightAllAngles(scene, render, collimators_new, fluence_data, debug);
}