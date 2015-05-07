#include "kyheader.h"
#include "Objectness.h"
#include "ValStructVec.h"
#include "CmShow.h"


void RunObjectness(CStr &resName, double base, int W, int NSS, int numPerSz);

void illutrateLoG()
{
    for (float delta = 0.5f; delta < 1.1f; delta+=0.1f){
        Mat f = Objectness::aFilter(delta, 8);
        normalize(f, f, 0, 1, NORM_MINMAX);
        CmShow::showTinyMat(format("D=%g", delta), f);
    }
    waitKey(0);
}

int main(int argc, char* argv[])
{
    //illutrateLoG();
    RunObjectness("WinRecall.m", 2, 8, 2, 130);

    return 0;
}

void RunObjectness(CStr &resName, double base, int W, int NSS, int numPerSz)
{
    srand((unsigned int) time(NULL));
    // DataSetVOC voc2007("/Datasets/VOC2007/");
    // voc2007.loadAnnotations();
    //voc2007.loadDataGenericOverCls();

    // printf("Dataset:`%s' with %d training and %d testing\n", _S(voc2007.wkDir), voc2007.trainNum, voc2007.testNum);
    // printf("%s Base = %g, W = %d, NSS = %d, perSz = %d\n", _S(resName), base, W, NSS, numPerSz);

    Objectness objNess(base, W, NSS);
    objNess.loadTrainedModel("/Datasets/VOC2007/model");
    // printf("Model\n");

    for(int i = 1; i < 10; i++)
    {
        string filename = format("/Datasets/VOC2007/JPEGImages/00001%d.jpg", i);
        printf("%s\n", filename.c_str());
        Mat img3u = imread(filename);
        ValStructVec<float, Vec4i> boxesTests;
        boxesTests.reserve(10000);
        objNess.getObjBndBoxes(img3u, boxesTests, numPerSz);

        int xmin, ymin, xmax, ymax;
        int num = boxesTests.size();
        printf("    %d\n", num);
        for (int j = 0; j < num; j++){
            Vec4i bb = boxesTests[j];
            xmin = bb[0];
            ymin = bb[1];
            xmax = bb[2];
            ymax = bb[3];
            // printf("    (%d, %d) -> (%d, %d)\n", xmin, ymin, xmax, ymax);
            rectangle(img3u, cvPoint(xmin, ymin), cvPoint(xmax, ymax), cvScalar(0, 0, 255), 3);
        }

        imshow(filename, img3u);
        waitKey(0);
    }


    // Objectness objNess(voc2007, base, W, NSS);
    // vector<vector<Vec4i> > boxesTests;
    // objNess.getObjBndBoxesForTests(boxesTests, 250);

    // objNess.getObjBndBoxesForTestsFast(boxesTests, numPerSz);
    //objNess.getRandomBoxes(boxesTests);

    //objNess.evaluatePerClassRecall(boxesTests, resName, 1000);
    //objNess.illuTestReults(boxesTests);
    //objNess.evaluatePAMI12();
    //objNess.evaluateIJCV13();
}
