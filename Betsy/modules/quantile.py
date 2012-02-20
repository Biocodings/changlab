#quantile.py

import os
import module_utils
from genomicode import quantnorm
import arrayio

def run(parameters,objects):
    identifier,single_object = get_identifier(parameters,objects)
    outfile,new_objects = get_outfile(parameters,objects)
    M = arrayio.read(identifier)
    Y = quantnorm.normalize(M)
    f = file(outfile,'w')
    Y_c = arrayio.convert(Y,to_format = arrayio.pcl_format)
    arrayio.pcl_format.write(Y_c,f)
    f.close()
    module_utils.write_Betsy_parameters_file(parameters,single_object)
    return new_objects


def make_unique_hash(parameters,objects):
    return module_utils.make_unique_hash(parameters,objects,'signal_file','Contents,DatasetId')

def get_outfile(parameters,objects):
    return module_utils.get_outfile(parameters,objects,'signal_file','Contents,DatasetId','signal_file')
    
def get_identifier(parameters,objects):
    return module_utils.find_object(parameters,objects,'signal_file','Contents,DatasetId')