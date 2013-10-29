#plot_illu_housekeeping_line.py
import os
import shutil
from Betsy import bie
from Betsy import rulebase
from Betsy import module_utils

def run(data_node,parameters,network):
    outfile = name_outfile(data_node)
    module_utils.plot_line_keywd(data_node.attributes['filename'],'housekeeping',outfile)
    assert module_utils.exists_nz(outfile),(
        'the output file %s for plot_illu_housekeeping_line fails'%outfile)
    new_parameters = parameters.copy()
    new_parameters['filename'] = os.path.split(outfile)[-1]
    out_node = bie.Data(rulebase.HousekeepingPlot,**new_parameters)
    return out_node



def make_unique_hash(data_node,pipeline,parameters):
    identifier = data_node.attributes['filename']
    return module_utils.make_unique_hash(identifier,pipeline,parameters)


def name_outfile(data_node):
    original_file = module_utils.get_inputid(
        data_node.attributes['filename'])
    filename = 'housekeeping_plot_' + original_file + '.png'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def get_out_attributes(parameters,data_node):
    return parameters

def find_antecedents(network, module_id,data_nodes,parameters):
    data_node = module_utils.get_identifier(network, module_id,
                                            data_nodes,datatype='ControlFile')
    
    return data_node