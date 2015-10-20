from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, in_data, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import config
        from Betsy import module_utils
        
        in_filename = in_data.identifier
        module_utils.safe_mkdir(out_path)
        bowtie_build = module_utils.which_assert(config.bowtie_build)

        #time bowtie /data/biocore/tophat/ebwt/hg19 test.fastq >& test.sam

        # bowtie-build <ref.fa> <output_stem>
        # Makes files:
        # <output_stem>.[1234].ebwt
        # <output_stem>.rev.[12].ebwt

        out_stem = user_options.get("assembly", "genome")

        sq = module_utils.shellquote
        cmd = [
            sq(bowtie_build),
            sq(in_filename),
            out_stem,
            ]
        cmd = " ".join(cmd)

        cwd = os.getcwd()
        try:
            os.chdir(out_path)
            module_utils.run_single(cmd)
        finally:
            os.chdir(cwd)

        # Check to make sure index was created successfully.
        f = os.path.join(out_path, "%s.1.ebwt" % out_stem)
        assert module_utils.exists_nz(f)


    def name_outfile(self, antecedents, user_options):
        # Should name outfile based on the assembly.
        return "reference.bowtie"