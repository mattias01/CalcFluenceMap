// Default settings if a setting is not coming as copiler arguments.

#ifndef NUMBER_OF_LEAVES
#define NUMBER_OF_LEAVES 40
#endif //NUMBEROFLEAVES

#ifndef EPSILON
#define EPSILON 0.0000001f
#endif //EPSILON

#ifndef INTENSITY_THRESHOLD
#define INTENSITY_THRESHOLD 0.0000001f
#endif //INTENSITY_THRESHOLD

#ifndef FLX
#define FLX 16
#endif //FLX

#ifndef FLY
#define FLY 16
#endif //FLY

#ifndef LSAMPLES
#define LSAMPLES 5
#endif //LSAMPLES

#ifndef LSAMPLESSQR
#define LSAMPLESSQR LSAMPLES*LSAMPLES
#endif //LSAMPLESSQR

#ifndef MODE
#define MODE 2
#endif //MODE

#ifndef NUMBER_OF_COLLIMATORS
#define NUMBER_OF_COLLIMATORS 1
#endif //NUMBER_OF_COLLIMATORS

#ifndef LINE_TRIANGLE_INTERSECTION_ALGORITHM
#define LINE_TRIANGLE_INTERSECTION_ALGORITHM 1
#endif //LINE_TRIANGLE_INTERSECTION_ALGORITHM

//#ifndef WG_LIGHT_SAMPLING_X
//#define WG_LIGHT_SAMPLING_X 1
//#endif //WG_LIGHT_SAMPLING_X

//#ifndef WG_LIGHT_SAMPLING_Y
//#define WG_LIGHT_SAMPLING_Y 1
//#endif //WG_LIGHT_SAMPLING_Y

//#ifndef WG_LIGHT_SAMPLING_Z
//#define WG_LIGHT_SAMPLING_Z 1
//#endif //WG_LIGHT_SAMPLING_Z

//#ifndef WG_LIGHT_SAMPLING_SIZE
//#define WG_LIGHT_SAMPLING_SIZE WG_LIGHT_SAMPLING_X * WG_LIGHT_SAMPLING_Y * WG_LIGHT_SAMPLING_Z
//#endif //WG_LIGHT_SAMPLING_SIZE

#ifndef RAY_AS
#define RAY_AS 0
#endif

#if RAY_AS == 0
	#define RAY_ASQ __private
#elif RAY_AS == 1
	#define RAY_ASQ __local
#elif RAY_AS == 2 // Does not work
	#define RAY_ASQ __constant
#elif RAY_AS == 3
	#define RAY_ASQ __global
#endif

#ifndef LEAF_AS
#define LEAF_AS 1
#endif

#if LEAF_AS == 0
	#define LEAF_ASQ __private
#elif LEAF_AS == 1
	#define LEAF_ASQ __local
#elif LEAF_AS == 2 // No support
	#define LEAF_ASQ __constant
#elif LEAF_AS == 3
	#define LEAF_ASQ __global
#endif

#ifndef SCENE_AS
#define SCENE_AS 2
#endif

#if SCENE_AS == 0 // No support
	#define SCENE_ASQ __private const
#elif SCENE_AS == 1 // No support
	#define SCENE_ASQ __local const
#elif SCENE_AS == 2
	#define SCENE_ASQ __constant
#elif SCENE_AS == 3
	#define SCENE_ASQ __global const
#endif

#ifndef STRUCTURE
#define STRUCTURE 0
#endif
