#classify_with_weighted_voting.py
import shutil
import os
import subprocess
import arrayio
from genomicode import config
from Betsy import bie 
from Betsy import rulebase
from Betsy import module_utils, read_label_file

def run(in_nodes,parameters, network):
    data_node_train,data_node_test,cls_node_train = in_nodes
    outfile = name_outfile(in_nodes)
    module_name = 'WeightedVoting'
    gp_parameters = dict()
    file1, file2 = module_utils.convert_to_same_platform(
        data_node_train.attributes['filename'],
        data_node_test.attributes['filename'])
    result, label_line, class_name = read_label_file.read(
        cls_node_train.attributes['filename'])
    M = arrayio.read(data_node_test.attributes['filename'])
    label_line = ['0'] * M.dim()[1]
    read_label_file.write('temp_test.cls',class_name,label_line)
    gp_parameters['train.filename'] = file1
    gp_parameters['train.class.filename'] = cls_node_train.attributes['filename']
    gp_parameters['test.filename'] = file2
    gp_parameters['test.class.filename'] = 'temp_test.cls'
    num_features = parameters['num_features']
    if num_features != 'all':
        gp_parameters['num.features'] = str(parameters['num_features'])
    if parameters['wv_minstd']:
        assert module_utils.is_number(
            parameters['wv_minstd']), 'the sv_minstd should be number'
        gp_parameters['min.std'] = str(parameters['wv_minstd'])
        
    wv_feature_stat = ['wv_snr', 'wv_ttest', 'wv_snr_median',
                       'wv_ttest_median', 'wv_snr_minstd',
                       'wv_ttest_minstd', 'wv_snr_median_minstd',
                       'wv_ttest_median_minstd']
    
    assert parameters['wv_feature_stat'] in wv_feature_stat, (
            'the wv_feature_stat is invalid')
    gp_parameters['feature.selection.statistic'] = str(
            wv_feature_stat.index(parameters[
                'wv_feature_stat']))
    gp_path = config.genepattern
    gp_module = module_utils.which(gp_path)
    assert gp_module, 'cannot find the %s' % gp_path
    download_directory = os.path.join(os.getcwd(),'wv_result')
    command = [gp_module, module_name, '-o', download_directory]
    for key in gp_parameters.keys():
        a = ['--parameters', key + ':' + gp_parameters[key]]
        command.extend(a)
    process = subprocess.Popen(command, shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    process.wait()
    error_message = process.communicate()[1]
    if error_message:
        raise ValueError(error_message)
    assert os.path.exists(download_directory), (
        'there is no output directory for weightedVoting')
    result_files = os.listdir(download_directory)
    assert 'stderr.txt' not in result_files, 'gene_pattern get error'
    gp_files = os.listdir(download_directory)
    for gp_file in gp_files:
        if gp_file.endswith('pred.odf'):
            gp_file = os.path.join(download_directory, gp_file)
            f = file(gp_file, 'r')
            text = f.readlines()
            f.close()
            os.rename(os.path.join(download_directory, gp_file),
                      os.path.join(download_directory, 'prediction.odf'))
            assert text[1][0: 12] == 'HeaderLines='
            start = int(text[1][12: -1])
            newresult = [['Sample_name', 'Predicted_class', 'Confidence']]
            for i in text[start + 2:]:
                line = i.split()
                n = len(line)
                newline = [' '.join(line[0: n - 4]), line[n - 3],
                               line[n - 2]]
                newresult.append(newline)
            f = file(outfile, 'w')
            for i in newresult:
                f.write('\t'.join(i))
                f.write('\n')
            f.close()
    assert module_utils.exists_nz(outfile), (
        'the output file %s for classify_with_weighted_voting fails' % outfile)
    new_parameters = parameters.copy()
    new_parameters['filename'] = os.path.split(outfile)[-1]
    out_node = bie.Data(rulebase.ClassifyFile,**new_parameters)
    return out_node



def name_outfile(in_nodes):
    data_node_train,data_node_test,cls_node_train = in_nodes
    original_file = module_utils.get_inputid(data_node_train.attributes['filename'])
    filename = 'weighted_voting_' + original_file + '.cdt'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def get_out_attributes(parameters,in_nodes):
    return parameters

def make_unique_hash(in_nodes,pipeline,parameters):
    data_node_train,data_node_test,cls_node_train = in_nodes
    identifier = data_node_train.attributes['filename']
    return module_utils.make_unique_hash(identifier,pipeline,parameters)

def find_antecedents(network, module_id,data_nodes,parameters):
    data_node_train = module_utils.get_identifier(network, module_id,
                                            data_nodes,contents='class0,class1',
                                            datatype='SignalFile2')
    data_node_test = module_utils.get_identifier(network, module_id,
                                            data_nodes,contents='test',
                                            datatype='SignalFile2')
    cls_node_train = module_utils.get_identifier(network, module_id,
                                            data_nodes,contents='class0,class1',
                                            datatype='ClassLabelFile')
    return data_node_train,data_node_test,cls_node_train
