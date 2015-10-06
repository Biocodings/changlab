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
        
        in_file_or_path = in_data.identifier
        module_utils.copytree_or_file_into_tree(in_file_or_path, out_path)

        fa_filenames = module_utils.find_fasta_files(out_path)
        assert fa_filenames, "Could not find reference genome."
        assert len(fa_filenames) == 1, "Found multiple reference genomes."
        reference_filename = fa_filenames[0]
        
        #module_utils.safe_mkdir(out_path)

        # bowtie2-build <ref.fa> <output_stem>
        # Makes files:
        # <output_stem>.[1234].bt2
        # <output_stem>.rev.[12].bt2

        # TODO: Use <ref> instead of <assembly>.
        out_stem = user_options.get("assembly", "genome")

        # Figure out the output stem.
        # Not good, because this is often a weird betsy-defined name.
        #in_path, in_file = os.path.split(in_filename)
        #x = in_file
        #if x.lower().endswith(".fa"):
        #    x = x[:-3]
        #if x.lower().endswith(".fasta"):
        #    x = x[:-6]
        #out_stem = x

        bowtie2_build = module_utils.which_assert(config.bowtie2_build)
        sq = module_utils.shellquote
        cmd = [
            sq(bowtie2_build),
            sq(reference_filename),
            out_stem,
            ]
        
        cwd = os.getcwd()
        try:
            os.chdir(out_path)
            module_utils.run_single(cmd)
        finally:
            os.chdir(cwd)

        # Check to make sure index was created successfully.
        f = os.path.join(out_path, "%s.1.bt2" % out_stem)
        assert module_utils.exists_nz(f)


    def name_outfile(self, antecedents, user_options):
        # Should name outfile based on the assembly.
        return "reference.bowtie2"
