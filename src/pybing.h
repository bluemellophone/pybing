#ifndef PYBING_DLL_DEFINES_H
	#define PYBING_DLL_DEFINES_H

	#ifdef WIN32
	    #ifndef snprintf
	    	#define snprintf _snprintf
	    #endif
	#endif

	#define PYBING_EXPORT
	
	#ifndef FOO_DLL
	    #ifdef PYBING_EXPORTS
	        #define PYBING_EXPORT __declspec(dllexport)
	    #else
	        //#define DETECTOR_EXPORT __declspec(dllimport)
	    #endif
	#else
		#define PYBING_EXPORT
	#endif
#endif
