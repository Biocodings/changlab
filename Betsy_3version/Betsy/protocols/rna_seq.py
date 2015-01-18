#rna_seq.py
from Betsy.protocol_utils import Parameter
import normalize_file
PRETTY_NAME="Gene Expression preprocessing."
COMMON = 'Common Parameters'
NORMALIZE = 'Normalize Parameters'
OPTIONAL = 'Optional Parameters'
ILLUMINA = 'Illumina Normalize Parameters'
CLASS_NEIGHBORS='Class Neighbor Parameters'

RNA = 'RNA Sequence analysis parameters'

CATEGORIES=[COMMON,NORMALIZE,OPTIONAL,CLASS_NEIGHBORS,RNA]



#input  datatype
INPUTS = [
    'RNASeqFile',
    'SamFolder',
    'BamFolder',
    'SampleGroupFile',
    'ClassLabelFile',
    'GeneListFile'
    ]

#output datatype
OUTPUTS = 'SignalFile'

#parameter objects
PARAMETERS=[Parameter('ref',pretty_name='reference species',default_value='human',
                        choices=['human', 'mouse'],category=RNA,
                      description='reference species for BamFolder',datatype='BamFolder'),

            Parameter('format',pretty_name='File Format',default_value='tdf',
                        choices=['tdf', 'gct'],category=COMMON,
                      description='output file format',datatype='SignalFile'),
            Parameter('preprocess',pretty_name='Preprocess',
                         choices=['rsem'],category=COMMON,default_value='rsem',
                         description='preprocess method',datatype='SignalFile'),
            Parameter('missing_algorithm',pretty_name='How to fill missing value',
                      choices=["none", "median_fill", "zero_fill"],category=COMMON,
                      description='method to the fill the missing value',datatype='SignalFile'),
            Parameter('logged',pretty_name='Logged or Not',default_value='yes',
                      choices=['no', 'yes'],category=COMMON,
                      description='signal is logged or not',datatype='SignalFile'),
            Parameter('filter',pretty_name='Filter',
                      default_value='no',choices=['yes','no'],
                      category=COMMON,description='filter the missing value or not',
                      datatype='SignalFile'),
            Parameter('quantile_norm',pretty_name='Quantile', 
                     choices=['yes', 'no'],category=NORMALIZE,
                      description='normalize by quanitle',datatype='SignalFile'),
            Parameter('combat_norm',pretty_name='Combat', 
                     choices=['yes', 'no'],category=NORMALIZE,
                      description='normalize by combat',datatype='SignalFile'),
            Parameter('shiftscale_norm',pretty_name='Shiftscale', 
                     choices=['yes', 'no'],category=NORMALIZE,
                      description='normalize by shiftscale',datatype='SignalFile'),
            Parameter('dwd_norm',pretty_name='Dwd', 
                     choices=['yes', 'no'],category=NORMALIZE,
                      description='normalize by dwd',datatype='SignalFile'),
            Parameter('bfrm_norm',pretty_name='BFRM',
                 choices=['yes', 'no'],category=NORMALIZE,
                      description='normalize by bfrm',datatype='SignalFile'),
            Parameter('predataset',pretty_name='Predataset Process',
                       choices=['yes', 'no'],category=COMMON,
                      description='filter and threshold genes',datatype='SignalFile'),
            Parameter('gene_center',pretty_name='Gene Center', 
                        choices=['mean', 'median', 'no'],
                        category=COMMON,description='gene center method',datatype='SignalFile'),
            Parameter('gene_normalize',pretty_name='Gene Normalize',
                           choices=['variance', 'sum_of_squares', 'no'],
                           category=COMMON,description='gene normalize method',datatype='SignalFile'),
            Parameter('gene_order',pretty_name='Gene Order',
                 choices=["no", "class_neighbors", "gene_list", "t_test_p", "t_test_fdr",
         'diff_ttest','diff_sam','diff_ebayes','diff_fold_change'],
                      category=NORMALIZE,
                      description='gene order',datatype='SignalFile'),
            Parameter('annotate',pretty_name='Annotation',
                                   choices=['yes','no'],category=OPTIONAL,
                      description='how to annotate the output file',datatype='SignalFile'),
            Parameter('unique_genes',pretty_name='Unique Genes',
                         choices=['average_genes', 'high_var', 'first_gene','no'],
                         category=COMMON,description='how to select unique genes',
                      datatype='SignalFile'),
            Parameter('duplicate_probe',pretty_name='Duplicate Probe',
                      choices=['high_var_probe','closest_probe','no'],
                      category=OPTIONAL,description='how to remove duplicate probe',
                      datatype='SignalFile'),
            Parameter('num_features',pretty_name='Select Gene Number',choices=['yes','no'],
                         category=COMMON,description='select num of genes or not',
                      datatype='SignalFile'),
            Parameter('platform',pretty_name='Platform',choices=['yes','no'],category=OPTIONAL,
                      description='output platform',datatype='SignalFile'),
            
            Parameter('group_fc',pretty_name='Group Fold Change',choices=['yes','no'],
                      category=OPTIONAL,
                      description='filter genes by fold change across classes',datatype='SignalFile'),
            Parameter('rename_sample',pretty_name='Rename samples',choices=['yes','no'],
                      category=OPTIONAL,
                      description='Rename sample name',datatype='SignalFile'),
            Parameter('contents',pretty_name='Contents',category=OPTIONAL,
                      choices=normalize_file.CONTENTS, description='output group information',
                      datatype='SignalFile'),
            ###for UserInput
            Parameter('num_factors',pretty_name='Number of Factors',
                           category=OPTIONAL,description='num of factors for bfrm normalization',
                      datatype='UserInput'),
            Parameter('filter_value',pretty_name='Filter missing Value by Percentage',
                           category=OPTIONAL,description='percentage to filter the missing value(0-1)',
                      datatype='UserInput'),
            
            Parameter('gene_select_threshold',pretty_name='Gene Selection Threshold',
                        category=OPTIONAL,
                      description='gene select threshold',datatype='UserInput'),
            Parameter('platform_name',pretty_name='Platform name',
                  choices = ["'HG_U133_Plus_2'", "'HG_U133B'", "'HG_U133A'",
                 "'HG_U133A_2'", "'HG_U95A'", "'HumanHT_12'", "'HumanWG_6'","'HG_U95Av2'",
                 "'Entrez_ID_human'", "'Entrez_symbol_human'", "'Hu6800'",
                 "'Mouse430A_2'", "'MG_U74Cv2'", "'Mu11KsubB'", "'Mu11KsubA'",
                 "'MG_U74Av2'", "'Mouse430_2'", "'MG_U74Bv2'",
                 "'Entrez_ID_mouse'", "'MouseRef_8'", "'Entrez_symbol_mouse'",
                 "'RG_U34A'", "'RAE230A'", 'unknown_platform'],description = 'output platform name',
                      datatype='UserInput',category=OPTIONAL),
            Parameter('num_features_value',pretty_name='Select Gene Number',
                      category=COMMON,description='select num of genes or not',
                      datatype='UserInput'),
            Parameter('group_fc_num',pretty_name='group_fc value',
                      category=COMMON,description='value for group fold change',
                      datatype='UserInput'),
            
            #class neighbors
            Parameter('cn_mean_or_median',pretty_name='cn mean or median',category=CLASS_NEIGHBORS,
                      choices=['mean', 'median'],description='use mean or median for feature selection',
                      datatype='GeneListFile'),
            
            Parameter('cn_ttest_or_snr',pretty_name='cn ttest or snr',category=CLASS_NEIGHBORS,
                      choices=['t_test','snr'],description='use signal-to-noise or t-test to select neighbors',
                      datatype='GeneListFile'),
            
            Parameter('cn_filter_data',choices=['yes','no'],category=CLASS_NEIGHBORS,
                      pretty_name='cn filter data',description='if no, values below will be ignored',
                      datatype='GeneListFile'),

            Parameter('cn_num_neighbors',pretty_name='cn num neighbors',category=CLASS_NEIGHBORS,
                      description='number of neighbors to find',datatype='UserInput'),
            Parameter('cn_num_perm',pretty_name='cn num permutations',category=CLASS_NEIGHBORS,
                      description='number of permutations in permutation test',datatype='UserInput'),
            Parameter('cn_user_pval',pretty_name='cn user pval',category=CLASS_NEIGHBORS,
                      description='user-set significance value for permutation test',datatype='UserInput'),

            Parameter('cn_min_threshold',category=CLASS_NEIGHBORS, pretty_name='cn min threshold',
                      description='minimum threshold for data',datatype='UserInput'),
            Parameter('cn_max_threshold',category=CLASS_NEIGHBORS, pretty_name='cn max threshold',
                     description='maximum threshold for data',datatype='UserInput'), 
            Parameter('cn_min_folddiff',category=CLASS_NEIGHBORS, pretty_name='cn min fold diff',
                     description='minimum fold difference for filtering genes',datatype='UserInput'), 
            Parameter('cn_abs_diff',category=CLASS_NEIGHBORS,pretty_name='cn abs diff',
                     description='minimum absolute difference for filtering genes',datatype='UserInput'),
           ]

