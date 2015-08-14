#convert_label_to_cls.py

import os
from Betsy import module_utils, read_label_file
import arrayio
from Betsy import bie3, rulebase


def run(network, antecedents, out_attributes, user_options, num_cores):
    data_node, cls_node = antecedents
    if data_node and cls_node:
        outfile = name_outfile(antecedents, user_options)
        f = file(cls_node.identifier, 'rU')
        text = f.readlines()
        f.close()
        text = [i.rstrip() for i in text]
        label_dict = {}
        for line in text:
            words = line.split('\t')
            if words[1] in label_dict:
                label_dict[words[1]].append(words[0])
            else:
                label_dict[words[1]] = [words[0]]
        class_names = label_dict.keys()
        M = arrayio.read(data_node.identifier)
        column_names = M.col_names('_SAMPLE_NAME')
        label_line = [0] * len(column_names)
        for i in range(len(class_names)):
            sample_names = label_dict[class_names[i]]
            for sample_name in sample_names:
                index = column_names.index(sample_name)
                label_line[index] = str(i)
        read_label_file.write(outfile, class_names, label_line)
        assert module_utils.exists_nz(outfile), (
            'the output file %s for convert_label_to_cls fails' % outfile
        )
        out_node = bie3.Data(rulebase.ClassLabelFile, **out_attributes)
        out_object = module_utils.DataObject(out_node, outfile)
        return out_object
    return False


def find_antecedents(network, module_id, out_attributes, user_attributes,
                     pool):
    filter1 = module_utils.AntecedentFilter(datatype_name='_SignalFile_Merge')
    filter2 = module_utils.AntecedentFilter(datatype_name='ClassLabelFile')
    x = module_utils.find_antecedents(
        network, module_id, user_attributes, pool, filter1, filter2)
    return x


def name_outfile(antecedents, user_options):
    data_node, cls_node = antecedents
    original_file = module_utils.get_inputid(data_node.identifier)
    filename = 'class_label_' + original_file + '.cls'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def set_out_attributes(antecedents, out_attributes):
    return out_attributes


def make_unique_hash(pipeline, antecedents, out_attributes, user_options):
    data_node, cls_node = antecedents
    identifier = data_node.identifier
    return module_utils.make_unique_hash(identifier, pipeline, out_attributes,
                                         user_options)