#center_genes.py
import os
import subprocess
from Betsy import module_utils,bie3,rulebase


def run(data_node,parameters, user_input,network):
    """mean or median"""
    CLUSTER_BIN = 'cluster'
    center_alg = {'mean': 'a', 'median': 'm'}
    try:
        center_parameter = center_alg[parameters['gene_center']]
    except:
        raise ValueError("Centering parameter is not recognized")
    outfile = name_outfile(data_node,user_input)
    process = subprocess.Popen([CLUSTER_BIN, '-f', data_node.identifier,
                                '-cg', center_parameter, '-u', outfile],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    error_message = process.communicate()[1]
    if error_message:
        raise ValueError(error_message)
    outputfile = outfile + '.nrm'
    os.rename(outputfile, outfile)
    assert module_utils.exists_nz(outfile), (
        'the output file %s for centering fails' % outfile)
    out_node = bie3.Data(rulebase.SignalFile1,**parameters)
    out_object = module_utils.DataObject(out_node,outfile)
    return out_object


def name_outfile(data_node,user_input):
    original_file = module_utils.get_inputid(data_node.identifier)
    filename = 'signal_center_' + original_file + '.tdf'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def get_out_attributes(parameters,data_node):
    new_parameters = parameters.copy()
    new_parameters['format']='tdf'
    return new_parameters
    

def make_unique_hash(data_node,pipeline,parameters,user_input):
    identifier = data_node.identifier
    return module_utils.make_unique_hash(identifier,pipeline,parameters,user_input)

def find_antecedents(network, module_id,data_nodes):
    data_node = module_utils.get_identifier(network, module_id,
                                            data_nodes)
    return data_node
