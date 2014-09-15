# Normalization
from Betsy.bie3 import *
import PcaAnalysis
import GeneExpProcessing
import BasicDataTypes
import ArrayPlatforms
import Database

list_files = []
all_modules = [
    
    Module(
        'make_normalize_report',
        [
            GeneExpProcessing.SignalFile,
            GeneExpProcessing.IntensityPlot,
            ArrayPlatforms.ControlPlot,
            PcaAnalysis.PcaPlot,
            ArrayPlatforms.ActbPlot,
            PcaAnalysis.PcaPlot,
            ],
        BasicDataTypes.ReportFile,
        Constraint(
            'preprocess', CAN_BE_ANY_OF,
            ['mas5','agilent','loess','unknown','tcga','rsem'],
            0),
        Constraint("annotate", MUST_BE, "yes", 0),
        Constraint(
            "contents", CAN_BE_ANY_OF, Database.CONTENTS,
            0),

        #SignalFile
        Constraint('quantile_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('combat_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('shiftscale_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('bfrm_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('dwd_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('gene_center', CAN_BE_ANY_OF, ['median', 'mean', 'no'], 0),
        Constraint(
            'gene_normalize', CAN_BE_ANY_OF,
            ['variance', 'sum_of_squares', 'no'], 0),
        Constraint(
            'unique_genes', CAN_BE_ANY_OF,
            ['no','average_genes', 'high_var', 'first_gene'], 0),
        Constraint('platform', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint('group_fc', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint('num_features', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint(
            'duplicate_probe', CAN_BE_ANY_OF,
            ["no", "closest_probe", "high_var_probe"], 0),
        
        # First PcaPlot.
        Constraint('quantile_norm', SAME_AS, 0, 3),
        Constraint('combat_norm', SAME_AS, 0, 3),
        Constraint('shiftscale_norm', SAME_AS, 0, 3),
        Constraint('bfrm_norm', SAME_AS, 0, 3),
        Constraint('dwd_norm', SAME_AS, 0, 3),
        Constraint('gene_center', SAME_AS, 0, 3),
        Constraint('gene_normalize', SAME_AS, 0, 3),
        Constraint('unique_genes', SAME_AS, 0, 3),
        Constraint('platform', SAME_AS, 0, 3),
        Constraint('group_fc', SAME_AS, 0, 3),
        Constraint('num_features', SAME_AS, 0, 3),
        Constraint('duplicate_probe', SAME_AS, 0, 3),
        
        # Second PcaPlot.
        Constraint('quantile_norm', MUST_BE, 'no', 5),
        Constraint('combat_norm', MUST_BE, 'no', 5),
        Constraint('shiftscale_norm', MUST_BE, 'no', 5),
        Constraint('bfrm_norm', MUST_BE, 'no', 5),
        Constraint('dwd_norm', MUST_BE, 'no', 5),
        Constraint('gene_center', MUST_BE, 'no', 5),
        Constraint('gene_normalize', MUST_BE, 'no', 5),
        Constraint('unique_genes', MUST_BE, 'no', 5),
        Constraint('platform', MUST_BE, 'no', 5),
        Constraint('group_fc', MUST_BE, 'no',5 ),
        Constraint('num_features', MUST_BE, 'no', 5),
        Constraint('duplicate_probe', MUST_BE, 'no', 5),
        
        Constraint('contents', SAME_AS, 0, 1),
        Constraint('contents', SAME_AS, 0, 2),
        Constraint('contents', SAME_AS, 0, 3),
        Constraint('contents', SAME_AS, 0, 4),
        Constraint('contents', SAME_AS, 0, 5),
        Constraint("preprocess", SAME_AS, 0, 3),
        Constraint("preprocess", SAME_AS, 0, 4),
        Constraint("preprocess", SAME_AS, 0, 5),
        Consequence('report_type', SET_TO, 'normalize_file'),
        help="make normalize report for mas5,agilent,loess,unknown,tcga,rsem"
        ),
    
    Module(
        'make_normalize_report_rma',
        [
            GeneExpProcessing.SignalFile,
            GeneExpProcessing.IntensityPlot,
            ArrayPlatforms.ControlPlot,
            PcaAnalysis.PcaPlot,
            ArrayPlatforms.ActbPlot,
            PcaAnalysis.PcaPlot,
            ],
        BasicDataTypes.ReportFile,
        
        Constraint('preprocess',MUST_BE,'rma',0),
        Constraint("annotate",MUST_BE,"yes",0),
        Constraint("contents",CAN_BE_ANY_OF,Database.CONTENTS,0),
        
        #SignalFile
        Constraint('quantile_norm', MUST_BE, 'yes', 0),
        Constraint('combat_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('shiftscale_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('bfrm_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('dwd_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('gene_center', CAN_BE_ANY_OF, ['median', 'mean', 'no'], 0),
        Constraint(
            'gene_normalize', CAN_BE_ANY_OF,
            ['variance', 'sum_of_squares', 'no'], 0),
        Constraint(
            'unique_genes', CAN_BE_ANY_OF,
            ['no','average_genes', 'high_var', 'first_gene'], 0),
        Constraint('platform', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint('group_fc', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint('num_features', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint(
            'duplicate_probe', CAN_BE_ANY_OF,
            ["no", "closest_probe", "high_var_probe"], 0),
        
        # First PcaPlot.
        Constraint('quantile_norm', SAME_AS, 0, 3),
        Constraint('combat_norm', SAME_AS, 0, 3),
        Constraint('shiftscale_norm', SAME_AS, 0, 3),
        Constraint('bfrm_norm', SAME_AS, 0, 3),
        Constraint('dwd_norm', SAME_AS, 0, 3),
        Constraint('gene_center', SAME_AS, 0, 3),
        Constraint('gene_normalize', SAME_AS, 0, 3),
        Constraint('unique_genes', SAME_AS, 0, 3),
        Constraint('platform', SAME_AS, 0, 3),
        Constraint('group_fc', SAME_AS, 0, 3),
        Constraint('num_features', SAME_AS, 0, 3),
        Constraint('duplicate_probe', SAME_AS, 0, 3),
        
        # Second PcaPlot.
        Constraint('quantile_norm',MUST_BE,'yes',5),
        Constraint('combat_norm',MUST_BE,'no',5),
        Constraint('shiftscale_norm',MUST_BE,'no',5),
        Constraint('bfrm_norm',MUST_BE,'no',5),
        Constraint('dwd_norm',MUST_BE,'no',5),
        Constraint('gene_center',MUST_BE,'no',5),
        Constraint('gene_normalize',MUST_BE,'no',5),
        Constraint('unique_genes',MUST_BE,'no',5),
        Constraint('platform',MUST_BE,'no',5),
        Constraint('group_fc',MUST_BE,'no',5),
        Constraint('num_features',MUST_BE,'no',5),
        Constraint('duplicate_probe', MUST_BE,'no', 5),
        
        Constraint('contents',SAME_AS,0,1),
        Constraint('contents',SAME_AS,0,2),
        Constraint('contents',SAME_AS,0,3),
        Constraint('contents',SAME_AS,0,4),
        Constraint('contents',SAME_AS,0,5),
        Constraint("preprocess",SAME_AS,0,3),
        Constraint("preprocess",SAME_AS,0,4),
        Constraint("preprocess",SAME_AS,0,5),
        Consequence('report_type',SET_TO,'normalize_file'),
        help="make normalize report for rma"
        ),
    
    Module(
        'make_normalize_report_illumina',
        [
            GeneExpProcessing.SignalFile,
            GeneExpProcessing.IntensityPlot,
            ArrayPlatforms.BiotinPlot,
            PcaAnalysis.PcaPlot,
            ArrayPlatforms.ActbPlot,
            PcaAnalysis.PcaPlot,
            ArrayPlatforms.HousekeepingPlot,
            ArrayPlatforms.Hyb_barPlot,
            ArrayPlatforms.ControlFile
            ],
        BasicDataTypes.ReportFile,
        Constraint("contents",CAN_BE_ANY_OF,Database.CONTENTS,0),
        Constraint('preprocess',MUST_BE,'illumina',0),
        Constraint('annotate',MUST_BE,'yes',0),

        #SignalFile
        Constraint('quantile_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('combat_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('shiftscale_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('bfrm_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('dwd_norm', CAN_BE_ANY_OF, ['yes','no'], 0),
        Constraint('gene_center', CAN_BE_ANY_OF, ['median', 'mean', 'no'], 0),
        Constraint(
            'gene_normalize', CAN_BE_ANY_OF,
            ['variance', 'sum_of_squares', 'no'], 0),
        Constraint(
            'unique_genes', CAN_BE_ANY_OF,
            ['no','average_genes', 'high_var', 'first_gene'], 0),
        Constraint('platform', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint('group_fc', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint('num_features', CAN_BE_ANY_OF, ['yes', 'no'], 0),
        Constraint(
            'duplicate_probe', CAN_BE_ANY_OF,
            ["no", "closest_probe", "high_var_probe"], 0),
        
        # First PcaPlot.
        Constraint('quantile_norm', SAME_AS, 0, 3),
        Constraint('combat_norm', SAME_AS, 0, 3),
        Constraint('shiftscale_norm', SAME_AS, 0, 3),
        Constraint('bfrm_norm', SAME_AS, 0, 3),
        Constraint('dwd_norm', SAME_AS, 0, 3),
        Constraint('gene_center', SAME_AS, 0, 3),
        Constraint('gene_normalize', SAME_AS, 0, 3),
        Constraint('unique_genes', SAME_AS, 0, 3),
        Constraint('platform', SAME_AS, 0, 3),
        Constraint('group_fc', SAME_AS, 0, 3),
        Constraint('num_features', SAME_AS, 0, 3),
        Constraint('duplicate_probe', SAME_AS, 0, 3),
        
        # Second PcaPlot.
        Constraint('quantile_norm',MUST_BE,'no',5),
        Constraint('combat_norm',MUST_BE,'no',5),
        Constraint('shiftscale_norm',MUST_BE,'no',5),
        Constraint('bfrm_norm',MUST_BE,'no',5),
        Constraint('dwd_norm',MUST_BE,'no',5),
        Constraint('gene_center',MUST_BE,'no',5),
        Constraint('gene_normalize',MUST_BE,'no',5),
        Constraint('unique_genes',MUST_BE,'no',5),
        Constraint('platform',MUST_BE,'no',5),
        Constraint('group_fc',MUST_BE,'no',5),
        Constraint('num_features',MUST_BE,'no',5),
        Constraint('duplicate_probe', MUST_BE, 'no', 5),
        
        Constraint('preprocess',MUST_BE,'illumina',3),
        Constraint('preprocess',MUST_BE,'illumina',5),
        Constraint('preprocess',MUST_BE,'illumina',8),
        Constraint('format',MUST_BE,'gct',8),
        Constraint("logged",MUST_BE,'no',8),
        
        Constraint('contents',SAME_AS,0,1),
        Constraint('contents',SAME_AS,0,2),
        Constraint('contents',SAME_AS,0,3),
        Constraint('contents',SAME_AS,0,4),
        Constraint('contents',SAME_AS,0,5),
        Constraint('contents',SAME_AS,0,6),
        Constraint('contents',SAME_AS,0,7),
        Constraint('contents',SAME_AS,0,8),
        Constraint("preprocess",SAME_AS,0,4),
        Consequence('report_type',SET_TO,'normalize_file'),
        help="make normalize report for illumina"),
    
    Module(
        'make_batch_effect_report',
        [
            GeneExpProcessing.SignalFile,
            PcaAnalysis.PcaPlot,
         
            GeneExpProcessing.SignalFile,
            PcaAnalysis.PcaPlot,
         
            GeneExpProcessing.SignalFile,
            PcaAnalysis.PcaPlot,
         
            GeneExpProcessing.SignalFile,
            PcaAnalysis.PcaPlot,
         
            GeneExpProcessing.SignalFile,
            PcaAnalysis.PcaPlot,
         
            GeneExpProcessing.SignalFile,
            PcaAnalysis.PcaPlot
            ],
        BasicDataTypes.ReportFile,
        
        Constraint("quantile_norm",MUST_BE,'no',0),
        Constraint("quantile_norm",SAME_AS,0,1),
        
        Constraint("quantile_norm",MUST_BE,'yes',2),
        Constraint("quantile_norm",SAME_AS,2,3),
        
        Constraint("quantile_norm",MUST_BE,'yes',4),
        Constraint("dwd_norm",MUST_BE,'yes',4),
        Constraint("quantile_norm",SAME_AS,4,5),
        Constraint("dwd_norm",SAME_AS,4,5),
        
        Constraint("quantile_norm",MUST_BE,'yes',6),
        Constraint("bfrm_norm",MUST_BE,'yes',6),
        Constraint("quantile_norm",SAME_AS,6,7),
        Constraint("bfrm_norm",SAME_AS,6,7),
        
        Constraint("quantile_norm",MUST_BE,'yes',8),
        Constraint("shiftscale_norm",MUST_BE,'yes',8),
        Constraint("quantile_norm",SAME_AS,8,9),
        Constraint("shiftscale_norm",SAME_AS,8,9),
        
        Constraint("quantile_norm",MUST_BE,'yes',10),
        Constraint("combat_norm",MUST_BE,'yes',10),
        Constraint("quantile_norm",SAME_AS,10,11),
        Constraint("combat_norm",SAME_AS,10,11),
        
        Consequence("report_type",SET_TO,'batch_effect_remove'),
        help="make batch effect remove report",
        ),
    ]
