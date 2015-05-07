#include <iostream>
#include <fstream>
#include <string>
#include <vector>

#include "pybing.h"
#include "kyheader.h"
#include "Objectness.h"
#include "ValStructVec.h"

using namespace std;

typedef unsigned char uint8;

#ifdef __cplusplus
extern "C"
{
#endif
#define PYBING extern PYBING_EXPORT

// TODO: REMOVE STRING WHERE CHAR* SHOULD BE USED
PYBING Objectness *init(double base, int W, int NSS, bool verbose, bool quiet)
{
    Objectness *detector = new Objectness(base, W, NSS);
    return detector;
}

PYBING void model(Objectness *detector, char *model_path, bool verbose, bool quiet)
{
    // string model_path_str(model_path);
    detector->loadTrainedModel(model_path);
}

PYBING void train2(Objectness *detector, bool verbose, bool quiet)
{
    // Nothing
}

PYBING void detect(Objectness *detector, char **input_gpath_array, int _input_gpath_num,
                                 int numPerSz,
                                 float** results_array, int* length_array, 
                                 int RESULT_LENGTH, bool serial, bool verbose, bool quiet)
{
    if( ! quiet )
    {
        // Parallel processing of the images, ideally, one image per core
        if(serial)
        {
            cout << "[pybing c] Detecting images in serial" << endl;
        }
        else
        {
            cout << "[pybing c] Detecting images in parallel" << endl;
        }
    }
    
    #pragma omp parallel for if(!serial)
    for (int index = 0; index < _input_gpath_num; ++index)
    {
        float **results = &results_array[index];
        string input_gpath = input_gpath_array[index];

        // Run detection
        Mat image = imread(input_gpath);
        ValStructVec<float, Vec4i> boxesTests;
        boxesTests.reserve(10000);
        detector->getObjBndBoxes(image, boxesTests, numPerSz);

        int length = boxesTests.size();
        *results = new float[ length * RESULT_LENGTH ];
        for (int i = 0; i < length; ++i)
        {
            for (int j = 0; j < RESULT_LENGTH; ++j)
            {
                (*results)[i * RESULT_LENGTH + j] = boxesTests[i][j];
            }
        }
        length_array[index] = length;
    }
}
#ifdef __cplusplus
}
#endif
