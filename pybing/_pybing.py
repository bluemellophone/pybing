from __future__ import absolute_import, division, print_function
# Standard
from collections import OrderedDict as odict
import multiprocessing
import ctypes as C
# Scientific
import utool as ut
import numpy as np
import time
from pybing.pybing_helpers import (_load_c_shared_library, _cast_list_to_c, _extract_np_array)


VERBOSE_BING = ut.get_argflag('--verbbing') or ut.VERBOSE
QUIET_BING   = ut.get_argflag('--quietbing') or ut.QUIET


#============================
# CTypes Interface Data Types
#============================
'''
    Bindings for C Variable Types
'''
NP_FLAGS       = 'aligned, c_contiguous, writeable'
# Primatives
C_OBJ          = C.c_void_p
C_BYTE         = C.c_char
C_CHAR         = C.c_char_p
C_INT          = C.c_int
C_DOUBLE       = C.c_double
C_BOOL         = C.c_bool
C_FLOAT        = C.c_float
NP_INT8        = np.uint8
NP_FLOAT32     = np.float32
# Arrays
C_ARRAY_CHAR   = C.POINTER(C_CHAR)
C_ARRAY_FLOAT  = C.POINTER(C_FLOAT)
NP_ARRAY_INT   = np.ctypeslib.ndpointer(dtype=C_INT,          ndim=1, flags=NP_FLAGS)
NP_ARRAY_FLOAT = np.ctypeslib.ndpointer(dtype=NP_FLOAT32,     ndim=2, flags=NP_FLAGS)
RESULTS_ARRAY  = np.ctypeslib.ndpointer(dtype=NP_ARRAY_FLOAT, ndim=1, flags=NP_FLAGS)


#=================================
# Method Parameter Types
#=================================
'''
IMPORTANT:
    For functions that return void, use Python None as the return value.
    For functions that take no parameters, use the Python empty list [].
'''

METHODS = {}
METHODS['init'] = ([
    C_DOUBLE,        # base
    C_INT,           # W
    C_INT,           # NSS
    C_BOOL,          # verbose
    C_BOOL,          # quiet
], C_OBJ)

METHODS['model'] = ([
    C_OBJ,           # detector
    C_CHAR,          # model_path
    C_BOOL,          # verbose
    C_BOOL,          # quiet
], C_OBJ)

METHODS['train2'] = ([
    C_OBJ,           # detector
    C_BOOL,          # verbose
    C_BOOL,          # quiet
], None)

METHODS['detect'] = ([
    C_OBJ,           # detector
    C_ARRAY_CHAR,    # input_gpath_array
    C_INT,           # _input_gpath_num
    C_INT,           # numPerSz
    RESULTS_ARRAY,   # results_val_array
    NP_ARRAY_INT,    # results_len_array
    C_INT,           # RESULT_LENGTH
    C_BOOL,          # serial
    C_BOOL,          # verbose
    C_BOOL,          # quiet
], None)
RESULT_LENGTH = 4

#=================================
# Load Dynamic Library
#=================================
BING_CLIB = _load_c_shared_library(METHODS)


#=================================
# BING Detector
#=================================
class BING_Detector(object):

    def __init__(bing, verbose=VERBOSE_BING, quiet=QUIET_BING, **kwargs):
        '''
            Create the C object for the PyBING detector.

            Args:
                verbose (bool, optional): verbose flag; defaults to --verbbing flag

            Kwargs:
                base (int)
                W (int)
                NNS (int)

            Returns:
                detector (object): the BING Detector object
        '''
        bing.verbose = verbose
        bing.quiet = quiet

        # Default values
        params = odict([
            ('base',       2.0),
            ('W',          8),
            ('NNS',        2),
            ('verbose',    verbose),
            ('quiet',      quiet),
        ])
        params.update(kwargs)
        params_list = list(params.values())

        if bing.verbose and not bing.quiet:
            """ debug with dmesg | tail -n 200 """
            print('[pybing.py] Start Create New BING Object')
            ut.print_dict(params)
            print('[pybing.py] params_list = %r' % (params_list,))
            print('[pybing.py] type of params = %r' % (list(map(type, params_list)),))
            pass

        bing.detector_c_obj = BING_CLIB.init(*params_list)

        if bing.verbose and not bing.quiet:
            print('[pybing.py] Finished Create New BING Object')

    def model(bing, model_path, **kwargs):
        '''
            Load the model.

            Args:
                model_path (str): model path
                serial (bool, optional): flag to signify if to load the model in serial;
                    defaults to False
                verbose (bool, optional): verbose flag; defaults to object's verbose or
                    selectively enabled for this function

            Returns:
                None
        '''
        # Default values
        params = odict([
            ('verbose',                      bing.verbose),
            ('quiet',                        bing.quiet),
        ])
        params.update(kwargs)

        # Data integrity
        assert len(model_path) > 0, \
            'Must specify at least one model path to load'

        params_list = [
            model_path,
        ] + params.values()
        BING_CLIB.model(bing.detector_c_obj, *params_list)

    def train(bing, **kwargs):
        '''
            NOT IMPLEMENTED

            Returns:
                None
        '''
        raise NotImplementedError()

    def detect(bing, input_gpath_list, **kwargs):
        '''
            Run detection with a given loaded model on a list of images

            Args:
                input_gpath_list (list of str): the list of image paths that you want
                    to test

            Kwargs:
                numPerSz (int): the number of results per size

        '''
        # Default values
        params = odict([
            ('numPerSz',                     130),
            ('batch_size',                   None),
            ('results_val_array',            None),  # This value always gets overwritten
            ('results_len_array',            None),  # This value always gets overwritten
            ('RESULT_LENGTH',                None),  # This value always gets overwritten
            ('serial',                       False),
            ('verbose',                      bing.verbose),
            ('quiet',                        bing.quiet),
        ])
        params.update(kwargs)
        params['RESULT_LENGTH'] = RESULT_LENGTH

        # Try to determine the parallel processing batch size
        if params['batch_size'] is None:
            try:
                cpu_count = multiprocessing.cpu_count()
                if not params['quiet']:
                    print('[pybing py] Detecting with %d CPUs' % (cpu_count, ))
                params['batch_size'] = cpu_count
            except:
                params['batch_size'] = 8

        # Run training algorithm
        batch_size = params['batch_size']
        del params['batch_size']  # Remove this value from params
        batch_num = int(len(input_gpath_list) / batch_size) + 1
        # Detect for each batch
        for batch in ut.ProgressIter(range(batch_num), lbl="[pybing py]", freq=1, invert_rate=True):
            begin = time.time()
            start = batch * batch_size
            end   = start + batch_size
            if end > len(input_gpath_list):
                end = len(input_gpath_list)
            input_gpath_list_        = input_gpath_list[start:end]
            num_images = len(input_gpath_list_)
            # Set image detection to be run in serial if less than half a batch to run
            if num_images < min(batch_size / 2, 8):
                params['serial'] = True
            # Final sanity check
            params['results_val_array'] = np.empty(num_images, dtype=NP_ARRAY_FLOAT)
            params['results_len_array'] = np.empty(num_images, dtype=C_INT)
            # Make the params_list
            params_list = [
                _cast_list_to_c(input_gpath_list_, C_CHAR),
                num_images,
            ] + params.values()
            BING_CLIB.detect(bing.detector_c_obj, *params_list)
            results_list = _extract_np_array(params['results_len_array'], params['results_val_array'], NP_ARRAY_FLOAT, NP_FLOAT32, RESULT_LENGTH)
            conclude = time.time()
            if not params['quiet']:
                print('[pybing py] Took %r seconds to compute %d images' % (conclude - begin, num_images, ))
            for input_gpath, result_list in zip(input_gpath_list_, results_list):
                result_list_ = []
                for result in result_list:
                    # Unpack result into a nice Python dictionary and return
                    temp = {}
                    temp['minx']    = int(result[0])
                    temp['miny']    = int(result[1])
                    temp['maxx']    = int(result[2])
                    temp['maxy']    = int(result[3])
                    result_list_.append(temp)
                yield (input_gpath, result_list_)
            params['results_val_array'] = None
            params['results_len_array'] = None

    # Pickle functions
    def dump(bing, file):
        '''
            UNIMPLEMENTED

            Args:
                file (object)

            Returns:
                None
        '''
        pass

    def dumps(bing):
        '''
            UNIMPLEMENTED

            Returns:
                string
        '''
        pass

    def load(bing, file):
        '''
            UNIMPLEMENTED

            Args:
                file (object)

            Returns:
                detector (object)
        '''
        pass

    def loads(bing, string):
        '''
            UNIMPLEMENTED

            Args:
                string (str)

            Returns:
                detector (object)
        '''
        pass
