from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, antecedents, out_attributes, user_options, num_cores,
        out_path):
        import os
        from genomicode import filelib
        #from genomicode import parallel
        from genomicode import hashlib
        from Betsy import module_utils as mlib

        #CALLERS = [
        #    "gatk", "platypus", "varscan",
        #    ]
        vcf_paths = [x.identifier for x in antecedents]
        nodes = [x.data for x in antecedents]
        CALLERS = [x.attributes["caller"] for x in nodes]
        assert len(CALLERS) == len(vcf_paths)
        filelib.safe_mkdir(out_path)
        metadata = {}

        # list of (sample, caller, out_vcf_path, in_vcf_file, out_vcf_file)
        jobs = []
        for i, caller in enumerate(CALLERS):
            inpath = vcf_paths[i]
            caller_h = hashlib.hash_var(caller)
            
            vcf_files = filelib.list_files_in_path(
                inpath, endswith=".vcf", toplevel_only=True)
            for file_ in vcf_files:
                # IN_FILE:   <inpath>/<sample>.vcf
                # OUT_FILE:  <out_path>/<caller>.vcf/<sample>.vcf
                p, sample, e = mlib.splitpath(file_)
                assert e == ".vcf"
                out_vcf_path = os.path.join(out_path, "%s.vcf" % caller_h)
                out_vcf_file = os.path.join(out_vcf_path, "%s.vcf" % sample)

                x = filelib.GenericObject(
                    sample=sample, caller=caller,
                    out_vcf_path=out_vcf_path, in_vcf_file=file_,
                    out_vcf_file=out_vcf_file)
                jobs.append(x)
                
        # Make sure the same samples are found in all callers.
        caller2samples = {}
        for j in jobs:
            if j.caller not in caller2samples:
                caller2samples[j.caller] = []
            caller2samples[j.caller].append(j.sample)
        comp_samples = None
        for caller, samples in caller2samples.iteritems():
            samples = sorted(samples)
            if comp_samples is None:
                comp_samples = samples
            assert comp_samples == samples, "%s %s" % (comp_samples, samples)

        for j in jobs:
            filelib.safe_mkdir(j.out_vcf_path)
            os.symlink(j.in_vcf_file, j.out_vcf_file)

        return metadata
            
    
    def name_outfile(self, antecedents, user_options):
        return "variants.vcf"
