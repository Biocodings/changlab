from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, antecedents, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import config
        from genomicode import parallel
        from genomicode import filelib
        from genomicode import alignlib
        from Betsy import module_utils

        fastq_node, sai_node, reference_node, sample_node = antecedents
        fastq_path = fastq_node.identifier
        assert os.path.exists(fastq_path)
        assert os.path.isdir(fastq_path)
        sai_path = sai_node.identifier
        assert os.path.exists(sai_path)
        assert os.path.isdir(sai_path)
        ref = alignlib.create_reference_genome(reference_node.identifier)
        filelib.safe_mkdir(out_path)

        # Technically, doesn't need the SampleGroupFile, since that's
        # already reflected in the sai data.  But better, because the
        # sai data might not always be generated by BETSY.

        # Find the merged fastq files.
        x = module_utils.find_merged_fastq_files(
            sample_node.identifier, fastq_path)
        fastq_files = x

        # Find the sai files.
        x = filelib.list_files_in_path(sai_path)
        x = [x for x in x if x.lower().endswith(".sai")]
        sai_filenames = x
        assert sai_filenames, "No .sai files."

        # Find the indexed reference genome at:
        # <index_path>/<assembly>.fa
        #x = os.listdir(index_path)
        #x = [x for x in x if x.lower().endswith(".fa")]
        #assert len(x) == 1, "Cannot find bwa index."
        #x = x[0]
        #reference_fa = os.path.join(index_path, x)
        
        bwa = filelib.which_assert(config.bwa)
        # bwa samse -f <output.sam> <reference.fa> <input.sai> <input.fq>
        # bwa sampe -f <output.sam> <reference.fa> <input_1.sai> <input_2.sai>
        #   <input_1.fq> <input_2.fq> >

        # list of (pair1.fq, pair1.sai, pair2.fq, pair2.sai, output.sam)
        # all full paths
        jobs = []
        for x in fastq_files:
            sample, pair1_fq, pair2_fq = x

            # The sai file should be in the format:
            # <sai_path>/<sample>.sai    Single end read
            # <sai_path>/<sample>_1.sai  Paired end read
            # <sai_path>/<sample>_2.sai  Paired end read
            # Look for pair1_sai and pair2_sai.
            pair1_sai = pair2_sai = None
            for sai_filename in sai_filenames:
                p, f = os.path.split(sai_filename)
                s, e = os.path.splitext(f)
                assert e == ".sai"
                if s == sample:
                    assert not pair1_sai
                    pair1_sai = sai_filename
                elif s == "%s_1" % (sample):
                    assert not pair1_sai
                    pair1_sai = sai_filename
                elif s == "%s_2" % (sample):
                    assert not pair2_sai
                    pair2_sai = sai_filename
            assert pair1_sai, "Missing .sai file: %s" % sample
            if pair2_fq:
                assert pair2_sai, "Missing .sai file 2: %s" % sample
            if pair2_sai:
                assert pair2_fq, "Missing .fq file 2: %s" % sample
                
            sam_filename = os.path.join(out_path, "%s.sam" % sample)
            log_filename = os.path.join(out_path, "%s.log" % sample)

            x = sample, pair1_fq, pair1_sai, pair2_fq, pair2_sai, \
                sam_filename, log_filename
            jobs.append(x)

        orientation = sample_node.data.attributes["orientation"]
        assert orientation in ["single", "paired_fr", "paired_rf"]

        # Make a list of bwa commands.
        sq = parallel.quote
        commands = []
        for x in jobs:
            sample, pair1_fq, pair1_sai, pair2_fq, pair2_sai, \
                    sam_filename, log_filename = x
            if orientation == "single":
                assert not pair2_fq
                assert not pair2_sai

            samse = "samse"
            if orientation.startswith("paired"):
                samse = "sampe"

            x = [
                sq(bwa),
                samse,
                "-f", sq(sam_filename),
                sq(ref.fasta_file_full),
                ]
            if orientation == "single":
                x += [
                    sq(pair1_sai),
                    sq(pair1_fq),
                ]
            else:
                y = [
                    sq(pair1_sai),
                    sq(pair2_sai),
                    sq(pair1_fq),
                    sq(pair2_fq),
                    ]
                if orientation == "paired_rf":
                    y = [
                        sq(pair2_sai),
                        sq(pair1_sai),
                        sq(pair2_fq),
                        sq(pair1_fq),
                        ]
                x += y
            x += [
                ">&", sq(log_filename),
                ]
            x = " ".join(x)
            commands.append(x)
            
        parallel.pshell(commands, max_procs=num_cores)

        # Make sure the analysis completed successfully.
        for x in jobs:
            sample, pair1_fq, pair1_sai, pair2_fq, pair2_sai, \
                    sam_filename, log_filename = x
            assert filelib.exists_nz(sam_filename), \
                   "Missing: %s" % sam_filename
    

    def name_outfile(self, antecedents, user_options):
        return "sam.bwa"
        #from Betsy import module_utils
        #original_file = module_utils.get_inputid(antecedents.identifier)
        #return 'bamFiles_' + original_file
