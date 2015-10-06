from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, in_data, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import filelib
        from Betsy import module_utils

        module_utils.safe_mkdir(out_path)

        raise NotImplementedError
        # Can be file or folder.  Return a full path to the FASTA file.
        reference_filename = module_utils.find_reference_genome(
            in_data.identifier)
        
        in_path = module_utils.unzip_if_zip(in_data.identifier)
        x = filelib.list_files_in_path(in_path)
        x = [x for x in x if x.lower().endswith(".bam")]
        in_filenames = x
        assert in_filenames, "No .bam files."

        # java -Xmx5g -jar MarkDuplicates.jar
        #   I=<input.sam or .bam> O=<output.bam> 
        #   METRICS_FILE=metricsFile CREATE_INDEX=true 
        #   VALIDATION_STRINGENCY=LENIENT REMOVE_DUPLICATES=true
        picard_jar = module_utils.find_picard_jar("MarkDuplicates")

        jobs = []  # list of (in_filename, out_filename)
        for in_filename in in_filenames:
            p, f = os.path.split(in_filename)
            out_filename = os.path.join(out_path, f)
            x = in_filename, out_filename
            jobs.append(x)
        
        # Make a list of commands.
        sq = module_utils.shellquote
        commands = []
        for x in jobs:
            in_filename, out_filename = x

            x = [
                "java", "-Xmx5g",
                "-jar", sq(picard_jar),
                "I=%s" % sq(in_filename),
                "O=%s" % sq(out_filename),
                "METRICS_FILE=metricsFile",
                #"CREATE_INDEX=true",
                "VALIDATION_STRINGENCY=LENIENT",
                "REMOVE_DUPLICATES=true",
                ]
            x = " ".join(x)
            commands.append(x)
            
        module_utils.run_parallel(commands, max_procs=num_cores)

        # Make sure the analysis completed successfully.
        for x in jobs:
            in_filename, out_filename = x
            assert module_utils.exists_nz(out_filename), \
                   "Missing: %s" % out_filename

    
    def name_outfile(self, antecedents, user_options):
        #from Betsy import module_utils
        #original_file = module_utils.get_inputid(antecedents.identifier)
        #filename = 'bamFiles_sorted' + original_file
        #return filename
        return "bam"


