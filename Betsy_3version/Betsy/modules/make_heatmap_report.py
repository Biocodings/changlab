#make_cluster_report.py

import os
import shutil
import imghdr
import time
from Betsy import bie3
from Betsy import rulebase
from Betsy import config
from Betsy import module_utils
from Betsy import hash_method


def run(data_node, parameters, user_input, network, num_cores):
    outfile_folder = name_outfile(data_node, user_input)
    outfile = os.path.join(outfile_folder, 'report.html')
    if not os.path.exists(outfile_folder):
        os.mkdir(outfile_folder)
    result_files = []
    filename = data_node.identifier
    new_name = os.path.join(outfile_folder, os.path.split(filename)[-1])
    if os.path.isdir(filename):
        shutil.copytree(filename, new_name)
    else:
        shutil.copyfile(filename, new_name)
    result_files.append(os.path.split(new_name)[-1])
    #write the report.html
    from genomicode import parselib
    from genomicode import htmllib

    def highlight(s):
        return htmllib.SPAN(s, style="background-color:yellow")

    def smaller(s):
        return htmllib.FONT(s, size=-1)

    try:
        lines = []
        w = lines.append
        w("<HTML>")
        title = "Heatmap Results"
        x = parselib.remove_all_tags(title)
        w(htmllib.HEAD(htmllib.TITLE(x)))
        w("<BODY>")
        w(htmllib.CENTER(htmllib.H1(title)))
        w(htmllib.P())
        w(htmllib.A("Methods", href="#methods_clustering"))
        w(htmllib.P())
        w(htmllib.A(htmllib.IMG(height=500,
                                src=result_files[0]),
                    href=result_files[0]))
        w(htmllib.P())
        name = 'Figure 1: In this heatmap, each row contains a signature and each column \
        contains a sample from your data set.'

        w(htmllib.B(name))

        w(htmllib.HR())
        w(htmllib.A("<methods_clustering>", name="methods_clustering"))
        w(htmllib.CENTER(htmllib.H2("Methods")))
        w(htmllib.H3("1.Heatmap File"))
        w('To generate this file, I ran the following analysis:')
        bie3.plot_network_gv(os.path.join(outfile_folder, "network.png"),
                             network)
        w(htmllib.A(htmllib.IMG(height=500,
                                src="network.png"),
                    href="network.png"))
        w(htmllib.P())
        w('I used the following parameters:')
        w(htmllib.H3("1. Heatmap File"))
        rows = []
        x = htmllib.TR(htmllib.TH("Parameter",
                                  align="LEFT") + htmllib.TH("Value",
                                                             align="LEFT"))
        rows.append(x)

        for key in data_node.data.attributes.keys():
            x = htmllib.TR(htmllib.TD(key,
                                      align="LEFT") +
                           htmllib.TD(data_node.data.attributes[key],
                                      align="LEFT"))
            rows.append(x)
        w(htmllib.TABLE("\n".join(rows),
                        border=1,
                        cellpadding=3,
                        cellspacing=0))
        w(htmllib.P())
        # Write out the footer.
        time_str = parselib.pretty_date(time.time())
        #hostname = pretty_hostname()
        w(htmllib.P())
        w(htmllib.HR())
        #w(htmllib.EM(
        #    "This analysis was run on %s on %s. \n" %
        #    (time_str, hostname)))
        w("</BODY>")
        w("</HTML>")
        x = "\n".join(lines) + "\n"
        open(outfile, 'w').write(x)
    except:
        raise
    out_node = bie3.Data(rulebase.ReportFile, **parameters)
    out_object = module_utils.DataObject(out_node, outfile)
    return out_object


def name_outfile(data_node, user_input):
    filename = 'report'
    outfile = os.path.join(os.getcwd(), filename)
    return outfile


def get_out_attributes(parameters, in_nodes):
    return parameters


def make_unique_hash(data_node, pipeline, parameters, user_input):
    identifier = data_node.identifier
    return module_utils.make_unique_hash(identifier, pipeline, parameters,
                                         user_input)


def find_antecedents(network, module_id, data_nodes, parameters,
                     user_attributes):
    data_node = module_utils.get_identifier(network, module_id, data_nodes,
                                            user_attributes)
    return data_node
