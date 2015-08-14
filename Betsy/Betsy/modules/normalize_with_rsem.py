#normalize_with_rsem.py
import os
from Betsy import module_utils, bie3, rulebase
import subprocess
from genomicode import config
import tempfile


def preprocess_single_sample(folder, sample, files, out_file, ref, num_cores):
    if ref == 'human':
        ref_file = config.rna_human
    elif ref == 'mouse':
        ref_file = config.rna_mouse
    else:
        raise ValueError("we cannot handle %s" % ref)
    bamfiles = os.listdir(folder)
    if sample + '.bam' in bamfiles:
        input_file = os.path.join(folder, sample + '.bam')
        command = ['rsem-calculate-expression', '--bam', input_file, ref_file,
                   '--no-bam-output', '-p', str(num_cores), sample]
        if len(files) == 2:
            command.append('--paired-end')
    else:
        if len(files) == 1:
            input_file = os.path.join(folder, files[0][0])
            command = ['rsem-calculate-expression', '--bam', input_file,
                       ref_file, '--no-bam-output', '-p', str(num_cores),
                       sample]
        elif len(files) == 2:
            input_file1 = os.path.join(folder, files[0][0])
            input_file2 = os.path.join(folder, files[1][0])
            command = ['rsem-calculate-expression', '--bam', '--paired-end',
                       input_file1, input_file2, ref_file, '--no-bam-output',
                       '-p', str(num_cores), sample]
        else:
            raise ValueError('number files is not correct')
    process = subprocess.Popen(command,
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    #process.wait()
    error_message = process.communicate()[1]
    if 'error' in error_message:
        raise ValueError(error_message)
    slice_BIN = config.slice_matrix
    command = ['python', slice_BIN, sample + '.genes.results',
               '--select_col_ids', 'transcript_id,gene_id,TPM',
               '--replace_col_ids', 'TPM,' + sample]
    f = file(out_file, 'w')
    try:
        process = subprocess.Popen(command,
                                   shell=False,
                                   stdout=f,
                                   stderr=subprocess.PIPE)
        process.wait()
    finally:
        f.close()
    error_message = process.communicate()[1]
    if 'error' in error_message:
        raise ValueError(error_message)
    assert module_utils.exists_nz(out_file), (
        'the output file %s does not exist' % out_file
    )


def preprocess_multiple_sample(folder, group_dict, outfile, ref, num_cores):
    filenames = os.listdir(folder)
    file_list = []
    for sample in group_dict:
        temp_file = tempfile.mkstemp()[1]
        preprocess_single_sample(folder, sample, group_dict[sample], temp_file,
                                 ref, num_cores)
        file_list.append(temp_file)
    result_file = file_list[0]
    tmp_list = file_list[:]
    try:
        for filename in file_list[1:]:
            tmp_result = tempfile.mkstemp()[1]
            f = file(tmp_result, 'a+')
            try:
                module_utils.merge_two_files(result_file, filename, f)
            finally:
                f.close()
                tmp_list.append(tmp_result)
            result_file = tmp_result
        os.rename(result_file, outfile)
    finally:
        for filename in tmp_list:
            if os.path.exists(filename):
                os.remove(filename)


def run(network, antecedents, out_attributes, user_options, num_cores):
    data_node, group_node = antecedents
    outfile = name_outfile(antecedents, user_options)
    group_dict = module_utils.process_group_info(group_node.identifier)
    preprocess_multiple_sample(data_node.identifier, group_dict, outfile,
                               data_node.data.attributes['ref'], num_cores)
    assert module_utils.exists_nz(outfile), (
        'the output file %s for normalize_with_rsem does not exist' % outfile
    )
    out_node = bie3.Data(rulebase._SignalFile_Postprocess, **out_attributes)
    out_object = module_utils.DataObject(out_node, outfile)
    return out_object


def make_unique_hash(pipeline, antecedents, out_attributes, user_options):
    data_node, group_node = antecedents
    identifier = data_node.identifier
    return module_utils.make_unique_hash(identifier, pipeline, out_attributes,
                                         user_options)


def name_outfile(antecedents, user_options):
    data_node, group_node = antecedents
    original_file = module_utils.get_inputid(data_node.identifier)
    filename = original_file + '.tdf'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def set_out_attributes(antecedents, out_attributes):
    return out_attributes


def find_antecedents(network, module_id, out_attributes, user_attributes,
                     pool):
    filter1 = module_utils.AntecedentFilter(datatype_name='BamFolder')
    filter2 = module_utils.AntecedentFilter(datatype_name='SampleGroupFile')
    x = module_utils.find_antecedents(
        network, module_id, user_attributes, pool, filter1, filter2)
    return x