from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, in_data, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import config
        from genomicode import filelib
        from Betsy import module_utils
        
        module_utils.safe_mkdir(out_path)

        in_path = module_utils.unzip_if_zip(in_data.identifier)
        x = filelib.list_files_in_path(in_path)
        x = [x for x in x if x.lower().endswith(".bam")]
        in_filenames = x
        assert in_filenames, "No .bam files."

        samtools = module_utils.which_assert(config.samtools)

        jobs = []  # list of (in_filename, out_filename)
        for in_filename in in_filenames:
            p, f = os.path.split(in_filename)
            out_filename = os.path.join(out_path, f)
            x = in_filename, out_filename
            jobs.append(x)
        
        # Make a list of samtools commands.
        sq = module_utils.shellquote
        commands = []
        for x in jobs:
            in_filename, out_filename = x

            # samtools sort <in_filename> <out_filestem>
            # .bam automatically added to <out_filestem>, so don't
            # need it.
            x = out_filename
            assert x.endswith(".bam")
            x = x[:-4]
            out_filestem = x
            
            x = [
                samtools,
                "sort",
                sq(in_filename),
                sq(out_filestem),
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

