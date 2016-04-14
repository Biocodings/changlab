from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, antecedents, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import config
        from genomicode import filelib
        from genomicode import parallel
        from genomicode import alignlib

        ref_node, gene_node = antecedents
        ref = alignlib.standardize_reference_genome(
            ref_node.identifier, out_path, use_symlinks=True)
        filelib.safe_mkdir(out_path)

        STAR = filelib.which_assert(config.STAR)
        gtf_file = gene_node.identifier
        filelib.assert_exists_nz(gtf_file)
       
        # STAR --runThreadN 40 --runMode genomeGenerate --genomeDir test05 \
        #   --genomeFastaFiles <file.fasta> \
        #   --sjdbGTFfile $GTF

        sq = parallel.quote
        x = [
            sq(STAR),
            "--runThreadN", num_cores,
            "--runMode", "genomeGenerate",
            "--genomeDir", sq(out_path),
            "--genomeFastaFiles", sq(ref.fasta_file_full),
            "--sjdbGTFfile", sq(gtf_file),
            ]
        x = "%s >& out.txt" % " ".join(map(str, x))
        parallel.sshell(x, path=out_path)

        # Check to make sure index was created successfully.
        files = [
            "chrLength.txt",
            "chrNameLength.txt",
            "chrName.txt",
            "chrStart.txt",
            "exonGeTrInfo.tab",
            "exonInfo.tab",
            "geneInfo.tab",
            "Genome",
            "genomeParameters.txt",
            "SA",
            "SAindex",
            "sjdbInfo.txt",
            "sjdbList.fromGTF.out.tab",
            "sjdbList.out.tab",
            "transcriptInfo.tab",
            ]
        x = [os.path.join(out_path, x) for x in files]
        filelib.assert_exists_nz_many(x)


    def name_outfile(self, antecedents, user_options):
        return "reference.star"