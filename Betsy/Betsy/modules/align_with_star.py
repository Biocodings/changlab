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

        fastq_node, sample_node, strand_node, reference_node = antecedents
        fastq_files = mlib.find_merged_fastq_files(
            sample_node.identifier, fastq_node.identifier)
        reference_path = reference_node.identifier
        assert mlib.dir_exists(reference_path)
        stranded = mlib.read_stranded(strand_node.identifier)
        filelib.safe_mkdir(out_path)

        metadata = {}
        metadata["tool"] = "STAR %s" % alignlib.get_STAR_version()

        # Do a quick check to make sure the reference is correct.
        # Otherwise, error may be hard to disgnose.
        x = os.path.join(reference_path, "genomeParameters.txt")
        assert filelib.exists_nz(x), "Does not look like STAR reference: %s" %\
               reference_path

        # Figure out the strandedness.
        is_stranded = stranded.stranded != "unstranded"

        # STAR --runThreadN 40 --genomeDir test05 \
        #   --readFilesIn test.fastq/test03_R1_001.fastq \
        #   test.fastq/test03_R2_001.fastq --outFileNamePrefix test06.
        # If unstranded, add --outSAMstrandField intronMotif
        
        STAR = mlib.findbin("STAR")

        # Make a list of the jobs to run.
        jobs = []
        for x in fastq_files:
            sample, pair1, pair2 = x
            out_prefix = "%s." % sample
            sam_filename = os.path.join(
                out_path, "%sAligned.out.sam" % out_prefix)
            log_filename = os.path.join(out_path, "%s.log" % sample)
            x = sample, pair1, pair2, out_prefix, sam_filename, log_filename
            jobs.append(x)

        # Make the commands.
        commands = []
        for x in jobs:
            sample, pair1, pair2, out_prefix, sam_filename, log_filename = x

            full_out_prefix = os.path.join(out_path, out_prefix)

            x = [
                mlib.sq(STAR),
                "--genomeDir", mlib.sq(reference_path),
                "--outFileNamePrefix", full_out_prefix,
                "--runThreadN", num_cores,
                ]
            if not is_stranded:
                x += ["--outSAMstrandField", "intronMotif"]
            x += ["--readFilesIn", mlib.sq(pair1)]
            if pair2:
                x += [mlib.sq(pair2)]
            x = " ".join(map(str, x))
            x = "%s >& %s" % (x, log_filename)
            commands.append(x)
        metadata["commands"] = commands
        metadata["num_cores"] = num_cores

        # STAR takes 28 Gb per process.  Make sure we don't use up
        # more memory than is available on the machine.
        # Defaults:
        # --limitGenomeGenerateRAM   31000000000
        # --outFilterMismatchNmax    10             Num mismatches.
        #nc = mlib.calc_max_procs_from_ram(50, buffer=100, upper_max=num_cores)
        #metadata["num_cores"] = nc
        #parallel.pshell(commands, max_procs=nc, path=out_path)
        
        # Run each job and make sure outfile exists.
        assert len(commands) == len(jobs)
        for i, cmd in enumerate(commands):
            sample, pair1, pair2, out_prefix, sam_filename, log_filename = \
                    jobs[i]
            parallel.sshell(cmd, path=out_path)
            filelib.assert_exists_nz(sam_filename)
            
        # Make sure the analysis completed successfully.
        #x = [x[-2] for x in jobs]  # sam_filename
        #filelib.assert_exists_nz_many(x)
        return metadata


    def name_outfile(self, antecedents, user_options):
        return "alignments.star"