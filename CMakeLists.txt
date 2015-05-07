cmake_minimum_required(VERSION 2.8)

#######################################
# Clang2 = Clang + OpenMP built for OSX Mavericks
# http://goo.gl/1Tg0Zj
if (APPLE)
    message("Detected APPLE system")
    SET(CLANG2 Off)
endif()

if (APPLE AND CLANG2)
	message("Using clang2")
    set(CMAKE_C_COMPILER "clang2")
    set(CMAKE_CXX_COMPILER "clang2++")
endif()


#######################################
project(pybing) #### !!!!IMPORTANT!!!! THIS MUST BE DOWN HERE FOR CLANG2
set(CMAKE_BUILD_TYPE "Release")

if (APPLE)
    #MacPorts
    message("USING MACPORTS")
    include_directories(/opt/local/include)
    link_directories(/opt/local/lib)
endif()

#######################################
message(STATUS "Checking OpenCV")
find_package( OpenCV REQUIRED )
include_directories(${OpenCV_INCLUDE_DIRS})

#######################################
if(APPLE AND CLANG2)    
    # Add flags to support clang2
    message("APPLE + CLANG2: Adding stdlib flags for clang")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
    # set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libstdc++")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -lstdc++ -stdlib=libstdc++")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -lstdc++ -stdlib=libstdc++")
endif()

#######################################
message(STATUS "Checking OpenMP")
find_package( OpenMP )
IF(OPENMP_FOUND)
    message("Found OpenMP! ^_^")
    # add flags for OpenMP
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${OpenMP_C_FLAGS} ${OpenMP_SHARED_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_C_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
ELSE()
    message("Missed OpenMP! x_x")
ENDIF()

#######################################

#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x -ftree-vectorize")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -ftree-vectorize")


add_library(LIBLINEAR  SHARED
    src/LibLinear/linear.cpp 
    src/LibLinear/linear.h 
    src/LibLinear/train.c 
    src/LibLinear/tron.cpp 
    src/LibLinear/tron.h)

target_link_libraries(LIBLINEAR  ${EXTERNAL_LIBS})

add_library(BLAS  SHARED
    src/LibLinear/blas/blas.h 
    src/LibLinear/blas/blasp.h 
    src/LibLinear/blas/daxpy.c 
    src/LibLinear/blas/ddot.c 
    src/LibLinear/blas/dnrm2.c 
    src/LibLinear/blas/dscal.c)

target_link_libraries(BLAS ${EXTERNAL_LIBS})

set(SOURCE_FILES 
    src/main.cpp
    src/CmShow.h
    src/CmShow.cpp
    src/kyheader.h
    src/kyheader.cpp
    src/CmFile.h
    src/CmFile.cpp
    src/CmTimer.h
    src/FilterTIG.h
    src/FilterTIG.cpp
    src/DataSetVOC.cpp
    src/DataSetVOC.h
    src/ImgContrastBB.h
    src/Objectness.cpp
    src/Objectness.h
    src/ValStructVec.h
    src/LibLinear/linear.cpp 
    src/LibLinear/linear.h 
    src/LibLinear/tron.cpp 
    src/LibLinear/tron.h
    src/LibLinear/blas/blas.h 
    src/LibLinear/blas/blasp.h 
    src/LibLinear/blas/daxpy.c 
    src/LibLinear/blas/ddot.c 
    src/LibLinear/blas/dnrm2.c 
    src/LibLinear/blas/dscal.c)

# add_executable(bing 
#     ${SOURCE_FILES})

add_library(${PROJECT_NAME} SHARED 
    src/pybing.cpp
    ${SOURCE_FILES})




########################################
## set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -Wall")
## set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -Wall")

########################################
## target_link_libraries(bing ${OpenCV_LIBS} ${EXTERNAL_LIBS})
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS} ${EXTERNAL_LIBS})
