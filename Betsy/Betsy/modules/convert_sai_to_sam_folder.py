from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, antecedents, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import parallel
        from genomicode import filelib
        from genomicode import alignlib
        from Betsy import module_utils as mlib

        fastq_node, sai_node, orient_node, sample_node, reference_node = \
                    antecedents
        fastq_files = mlib.find_merged_fastq_files(
            sample_node.identifier, fastq_node.identifier)
        sai_path = sai_node.identifier
        assert mlib.dir_exists(sai_path)
        orient = mlib.read_orientation(orient_node.identifier)
        ref = alignlib.create_reference_genome(reference_node.identifier)
        filelib.safe_mkdir(out_path)
        metadata = {}
        metadata["tool"] = "bwa %s" % alignlib.get_bwa_version()

        # Technically, doesn't need the SampleGroupFile, since that's
        # already reflected in the sai data.  But better, because the
        # sai data might not always be generated by BETSY.

        # Find the merged fastq files.

        # Find the sai files.
        sai_filenames = filelib.list_files_in_path(
            sai_path, endswith=".sai", case_insensitive=True)
        assert sai_filenames, "No .sai files."

        bwa = mlib.findbin("bwa")
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
                p, s, e = mlib.splitpath(sai_filename)
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

        orientation = orient.orientation
        #orientation = sample_node.data.attributes["orientation"]
        assert orientation in ["single", "paired_fr", "paired_rf"]

        # Make a list of bwa commands.
        sq = mlib.sq
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
        metadata["commands"] = commands
        metadata["num_cores"] = num_cores
        parallel.pshell(commands, max_procs=num_cores)

        # Make sure the analysis completed successfully.
        x = [x[-2] for x in jobs]
        filelib.assert_exists_nz_many(x)
        
        return metadata
    

    def name_outfile(self, antecedents, user_options):
        return "bwa.sam"
