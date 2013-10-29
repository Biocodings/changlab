#classify_with_svm.py
import svmutil
import sys
import arrayio
import os
from Betsy import read_label_file, module_utils
from Betsy import bie
from Betsy import rulebase

def run(in_nodes,parameters, network):
    svm_model,data_node_test,cls_node_train = in_nodes
    outfile = name_outfile(in_nodes)
    a, train_label, second_line = read_label_file.read(
            cls_node_train.attributes['filename'])
    M = arrayio.read(data_node_test.attributes['filename'])
    # convert to the format libsvm accept
    test = M.matrix(None,range(len(train_label),M.dim()[1]))
    x_test = module_utils.format_convert(test)
    model = svmutil.svm_load_model(svm_model.attributes['filename'])
    a, train_label, second_line = read_label_file.read(
            cls_node_train.attributes['filename'])
    y_test = [0]*len(x_test)
    p_label, p_acc, p_val = svmutil.svm_predict(y_test, x_test, model)
    prediction_index = [int(i) for i in p_label]
    prediction = [second_line[i] for i in prediction_index]
    name = test._col_names.keys()[0]
    sample_name = test._col_names[name]
    result = [['Sample_name', 'Predicted_class', 'Confidence']]
    for i in range(len(sample_name)):
        result.append(
            [str(sample_name[i]), prediction[i], str(p_val[i][0])])
    f = file(outfile, 'w')
    for i in result:
        f.write('\t'.join(i))
        f.write('\n')
    f.close()
    assert module_utils.exists_nz(outfile), (
        'the output file %s for classify_with_svm fails' % outfile)
    new_parameters = parameters.copy()
    new_parameters['filename'] = os.path.split(outfile)[-1]
    out_node = bie.Data(rulebase.ClassifyFile,**new_parameters)
    return out_node




def name_outfile(in_nodes):
    svm_model,data_node_test,cls_node_train = in_nodes
    original_file = module_utils.get_inputid(svm_model.attributes['filename'])
    filename = 'svm_result' + original_file + '.txt'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def get_out_attributes(parameters,in_nodes):
    return parameters

def make_unique_hash(in_nodes,pipeline,parameters):
    svm_model,data_node_test,cls_node_train = in_nodes
    identifier = svm_model.attributes['filename']
    return module_utils.make_unique_hash(identifier,pipeline,parameters)

def find_antecedents(network, module_id,data_nodes,parameters):
    svm_model_node = module_utils.get_identifier(network, module_id,
                                            data_nodes,
                                            datatype='SvmModel')
    data_node_test = module_utils.get_identifier(network, module_id,
                                            data_nodes,contents='class0,class1,test',
                                            datatype='SignalFile2')
    cls_node_train = module_utils.get_identifier(network, module_id,
                                            data_nodes,contents='class0,class1',
                                            datatype='ClassLabelFile')
    return svm_model_node,data_node_test,cls_node_train