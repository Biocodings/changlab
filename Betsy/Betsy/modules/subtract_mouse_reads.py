from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, antecedents, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import filelib
        from genomicode import parallel
        from Betsy import module_utils

        # This this is I/O heavy, don't use so many cores.  Also,
        # takes 4-5 Gb RAM per process.
        MAX_CORES = 2

        fastq_node, sample_node, summary_node = antecedents
        fastq_path = fastq_node.identifier
        x = module_utils.find_merged_fastq_files(
            sample_node.identifier, fastq_path)
        fastq_files = x
        assert fastq_files, "I could not find any FASTQ files."
        summary_filenames = filelib.list_files_in_path(
            summary_node.identifier, endswith=".matches.txt")
        assert summary_filenames, "No .matches.txt files."
        filelib.safe_mkdir(out_path)

        sample2summary = {}  # sample -> summary_filename
        for filename in summary_filenames:
            # <sample>.matches.txt
            p, f = os.path.split(filename)
            assert f.endswith(".matches.txt")
            sample = f.replace(".matches.txt", "")
            assert sample not in sample2summary
            sample2summary[sample] = filename

        # list of (sample, fastq_file1, fastq_file2, summary_filename,
        #          out_file1, out_file2, subtracted_file1, subtracted_file2)
        jobs = []
        for x in fastq_files:
            sample, pair1_fastq, pair2_fastq = x
            assert sample in sample2summary, \
                   "Missing summary for sample: %s" % sample
            p1, f1 = os.path.split(pair1_fastq)
            if pair2_fastq:
                p2, f2 = os.path.split(pair2_fastq)
                assert p1 == p2
            out1_fastq = os.path.join(out_path, f1)
            sub1_fastq = os.path.join(out_path, "%s.subtracted" % f1)
            out2_fastq = None
            sub2_fastq = None
            if pair2_fastq:
                out2_fastq = os.path.join(out_path, f2)
                sub2_fastq = os.path.join(out_path, "%s.subtracted" % f2)
            x = sample, pair1_fastq, pair2_fastq, sample2summary[sample], \
                out1_fastq, out2_fastq, sub1_fastq, sub2_fastq
            jobs.append(x)

        jobs2 = []  # list of (function, args, keywds)
        for x in jobs:
            sample, pair1_fastq, pair2_fastq, summary_file, \
                    out1_fastq, out2_fastq, sub1_fastq, sub2_fastq = x
            x = summary_file, pair1_fastq, out1_fastq, sub1_fastq
            x = subtract_mouse_reads, x, {}
            jobs2.append(x)
            if pair2_fastq:
                x = summary_file, pair2_fastq, out2_fastq, sub2_fastq
                x = subtract_mouse_reads, x, {}
                jobs2.append(x)

        nc = min(MAX_CORES, num_cores)
        results = parallel.pyfun(jobs2, num_procs=nc, DELAY=0.5)
        assert len(results) == len(jobs2)

        # Make sure the fastq files were generated.
        x1 = [x[4] for x in jobs]
        x2 = [x[5] for x in jobs]
        x = x1 + x2
        x = [x for x in x if x]
        # BUG: If all reads were removed, then this will fail incorrectly.
        filelib.assert_exists_nz_many(x)
            
    
    def name_outfile(self, antecedents, user_options):
        return "subtracted.fastq"


def subtract_mouse_reads(summary_file, in_fastq, out_fastq, sub_fastq):
    from genomicode import filelib
    from genomicode import genomelib

    # List the reads with perfect matches.
    perfect_aligns = {}
    for d in filelib.read_row(summary_file, header=1):
        if int(d.NM) == 0:
            perfect_aligns[d.query_name] = 1

    outhandle = open(out_fastq, 'w')
    subhandle = open(sub_fastq, 'w')
    for x in genomelib.read_fastq(in_fastq):
        title, sequence, quality = x
        x = title
        if x.startswith("@"):
            x = x[1:]
        x = x.split()[0]  # BAM file only contains the first part.
        if x in perfect_aligns:
            genomelib.write_fastq(title, sequence, quality, subhandle)
        else:
            genomelib.write_fastq(title, sequence, quality, outhandle)
