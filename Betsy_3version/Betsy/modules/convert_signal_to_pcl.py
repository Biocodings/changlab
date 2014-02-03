#convert_signal_to_pcl.py
import os
from Betsy import module_utils
import shutil
from Betsy import bie3,rulebase

def run(data_node,parameters, user_input,network):
    """convert signal file to pcl format"""
    import arrayio
    outfile = name_outfile(data_node,user_input)
    f = file(outfile, 'w')
    M = arrayio.choose_format(data_node.identifier)
    if M.__name__[8: -7] == 'pcl':
        shutil.copyfile(data_node.identifier, outfile)
        f.close()
    else:
        M = arrayio.read(data_node.identifier)
        M_c = arrayio.convert(M, to_format=arrayio.pcl_format)
        arrayio.pcl_format.write(M_c, f)
        f.close()
    assert module_utils.exists_nz(outfile), (
        'the output file %s for convert_signal_to_pcl fails' % outfile)
    out_node = bie3.Data(rulebase.SignalFile1,**parameters)
    out_object = module_utils.DataObject(out_node,outfile)
    return out_object




def name_outfile(data_node,user_input):
    original_file = module_utils.get_inputid(data_node.identifier)
    filename = 'signal_' + original_file + '.pcl'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def make_unique_hash(data_node,pipeline,parameters,user_input):
    identifier = data_node.identifier
    return module_utils.make_unique_hash(identifier,pipeline,
                                         parameters,user_input)

def get_out_attributes(parameters,data_node):
    return parameters

def find_antecedents(network, module_id,data_nodes):
    data_node = module_utils.get_identifier(network, module_id,
                                            data_nodes)

    return data_node
