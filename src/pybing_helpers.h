#define DEBUG_PYBING 0

#if DEBUG_PYBING
    #define printDBG(msg) std::cout << "[pybing.c] " << msg << std::endl;
    #define write(msg) std::cout << msg;
#else
    #define printDBG(msg);
#endif
