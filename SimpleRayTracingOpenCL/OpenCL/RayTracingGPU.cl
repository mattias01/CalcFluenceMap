#include "OpenCL/PrimitivesGPU.cl"
#include "OpenCL/CollimatorGPU.cl"
#include "OpenCL/Misc.cl"
#include "OpenCL/Settings.cl"

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
	int numberOfCollimators;
#if SOA == 0
	Collimator collimators[NUMBER_OF_COLLIMATORS];
#elif SOA == 1
	Collimator collimators;
#endif
	FluenceMap fluenceMap;
} __attribute((packed)) Scene;

typedef struct Render {
	int flx, fly;
	float xstep, ystep, xoffset, yoffset;
	int lsamples;
	float lstep;
	//int mode;
} __attribute((packed)) Render;

// Intersections

void intersectSimpleRaySourceDisc(RAY_ASQ const Line *l, __constant const SimpleRaySourceDisc *rs, bool *intersect, float *distance, float4 *ip) {
	Disc d = rs->disc; // Copy from constant memory to private
	intersectLineDisc(l, &d, intersect, distance, ip);
}

// Ray tracing

void firstHitLeaf(__constant const Scene *s, __constant const Render *render, RAY_ASQ const Line *r, LEAF_ASQ const float4 *leaf_data, int *collimatorIndex, bool *intersect, float4 *ip, float *thickness, __global Debug *debug) {
	*intersect = false;
	float minDistance = MAXFLOAT;
#if SOA == 0
	for (int i = 0; i < s->collimators[*collimatorIndex].numberOfLeaves; i++) {
#elif SOA == 1
	for (int i = 0; i < s->collimators.numberOfLeaves[*collimatorIndex]; i++) {
#endif
		bool intersectTmp;
		float distanceTmp;
		float4 ipTmp;
		float thicknessTmp;
		#if MODE == 0
			#if SOA == 0
				intersectLineFlatCollimatorLeaf(r, &(leaf_data[s->collimators[*collimatorIndex].flatCollimator.leafArrayOffset + i*s->collimators[*collimatorIndex].flatCollimator.leafArrayStride]), &(leaf_data[s->collimators[*collimatorIndex].flatCollimator.leafArrayOffset + i*s->collimators[*collimatorIndex].flatCollimator.leafArrayStride + 3]), &intersectTmp, &distanceTmp, &ipTmp);
				thicknessTmp = s->collimators[*collimatorIndex].height;
			#elif SOA == 1
				//intersectLineFlatCollimatorLeaf(r, &(leaf_data[s->collimators.flatCollimator.leafArrayOffset[*collimatorIndex] + i*s->collimators.flatCollimator.leafArrayStride[*collimatorIndex]]), &(leaf_data[s->collimators.flatCollimator.leafArrayOffset[*collimatorIndex] + i*s->collimators.flatCollimator.leafArrayStride[*collimatorIndex] + 3]), &intersectTmp, &distanceTmp, &ipTmp);
				intersectLineFlatCollimatorLeaf(r, &(leaf_data[i*s->collimators.flatCollimator.leafArrayStride[*collimatorIndex]]), &(leaf_data[i*s->collimators.flatCollimator.leafArrayStride[*collimatorIndex] + 3]), &intersectTmp, &distanceTmp, &ipTmp);
				thicknessTmp = s->collimators.height[*collimatorIndex];
			#endif
		#elif MODE == 1
			float4 ipInTmp;
			float distanceOutTmp;
			#if SOA == 0
				intersectLineBBoxCollimatorLeaf(r, &(leaf_data[s->collimators[*collimatorIndex].bboxCollimator.leafArrayOffset + i*s->collimators[*collimatorIndex].bboxCollimator.leafArrayStride]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
			#elif SOA == 1
				//intersectLineBBoxCollimatorLeaf(r, &(leaf_data[s->collimators.bboxCollimator.leafArrayOffset[*collimatorIndex] + i*s->collimators.bboxCollimator.leafArrayStride[*collimatorIndex]]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
				intersectLineBBoxCollimatorLeaf(r, &(leaf_data[i*s->collimators.bboxCollimator.leafArrayStride[*collimatorIndex]]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
			#endif
			thicknessTmp = distanceOutTmp - distanceTmp;
		#elif MODE == 2
			float4 ipInTmp;
			float distanceOutTmp;
			#if SOA == 0
				intersectLineBoxCollimatorLeaf(r, &(leaf_data[s->collimators[*collimatorIndex].boxCollimator.leafArrayOffset + i*s->collimators[*collimatorIndex].boxCollimator.leafArrayStride]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
			#elif SOA == 1
				//intersectLineBoxCollimatorLeaf(r, &(leaf_data[s->collimators.boxCollimator.leafArrayOffset[*collimatorIndex] + i*s->collimators.boxCollimator.leafArrayStride[*collimatorIndex]]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
				intersectLineBoxCollimatorLeaf(r, &(leaf_data[i*s->collimators.boxCollimator.leafArrayStride[*collimatorIndex]]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
			#endif
			thicknessTmp = distanceOutTmp - distanceTmp;
		#endif

		if (intersectTmp && (distanceTmp < minDistance)) {
			minDistance = distanceTmp;
			*intersect = true;
			*ip = ipTmp;
			*thickness = thicknessTmp;
		}
	}
}

void firstHitCollimator(__constant const Scene *s, __constant const Render *render, RAY_ASQ Line *r, __global const float4 *leaf_data, bool *intersect, float4 *ip, float *intensityCoeff, __global Debug *debug) {
	*intersect = false;
	float minDistance = MAXFLOAT;
	*intensityCoeff = 1;
	int collimatorIndex = -1;
	for (int i = 0; i < s->numberOfCollimators; i++) { // Find closest collimator
		bool intersectTmp;
		float distanceTmpIn;
		float distanceTmpOut;
		float4 ipTmpCollimatorBBIn;
		float4 ipTmpCollimatorBBOut;
		#if MODE == 0
			#if SOA == 0
				intersectLineBBoxInOut(r, &(s->collimators[i].flatCollimator.boundingBox), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
			#elif SOA == 1
				intersectLineBBoxInOut(r, &(s->collimators.flatCollimator.boundingBox[i]), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
			#endif
		#elif MODE == 1
			#if SOA == 0
				intersectLineBBoxInOut(r, &(s->collimators[i].bboxCollimator.boundingBox), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
			#elif SOA == 1
				intersectLineBBoxInOut(r, &(s->collimators.bboxCollimator.boundingBox[i]), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
			#endif
		#elif MODE == 2
			#if SOA == 0
				intersectLineBBoxInOut(r, &(s->collimators[i].boxCollimator.boundingBox), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
			#elif SOA == 1
				intersectLineBBoxInOut(r, &(s->collimators.boxCollimator.boundingBox[i]), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
			#endif
		#endif

		if (intersectTmp && (distanceTmpIn < minDistance)) {
			collimatorIndex = i;
			minDistance = distanceTmpIn;
			*intersect = true;
			*ip = ipTmpCollimatorBBOut;

			//bool intersectTmp;
			float4 ipTmpLeaf;
			float thickness;

			#if LEAF_AS == 0
			#elif LEAF_AS == 1
				#if MODE == 0
					__local float4 col_leaf_data[NUMBER_OF_LEAVES * 2 * 3]; // Make sure it's >= than the leaf data.
					for (int j = 0; j < s->collimators.flatCollimator.numberOfLeaves[collimatorIndex] * s->collimators.flatCollimator.leafArrayStride[collimatorIndex]; j++) {
						col_leaf_data[j] = leaf_data[s->collimators.flatCollimator.leafArrayOffset[collimatorIndex] + j];
					}
					barrier(CLK_LOCAL_MEM_FENCE);
				#elif MODE == 1
					__local float4 col_leaf_data[NUMBER_OF_LEAVES * 2]; // Make sure it's >= than the leaf data.
					for (int j = 0; j < s->collimators.bboxCollimator.numberOfLeaves[collimatorIndex] * s->collimators.bboxCollimator.leafArrayStride[collimatorIndex]; j++) {
						col_leaf_data[j] = leaf_data[s->collimators.bboxCollimator.leafArrayOffset[collimatorIndex] + j];
					}
					barrier(CLK_LOCAL_MEM_FENCE);
				#elif MODE == 2
					__local float4 col_leaf_data[NUMBER_OF_LEAVES * 12 * 3]; // Make sure it's >= than the leaf data.
					for (int j = 0; j < s->collimators.boxCollimator.numberOfLeaves[collimatorIndex] * s->collimators.boxCollimator.leafArrayStride[collimatorIndex]; j++) {
						col_leaf_data[j] = leaf_data[s->collimators.boxCollimator.leafArrayOffset[collimatorIndex] + j];
					}
					barrier(CLK_LOCAL_MEM_FENCE);
				#endif
			#elif LEAF_AS == 3
				#if MODE == 0
					__global float4 *col_leaf_data = &leaf_data[s->collimators.flatCollimator.leafArrayOffset[collimatorIndex]];
				#elif MODE == 1
					__global float4 *col_leaf_data = &leaf_data[s->collimators.bboxCollimator.leafArrayOffset[collimatorIndex]];
				#elif MODE == 2
					__global float4 *col_leaf_data = &leaf_data[s->collimators.boxCollimator.leafArrayOffset[collimatorIndex]];
				#endif
			#endif

			firstHitLeaf(s, render, r, col_leaf_data, &collimatorIndex, &intersectTmp, &ipTmpLeaf, &thickness, debug);
			#if SOA == 0
				float absorptionCoeff = s->collimators[collimatorIndex].absorptionCoeff;
			#elif SOA == 1
				float absorptionCoeff = s->collimators.absorptionCoeff[collimatorIndex];
			#endif
			while (intersectTmp) {
				*intersect = true;
				*intensityCoeff *= exp(-absorptionCoeff*thickness);
				#if MODE == 0
					// One leaf hit. Continue ray after collimator because leaves don't have thickness.
					intersectTmp = false;
					*ip = ipTmpLeaf;
				#elif MODE == 1 || MODE == 2
					// One ray can hit several leaves.
					*ip = ipTmpLeaf;
					r->origin = ipTmpLeaf;
					firstHitLeaf(s, render, r, col_leaf_data, &collimatorIndex, &intersectTmp, &ipTmpLeaf, &thickness, debug);
				#endif
			}
		}
	}
	
	/*if (collimatorIndex != -1) { // Check leaves on closest Collimator.
		bool intersectTmp;
		float4 ipTmpLeaf;
		float thickness;
		firstHitLeaf(s, render, r, leaf_data, &collimatorIndex, &intersectTmp, &ipTmpLeaf, &thickness, debug);
		#if SOA == 0
			float absorptionCoeff = s->collimators[collimatorIndex].absorptionCoeff;
		#elif SOA == 1
			float absorptionCoeff = s->collimators.absorptionCoeff[collimatorIndex];
		#endif
		while (intersectTmp) {
			*intersect = true;
			*intensityCoeff *= exp(-absorptionCoeff*thickness);
			#if MODE == 0
				// One leaf hit. Continue ray after collimator because leaves don't have thickness.
				intersectTmp = false;
				*ip = ipTmpLeaf;
			#elif MODE == 1 || MODE == 2
				// One ray can hit several leaves.
				*ip = ipTmpLeaf;
				r->origin = ipTmpLeaf;
				firstHitLeaf(s, render, r, leaf_data, &collimatorIndex, &intersectTmp, &ipTmpLeaf, &thickness, debug);
			#endif
		}
	}*/
}

void traceRay(__constant const Scene *s, __constant const Render *render, RAY_ASQ Line *r, __global const float4 *leaf_data, float *i, __global Debug *debug) {
	float intensity = 1;
	bool intersectCollimator;
	float4 ipCollimator;
	float intensityCoeff;
	firstHitCollimator(s, render, r, leaf_data, &intersectCollimator, &ipCollimator, &intensityCoeff, debug);
	while (intersectCollimator) {
		intensity *= intensityCoeff;
		if (intensity < INTENSITY_THRESHOLD) { // If intensity is below a treshhold, don't bother to cast more rays. Return 0 intensity.
			*i = 0;
			return;
		}
		else {
			r->origin = ipCollimator; // Create a new ray. Same direction but new origin.
			firstHitCollimator(s, render, r, leaf_data, &intersectCollimator, &ipCollimator, &intensityCoeff, debug);
		}
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

// Gives vectors from the ray origin to left, right, bottom, top of the ray source.
void lightSourceAreaVectors(__constant const Scene *scene, const float4 *rayOrigin, float4 *vi0, float4 *vi1, float4 *vj0, float4 *vj1, __global Debug *debug) {
	*vi0 = (float4) (scene->raySource.disc.origin.x - scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.y, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;

	*vi1 = (float4) (scene->raySource.disc.origin.x + scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.y, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;

	*vj0 = (float4) (scene->raySource.disc.origin.x, 
					 scene->raySource.disc.origin.y - scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;

	*vj1 = (float4) (scene->raySource.disc.origin.x, 
					 scene->raySource.disc.origin.y + scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;
}

/*// Integration over the light source is done as if the rays where cast from a pixel straight under the origin of the light source. The sampling is uniform only from that point.
void flatLightSourceSampling(__constant const Scene *scene, __constant const Render *render, __global const Collimator collimators[NUMBER_OF_COLLIMATORS], const float4 *rayOrigin, float *fluenceSum, __global Debug *debug) {
	for (int li = 0; li < render->lsamples; li++) {
		for (int lj = 0; lj < render->lsamples; lj++) {
			float4 lPoint =  (float4) (scene->raySource.disc.origin.x - scene->raySource.disc.radius + li*render->lstep, 
									   scene->raySource.disc.origin.y - scene->raySource.disc.radius + lj*render->lstep, 
                                       scene->raySource.disc.origin.z,
                                       scene->raySource.disc.origin.w);
			float4 rayDirection = lPoint - *rayOrigin;

			Line ray = {
				.origin = *rayOrigin, 
				.direction = normalize(rayDirection)};

			float intensity;
			traceRay(scene, render, &ray, collimators, &intensity, debug);
			
			*fluenceSum += intensity; // Add intensity from ray
		}
	}
}*/

// Integration is done in a uniform way over the light source. The sampling is uniform from every point. This contains errors!
/*void uniformLightSourceSampling(__constant const Scene *scene, __constant const Render *render, __global const Collimator *collimators, const float4 *rayOrigin, float *fluenceSum, __global Debug *debug) {
	float4 lvi0, lvi1, lvj0, lvj1;
	lightSourceAreaVectors(scene, rayOrigin, &lvi0, &lvi1, &lvj0, &lvj1, debug);

	float4 vi0, vi1, vj0, vj1; // 0 is the closest vector
	if (length(lvi0) < length(lvi1)) { // Find the closest i vector.
		vi0 = lvi0;
		vi1 = lvi1;
	}
	else {
		vi0 = lvi1;
		vi1 = lvi0;
	}
	if (length(lvj0) < length(lvj1)) { // Find the closest j vector.
		vj0 = lvj0;
		vj1 = lvj1;
	}
	else {
		vj0 = lvj1;
		vj1 = lvj0;
	}
	vi1 = length(vi0)*normalize(vi1); // vx1 is now of same length as vx0 which creates a plane that we cast rays on to get an uniform sampling.
	vj1 = length(vj0)*normalize(vj1);
	float4 idir = (*rayOrigin + vi1) - (*rayOrigin + vi0);
	float4 jdir = (*rayOrigin + vj1) - (*rayOrigin + vj0);
	float istep = length(idir)/(render->lsamples-1);
	float jstep = length(jdir)/(render->lsamples-1);
	
	float4 corner = (*rayOrigin + vi0) - normalize(jdir)*length(jdir)/2;

	for (int li = 0; li < render->lsamples; li++) {
		for (int lj = 0; lj < render->lsamples; lj++) {
			float4 lPoint =  corner + li*istep*idir + lj*jstep*jdir;
			float4 rayDirection = lPoint - *rayOrigin;

			Line ray = {
				.origin = *rayOrigin, 
				.direction = normalize(rayDirection)};

			float intensity;
			traceRay(scene, render, &ray, collimators, &intensity, debug);
			
			*fluenceSum += intensity; // Add intensity from ray
		}
	}
}*/

/*void initCollimators(__constant const Scene *scene, __constant const Render *render, __constant const Collimator collimators[NUMBER_OF_COLLIMATORS], Collimator *collimators_new) {
	// First copy all properties
	for (int i = 0; i < scene->collimators; i++) {
		collimators_new[i].boundingBox = collimators[i].boundingBox;
		collimators_new[i].position = collimators[i].position;
		collimators_new[i].xdir = collimators[i].xdir;
		collimators_new[i].ydir = collimators[i].ydir;
		collimators_new[i].absorptionCoeff = collimators[i].absorptionCoeff;
		collimators_new[i].numberOfLeaves = collimators[i].numberOfLeaves;
		for (int l = 0; l < collimators[i].numberOfLeaves; l++) {
			collimators_new[i].leafPositions[l] = collimators[i].leafPositions[l];
		}
	}
	// Copy simplified model according to mode.
	#if MODE == 0
		for (int i = 0; i < scene->collimators; i++) {
			FlatCollimator flatCollimator;
			Collimator col = collimators[i]; // Copy from constant to private memory.
			createFlatCollimator(&col, &flatCollimator);
			collimators_new[i].flatCollimator = flatCollimator;
		}
	#endif
}*/

// Integration over the light source is done as if the rays where cast from a pixel straight under the origin of the light source. The sampling is uniform only from that point.
__kernel void flatLightSourceSampling(__constant const Scene *scene, __constant const Render *render, __global const float4 *leaf_data, __global float *intensity_map, __global Debug *debug) {
	int i = get_global_id(0);
	int j = get_global_id(1);
	int k = get_global_id(2);
	int li = (k/render->lsamples);
	int lj = (k%render->lsamples);

#if RAY_AS == 0
	float4 rayOrigin = (float4) (scene->fluenceMap.rectangle.p0.x + i*render->xstep + render->xoffset, 
								 scene->fluenceMap.rectangle.p0.y + j*render->ystep + render->yoffset, 
								 scene->fluenceMap.rectangle.p0.z, 0);
	float4 lPoint =  (float4) (scene->raySource.disc.origin.x - scene->raySource.disc.radius + li*render->lstep, 
							   scene->raySource.disc.origin.y - scene->raySource.disc.radius + lj*render->lstep, 
                               scene->raySource.disc.origin.z, 0);
	float4 rayDirection = normalize(lPoint - rayOrigin);
	
	Line ray = {
		.origin = rayOrigin,
		.direction = rayDirection};
#elif RAY_AS == 1
	int x = get_local_id(0);
	int y = get_local_id(1);
	int z = get_local_id(2);

	__local Line ray[WG_LIGHT_SAMPLING_SIZE];
	ray[x + y*WG_LIGHT_SAMPLING_X + z*WG_LIGHT_SAMPLING_X*WG_LIGHT_SAMPLING_Y].origin = (float4) (scene->fluenceMap.rectangle.p0.x + i*render->xstep + render->xoffset, scene->fluenceMap.rectangle.p0.y + j*render->ystep + render->yoffset, scene->fluenceMap.rectangle.p0.z, 0);
	ray[x + y*WG_LIGHT_SAMPLING_X + z*WG_LIGHT_SAMPLING_X*WG_LIGHT_SAMPLING_Y].direction = normalize(((float4)(scene->raySource.disc.origin.x - scene->raySource.disc.radius + li*render->lstep, scene->raySource.disc.origin.y - scene->raySource.disc.radius + lj*render->lstep, scene->raySource.disc.origin.z, 0)) - ((float4)(scene->fluenceMap.rectangle.p0.x + i*render->xstep + render->xoffset, scene->fluenceMap.rectangle.p0.y + j*render->ystep + render->yoffset, scene->fluenceMap.rectangle.p0.z, 0)));
#endif //LOCAL_RAYS
 
	float intensity;
#if RAY_AS == 0
	traceRay(scene, render, &ray, leaf_data, &intensity, debug);
#elif RAY_AS == 1
	traceRay(scene, render, &(ray[x + y*WG_LIGHT_SAMPLING_X + z*WG_LIGHT_SAMPLING_X*WG_LIGHT_SAMPLING_Y]), leaf_data, &intensity, debug);
#endif //RAY_AS
					
	//intensity_map[j + i*render->fly + k*render->flx*render->fly] = intensity; // Add intensity from ray
	//intensity_map[get_global_id(1) + get_global_id(0)*render->fly + get_global_id(2)*render->flx*render->fly] = intensity; // Add intensity from ray. Use get_global_id() to let the compiler spare some registers.
	intensity_map[get_global_id(1) + get_global_id(0)*FLY + get_global_id(2)*FLX*FLY] = intensity; // Add intensity from ray. Use get_global_id() to let the compiler spare some registers.
}

__kernel void calculateIntensityDecreaseWithDistance(__constant const Scene *scene, __constant const Render *render, __global float *distanceFactors, __global Debug *debug) {
	float4 vi0, vi1, vj0, vj1;

	int i = get_global_id(0);
	int j = get_global_id(1);

	float4 rayOrigin = (float4) (scene->fluenceMap.rectangle.p0.x + i*render->xstep + render->xoffset, 
								 scene->fluenceMap.rectangle.p0.y + j*render->ystep + render->yoffset, 
								 scene->fluenceMap.rectangle.p0.z, 0);

	lightSourceAreaVectors(scene, &rayOrigin, &vi0, &vi1, &vj0, &vj1, debug);
	float anglei = acos(dot(normalize(vi0), normalize(vi1)));
    float anglej = acos(dot(normalize(vj0), normalize(vj1)));

	distanceFactors[j+i*render->fly] = anglei*anglej/M_PI_F*2; // The ratio of a unit half sphere that are covering the light source. => Things that are further away recieves less photons.
}

__kernel void calcFluenceElement(__constant const Scene *scene, __constant const Render *render, __global float *intensity_map, __global float *fluence_data, __global Debug *debug){
	unsigned int i = get_global_id(0);
    unsigned int j = get_global_id(1);

	float fluenceSum;
	for (int k = 0; k < render->lsamples*render->lsamples; k++) {
		fluenceSum += intensity_map[j + i*render->fly + k*render->flx*render->fly];
	}
	
	fluence_data[j+i*render->fly] *= fluenceSum; // Assumes fluence element already contains distance factor.
}

/*__kernel void drawScene(__constant const Scene *scene, __constant const Render *render, __global float *fluence_data, __global const Collimator collimators[NUMBER_OF_COLLIMATORS], __global Debug *debug)
{
	//unsigned int i = get_global_id(0);
    //unsigned int j = get_global_id(1);

	calcFluenceElement(scene, render, collimators, fluence_data, debug);
}*/