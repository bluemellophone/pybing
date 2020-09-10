#!/usr/bin/env python2.7
from __future__ import absolute_import, division, print_function
from os.path import join
from pybing import BING_Detector
import utool


TEST_DATA_DETECT_URL = 'https://lev.cs.rpi.edu/public/data/testdata_bing.zip'
TEST_DATA_MODEL_URL =  'https://lev.cs.rpi.edu/public/models/bing.zip'


def test_pybing():
    #=================================
    # Detect Initialization
    #=================================

    # Create detector
    detector = BING_Detector()

    test_path = utool.grab_zipped_url(TEST_DATA_DETECT_URL, appname='utool')
    model_path = utool.grab_zipped_url(TEST_DATA_MODEL_URL, appname='pybing')

    #=================================
    # Detect using Random Forest
    #=================================
    model_path = join(model_path, 'model')
    print('Loading models: %r' % (model_path, ))
    detector.model(model_path)

    gpath_list = utool.list_images(test_path, fullpath=True, recursive=False)
    num_images = len(gpath_list)
    print('Testing on %r images' % num_images)

    with utool.Timer('[test_pybing] for loop detector.detect') as t1:
        results_list = detector.detect(gpath_list)

    print('')
    print('+ --------------')
    print('| total time1: %r' % t1.ellapsed)
    print('|')
    print('| num results1 = %r' % (list(map(len, [ _[1] for _ in results_list ] ))))
    return locals()


if __name__ == '__main__':
    test_pybing()
