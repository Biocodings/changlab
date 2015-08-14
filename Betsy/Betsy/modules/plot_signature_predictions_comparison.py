#plot_signature_prediction_comparison.py
import os
import subprocess
from genomicode import config, graphlib
import arrayio
from Betsy import bie3
from Betsy import rulebase
from Betsy import module_utils


def run(network, antecedents, out_attributes, user_options, num_cores):
    """generate a heatmap of input file"""
    in_data = antecedents
    outfile = name_outfile(in_data, user_options)
    Heatmap_path = config.arrayplot
    Heatmap_BIN = module_utils.which(Heatmap_path)
    assert Heatmap_BIN, 'cannot find the %s' % Heatmap_path

    command = ['python', Heatmap_BIN, in_data.identifier, '-o', outfile,
               "--label_arrays", "--label_genes"]
    if 'color' in out_attributes.keys():
        color = ['--color', out_attributes['color'].replace('_', '-')]
        command.extend(color)
    
    M = arrayio.read(in_data.identifier)
    nrow = M.nrow()
    ncol = M.ncol()
    ratio = float(nrow) / ncol
    max_box_height = 20
    max_box_width = 60
    if 'hm_width' in user_options:
        max_box_width = user_options['hm_width']
    
    if 'hm_height' in user_options:
        max_box_height = user_options['hm_height']
    
    if ratio >= 4:
        x, y = graphlib.find_tall_heatmap_size(nrow, ncol,
                                               max_box_height=max_box_height,
                                               max_box_width=max_box_width,
                                               min_box_height=20,
                                               min_box_width=20,
                                               max_megapixels=128)
    else:
        x, y = graphlib.find_wide_heatmap_size(nrow, ncol,
                                               max_box_height=max_box_height,
                                               max_box_width=max_box_width,
                                               min_box_height=20,
                                               min_box_width=20,
                                               max_megapixels=128)
    
    command.extend(['-x', str(x), '-y', str(y)])
    process = subprocess.Popen(command,
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    error_message = process.communicate()[1]
    if error_message:
        raise ValueError(error_message)
    
    assert module_utils.exists_nz(outfile), (
        'the output file %s for plot_signature_prediction_comparison fails' %
        outfile)
    out_node = bie3.Data(rulebase.ScoreComparePlot, **out_attributes)
    out_object = module_utils.DataObject(out_node, outfile)
    return out_object


def name_outfile(antecedents, user_options):
    original_file = module_utils.get_inputid(antecedents.identifier)
    filename = 'heatmap_' + original_file + '.png'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def set_out_attributes(antecedents, out_attributes):
    return out_attributes


def make_unique_hash(pipeline, antecedents, out_attributes, user_options):
    identifier = antecedents.identifier
    return module_utils.make_unique_hash(identifier, pipeline, out_attributes,
                                         user_options)


def find_antecedents(network, module_id, out_attributes, user_attributes,
                     pool):
    data_node = module_utils.find_antecedents(network, module_id, user_attributes,
                                            pool)
    return data_node