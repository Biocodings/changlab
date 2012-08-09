#extract_illumina_idat_files.py

import module_utils
import shutil
import os
import Betsy_config
import zipfile
import hash_method
import rule_engine

def extract_all(zipName):
    z = zipfile.ZipFile(zipName)
    for f in z.namelist():
        if f.endswith('/'):
            os.makedirs(f)
        else:
            z.extract(f)

def run(parameters,objects,pipeline):
    single_object = get_identifier(parameters,objects)
    outfile = get_outfile(parameters,objects,pipeline)
    if zipfile.is_zipfile(single_object.identifier):
        directory = os.path.split(single_object.identifier)[-1]
        directory = os.path.splitext(directory)[0]
        directory = os.path.join(os.getcwd(),directory)
        extract_all(single_object.identifier)
    else:
        directory = single_object.identifier
    illumina_file = []
    for filename in os.listdir(directory):
        if filename in ['.DS_Store','._.DS_Store','.Rapp.history']:
            continue
        if filename.endswith('.idat'):
            illumina_file.append(filename)
    if illumina_file:
        os.mkdir(outfile)
        for filename in illumina_file:
            if filename[:-5].endswith('_Grn'):
                newfilename = filename[:-9] + filename[-5:]
            else:
                newfilename = filename
            old_file = os.path.join(directory,filename)
            new_file = os.path.join(outfile,newfilename)
            shutil.copyfile(old_file,new_file)
        assert module_utils.exists_nz(outfile),(
            'the output file %s for extract_illumina_idat_files fails'%outfile)
        new_objects = get_newobjects(parameters,objects,pipeline)
        module_utils.write_Betsy_parameters_file(
                        parameters,single_object,pipeline,outfile)
        return new_objects
    else:
        return None
    
def make_unique_hash(identifier,pipeline,parameters):
    original_file = module_utils.get_inputid(identifier)
    hash_profile={'version': 'illumina',
                   'number of files':str(len(os.listdir(identifier))),
                  'filenames':str(os.listdir(identifier))}
    hash_result=hash_method.hash_parameters(
        original_file,pipeline,**hash_profile)
    return hash_result

def get_outfile(parameters,objects,pipeline):
    single_object = get_identifier(parameters,objects)
    original_file = module_utils.get_inputid(single_object.identifier)
    hash_result = make_unique_hash(single_object.identifier,pipeline,parameters)
    filename = 'idat_files_' + hash_result + '*'+ original_file
    outfile = os.path.join(os.getcwd(),filename)
    return outfile

def get_newobjects(parameters,objects,pipeline):
    outfile = get_outfile(parameters,objects,pipeline)
    single_object = get_identifier(parameters,objects)
    new_objects = module_utils.get_newobjects(
        outfile,'idat_files',parameters,objects,single_object)
    return new_objects
    

def get_identifier(parameters,objects):
    single_object = module_utils.find_object(
        parameters,objects,'idat_files','contents')
    assert os.path.exists(single_object.identifier),(
        'the input file %s for extract_illumina_idat_files does not exist'
        %single_object.identifier)
    return single_object
