#!/usr/bin/env python
import os
import argparse
import numpy
import sys
import arrayio
from genomicode import filelib, jmath, genesetlib, config
from genomicode import matrixlib, Matrix, colorlib
from genomicode import hashlib


def guess_file_type(filename):
    M = arrayio.read(filename)
    headers = M._row_order
    if headers == ['FILE', 'SAMPLE']:
        return 'geneset_file'
    else:
        return 'gene_expression_file'


def calc_km(survival, dead, group, unique_group):
    R = jmath.start_R()
    jmath.R_equals(survival, 'survival')
    jmath.R_equals(dead, 'dead')
    jmath.R_equals(group, 'group')
    R('x <- calc.km.multi(survival, dead, group)')
    c = R['x']
    p_value = c.rx2('p.value')[0]
    surv90 = [''] * len(unique_group)
    surv50 = [''] * len(unique_group)
    for k in range(len(unique_group)):
        surv90[k] = c.rx2('surv').rx2(unique_group[k]).rx2('surv.90')[0]
        surv50[k] = c.rx2('surv').rx2(unique_group[k]).rx2('surv.50')[0]
    med_low,med_high=surv50[0], surv50[-1]
    MAX_SURV = 1e10
    direction = ''
    if (str(med_high), str(med_low)) == ('NA', 'NA'):
        med_low, med_high=surv90[0], surv90[-1]
    if str(med_high) == 'NA':
        med_high = MAX_SURV
    if str(med_low) == 'NA':
        med_low = MAX_SURV
    assert med_low <= MAX_SURV and med_high <= MAX_SURV
    if med_high > med_low:
        direction = ('Low expression has shorter survival.')
    elif med_high < med_low:
        direction = ('High expression has shorter survival.')
    if p_value >= 0.05:
        direction = ''
    surv90 = ['' if (str(k) == 'NA') else str(k) for k in surv90]
    surv50 = ['' if (str(k) == 'NA') else str(k) for k in surv50]
    return p_value, surv90, surv50, direction


def parse_cutoffs(cutoffs):
    if cutoffs:
        cutoffs = cutoffs.split(',')
        cutoffs = [float(i) for i in cutoffs]
        cutoffs.sort()
    if not cutoffs:
        cutoffs = [0.5]
    for cutoff in cutoffs:
        assert cutoff > 0 and cutoff < 1.0, 'cutoff should be between 0 and 1'
    cutoffs = [0] + cutoffs + [1]
    return cutoffs


def parse_genes(genes):
    if genes:
        gene_list = []
        for i in genes:
            gene_list.extend(i.split(','))
        return gene_list
    else:
        return None


def align_matrix_with_clinical_data(M, clinical_dict):
    import arrayio

    assert clinical_dict, "No clinical data."

    sample_name = M._col_names['_SAMPLE_NAME']

    # Figure out the header in the clinical data that contains these
    # samples.
    name2count = {}
    for name, values in clinical_dict.iteritems():
        count = len(set(sample_name).intersection(values))
        name2count[name] = count
    best_name = best_count = None
    for name, count in name2count.iteritems():
        if best_count is None or count > best_count:
            best_name, best_count = name, count
    assert best_count > 0, \
           "I could not align the matrix with the clinical data."
    clinical_name = clinical_dict[best_name]

    # From the clinical data, only keep the samples that occur in the
    # matrix.
    I = [i for (i, name) in enumerate(clinical_name) if name in sample_name]
    clinical_clean = {}
    for name, values in clinical_dict.iteritems():
        values_clean = [values[i] for i in I]
        clinical_clean[name] = values_clean
    clinical_dict = clinical_clean

    # Realign the matrix to match the clinical data.
    x = matrixlib.align_cols_to_annot(
        M, clinical_dict[best_name], reorder_MATRIX=True)
    M, colnames = x
    assert colnames == clinical_dict[best_name]

    return M, clinical_dict


## def intersect_clinical_matrix_sample_name(M, clinical_data):
##     sample_name = M._col_names['_SAMPLE_NAME']
##     name_in_clinical = None
##     clinical_dict = dict()
##     for g in clinical_data:
##         name, description, values = g
##         clinical_dict[name] = values
##     for g in clinical_dict:
##         n = len(list(set(sample_name).intersection(set(clinical_dict[g]))))
##         if n > 0:
##             name_in_clinical = clinical_dict[g]
##     assert name_in_clinical, ('cannot match the sample name in '
##                               'clinical data and gene data')
##     return clinical_dict, name_in_clinical


def convert_genesetfile2matrix(filename):
    matrix = [x for x in filelib.read_cols(filename)]
    matrix = jmath.transpose(matrix)
    col_names = {}
    col_names['_SAMPLE_NAME'] = matrix[1][1:]
    row_names = {}
    row_names['geneset'] = []
    data = []
    for line in matrix[2:]:
        single_data = [float(i) for i in line[1:]]
        data.append(single_data)
        row_names['geneset'].append(line[0])
    M = Matrix.InMemoryMatrix(data, row_names=row_names, col_names=col_names)
    return M


def colortuple2hex(R, G, B):
    R = hex(int(R * 255))[2:]
    G = hex(int(G * 255))[2:]
    B = hex(int(B * 255))[2:]
    color_hex = '#' + R + G + B
    return color_hex


def make_color_command(group_names):
    """given group_names,generate a command string for R"""
    if len(group_names) == 2:
        colors = ['#1533AD', '#FFB300']
    else:
        x = colorlib.bild_colors(len(group_names))
        x = [colortuple2hex(*x) for x in x]
        colors = x
    color_command = 'col<-list('
    for i in range(len(group_names)):
        color_command = (color_command + '"'
                         + group_names[i] + '"="' + colors[i] + '",')
    color_command = color_command[:-1] + ')'
    return color_command


def make_group_names(cutoffs, file_type):
    """given the cutoffs and file_type,
       generate group name"""
    score_or_expression = 'Expression'
    if file_type == 'geneset_file':
        score_or_expression = 'Score'
    name = [''] * (len(cutoffs) - 1)
    percentage_name = [''] * (len(cutoffs) - 1)
    if len(cutoffs) - 1 == 2:
        name[0] = 'Low ' + score_or_expression
        name[1] = 'High ' + score_or_expression
    elif len(cutoffs) - 1 > 2:
        for j in range(len(cutoffs) - 1):
            percentage_name[j] = "%d - %d" % (
                cutoffs[j] * 100, cutoffs[j + 1] * 100)
        name[0] = 'Lowest ' + percentage_name[0] + '% ' + score_or_expression
        name[-1] = ('Highest ' + percentage_name[-1] + '% '
                    + score_or_expression)
        for k in range(len(name) - 2):
            name[k + 1] = ('Middle ' + percentage_name[k + 1] +
                           '% ' + score_or_expression)
    return name


def main():
    parser = argparse.ArgumentParser(
        description='Associate gene expression patterns with outcomes.')
    parser.add_argument(dest='expression_file', type=str, default=None,
                        help='gene expression file or geneset score file')
    parser.add_argument(dest='clinical_data', type=str, default=None)
    parser.add_argument('--outcome', dest='outcome', type=str,
                        help=('format <time_header>,<dead_header>'),
                        default=[], action='append')
    parser.add_argument('--gene', dest='gene', type=str,
                        help=('gene to analyze.  It can appear anywhere '
                              'in the annotations of the expression_file. '
                              'To specify multiple genes, use this parameter '
                              'multiple times.'),
                        default=None, action='append')
    parser.add_argument('--geneset', dest='geneset', type=str,
                        help=('geneset to analyze. '
                              'To specify multiple genes, use this parameter '
                              'multiple times.'),
                        default=[], action='append')
    parser.add_argument('--cutoff', dest='cutoff', type=str,
                        help=('comma-separated list of breakpoints '
                              '(between 0 and 1),e.g. 0.25,0.50'),
                        default=None)
    parser.add_argument('-o', dest='filestem', type=str,
                        help='prefix used to name files.  e.g. "myanalysis".',
                        default=None)
    parser.add_argument('--write_prism', dest='write_prism',
                        action="store_true", default=False,
                        help='write Prism-formatted output')
    parser.add_argument('--plot_km', dest='plot_km', action="store_true",
                        help='write PNG-formatted Kaplan-Meier plot',
                        default=False)
    parser.add_argument('--xlab', dest='xlab', default=None, type=str,
                        help='the x label for Kaplan-Meier plot')
    parser.add_argument('--ylab', dest='ylab', default=None, type=str,
                        help='the y label for Kaplan-Meier plot')
    parser.add_argument('--title', dest='title', default=None,
                        type=str, help='the title for Kaplan-Meier plot')

    args = parser.parse_args()
    input_file = args.expression_file
    assert input_file, ('please specify the path of gene expression data '
                        'file or geneset score file')
    file_type = guess_file_type(input_file)
    clinical_file = args.clinical_data
    assert clinical_file, 'please specify the path of clinical data'
    outcomes = args.outcome
    assert len(outcomes) > 0, 'please specify the time_header and dead_header'
    cutoffs = parse_cutoffs(args.cutoff)
    gene_list = parse_genes(args.gene)
    geneset_list = args.geneset
    if gene_list and geneset_list:
        raise AssertionError('we only accept gene '
                             'or geneset at each time, not both')
    
    if file_type == "gene_expression_file":
        assert gene_list, "Please specify a gene to analyze."
        assert not geneset_list, 'gene_expression_file cannot run with geneset'
        M = arrayio.read(input_file)
    elif file_type == "geneset_file":
        assert geneset_list, "Please specify a gene set to analyze."
        assert not gene_list, 'geneset_file cannot run with gene'
        M = convert_genesetfile2matrix(input_file)
    else:
        raise AssertionError, "Unknown file type: %s" % file_type

    clinical_dict = {}
    for x in genesetlib.read_tdf(
        clinical_file, preserve_spaces=True, allow_duplicates=True):
        name, description, values = x
        clinical_dict[name] = values
        
    x = align_matrix_with_clinical_data(M, clinical_dict)
    M, clinical_dict = x


    #if given genes or geneset,get of match genes or geneset
    assert gene_list or geneset_list
    if gene_list:
        x = M._index(row=gene_list)
    elif geneset_list:
        x = M._index(row=geneset_list)
    index_list, rownames = x
    assert index_list, 'we cannot match any gene or geneset as required'
    M = M.matrix(index_list, None)
    headers = M.row_names()
    geneids = M.row_names(headers[0])
    #add the gene annotation column to the output_data
    output_data = []
    for i in range(len(geneids)):
        output_data.append([M.row_names(name)[i] for name in M.row_names()])
        
    kaplanmeierlib_path = config.kaplanmeierlib
    assert os.path.exists(kaplanmeierlib_path), (
        'can not find the kaplanmeierlib script %s' % kaplanmeierlib_path)
    R = jmath.start_R()
    R('require(splines,quietly=TRUE)')
    R('source("' + config.kaplanmeierlib + '")')
    #generate output headers
    name = make_group_names(cutoffs, file_type)
    num_samples = ['Num Samples (' + k + ')' for k in name]
    if file_type == 'gene_expression_file':
        ave_expression = ['Average Expression (' + k + ')'for k in name]
    elif file_type == 'geneset_file':
        ave_expression = ['Average gene set score (' + k + ')'for k in name]
    surv90_header = ['90% Survival (' + k + ')' for k in name]
    surv50_header = ['50% Survival (' + k + ')' for k in name]
    output_header = (['p-value'] + num_samples + ave_expression
                     + surv90_header + surv50_header + ['Relationship'])
    #get the time_header, dead_header,time_data,dead_data,
    #and sample_index for each outcome
    all_time_header = []
    all_dead_header = []
    all_sample_index = []
    all_time_data = []
    all_dead_data = []
    for outcome in outcomes:
        x = outcome.split(',')
        assert len(x) == 2, (
            'the outcome format should be <time_header>,<dead_header>')
        time_header, dead_header = x
        time_data = clinical_dict.get(time_header)
        dead_data = clinical_dict.get(dead_header)
        assert time_data, 'there is no column named %s' % time_header
        assert dead_data, 'there is no column named %s' % dead_header
        #only consider the sample who has month and dead information
        sample_index1 = [index for index, item in
                         enumerate(time_data) if len(item) > 0]
        sample_index2 = [index for index, item in
                         enumerate(dead_data) if len(item) > 0]
        sample_index = list(set(sample_index1).intersection(
            set(sample_index2)))
        all_time_header.append(time_header)
        all_dead_header.append(dead_header)
        all_sample_index.append(sample_index)
        all_time_data.append(time_data)
        all_dead_data.append(dead_data)
    #update the output headers
    for k in range(len(outcomes)):
        if len(outcomes) > 1:
            tmp_header = [all_time_header[k] + ' ' + i for i in output_header]
        else:
            tmp_header = output_header
        headers.extend(tmp_header)
        
    #calculate the survival analysis for each gene in each outcome
    all_group_name = [[]] * len(outcomes)
    all_survival = []
    all_dead = []
    all_p_value = [[]] * len(outcomes)
    jmath.R_equals(cutoffs[1:-1], 'cutoffs')
    for h in range(len(outcomes)):
        survival = [float(all_time_data[h][i]) for i in all_sample_index[h]]
        dead = [int(all_dead_data[h][i]) for i in all_sample_index[h]]
        all_survival.append(survival)
        all_dead.append(dead)
        for i in range(len(geneids)):
            data = M.value(i, None)
            data_select = [data[j] for j in all_sample_index[h]]
            jmath.R_equals(data_select, 'F')
            R('group <- group.by.value(F, cutoffs)')
            group = R['group']
            avg = [0] * len(name)
            num_group = [0] * len(name)
            group_name = [""] * len(group)
            for k in range(len(name)):
                group_data = [data_select[j] for j in range(len(group))
                              if group[j] == k]
                avg[k] = str(sum(group_data) / len(group_data))
                num_group[k] = str(len(group_data))
            for k in range(len(group)):
                group_name[k] = name[group[k]]
            p_value, surv90, surv50, direction = calc_km(survival,
                                                         dead, group_name,name)
            if file_type == 'geneset_file':
                direction = direction.replace('expression', 'gene set score')
            single_data = ([str(p_value)] + num_group + avg + surv90
                           + surv50 + [direction])
            output_data[i].extend(single_data)
            all_group_name[h].append(group_name)
            all_p_value[h].append(p_value)
    #generate the prism file and the km plot for each gene in each outcome
    filestem = '' if not args.filestem else args.filestem + '.'
    for h in range(len(outcomes)):
        jmath.R_equals(all_survival[h], 'survival')
        jmath.R_equals(all_dead[h], 'dead')
        for i in range(len(geneids)):
            sample_group_name = all_group_name[h][i]
            jmath.R_equals(sample_group_name, 'name')
            if args.write_prism:
                prism_file = str(filestem + all_time_header[h] + '.'
                                 + geneids[i] + '.prism.txt')
                jmath.R_equals(prism_file, 'filename')
                R('write.km.prism.multi(filename,survival, dead, name)')
            if args.plot_km:
                geneid_clean = hashlib.hash_var(geneids[i])
                km_plot = "%s%s.%s.km.png" % (
                    filestem, all_time_header[h], geneid_clean)
                R(make_color_command(name))
                jmath.R_equals(km_plot, 'filename')
                jmath.R_equals(geneids[i], 'title')
                jmath.R_equals('p_value=%.2g' % all_p_value[h][i], 'sub')
                R('xlab<-""')
                R('ylab<-""')
                if args.xlab:
                    jmath.R_equals(args.xlab , 'xlab')
                if args.ylab:
                    jmath.R_equals(args.ylab, 'ylab')
                if args.title:
                    jmath.R_equals(args.title, 'title')
                #R('bitmap(file=filename,type="png256")')
                jmath.R_fn(
                    "bitmap", file=jmath.R_var("filename"), type="png256",
                     height=1600, width=1600, units="px", res=300)
                R('plot.km.multi(survival, dead, name,'
                  'col=col, main=title, sub=sub, xlab=xlab, ylab=ylab)')
                R('dev.off()')
    #write the output data
    f = sys.stdout
    if args.filestem:
        outfile = args.filestem + '.stats.txt'
        f = file(outfile, 'w')
    print >> f, '\t'.join(headers)
    for i in range(len(geneids)):
        print >> f, '\t'.join(output_data[i])
    f.close()


if __name__ == '__main__':
    main()
