from Module import AbstractModule

class Module(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self)

    def run(
        self, network, in_data, out_attributes, user_options, num_cores,
        out_path):
        #import shutil
        #shutil.copyfile(in_data.identifier, outfile)
        import os
        os.symlink(in_data.identifier, out_path)


    def name_outfile(self, antecedents, user_options):
        #from Betsy import module_utils
        #original_file = module_utils.get_inputid(antecedents.identifier)
        #filename = 'SignatureScore_' + original_file
        #return filename
        return "scoresig"