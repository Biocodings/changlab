#make_normalize_report_rma.py

import os
import shutil
import imghdr
import time
from Betsy import bie3
from Betsy import rulebase
from Betsy import config
from Betsy  import module_utils
from Betsy import hash_method

def run(in_nodes,parameters,user_input, network):
    outfile_folder=name_outfile(in_nodes,user_input)
    outfile = os.path.join(outfile_folder,'report.html')
    if not os.path.exists(outfile_folder):
        os.mkdir(outfile_folder)
    result_files = []
    for index, data_node in enumerate(in_nodes):
        filename = data_node.identifier
        new_name = os.path.join(outfile_folder,os.path.split(filename)[-1])
        #rename one of the pcaplot filename 
        if index == 2:
            new_name = os.path.join(outfile_folder,'after_'+ os.path.split(filename)[-1])
        if os.path.isdir(filename):
            shutil.copytree(filename,new_name)
        else:
            shutil.copyfile(filename,new_name)
        result_files.append(os.path.split(new_name)[-1])   
    data_node1, data_node2, data_node3, data_node4,data_node5, data_node6 = in_nodes
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
        title = "Normalization Results"
        x = parselib.remove_all_tags(title)
        w(htmllib.HEAD(htmllib.TITLE(x)))
        w("<BODY>")
        w(htmllib.CENTER(htmllib.H1(title)))
        w('I generated a file that contains the normalized gene expression values')
        w(htmllib.P())
        w(htmllib.A(result_files[0], result_files[0]))
        w(htmllib.P())
        w(htmllib.A("Methods",href="#methods_normalization"))
        w(htmllib.P())
##        if pipelines[1] == pipelines[2]:
##            w(htmllib.A(htmllib.IMG(height=500,
##                src=result_files[1]), href=result_files[1]))
##        else:
        rows=[]
        x = htmllib.TR(
            htmllib.TD(htmllib.A(htmllib.IMG(height=500,
            src=result_files[1]), href=result_files[1]), align="CENTER") +
            htmllib.TD(htmllib.A(htmllib.IMG(height=500,
            src=result_files[2]), href=result_files[2]), align="CENTER") 
            )
        rows.append(x)
        x = htmllib.TR(
        htmllib.TH("Before", align="CENTER") +
        htmllib.TH("After", align="CENTER") 
        )
        rows.append(x)
        w(htmllib.TABLE("\n".join(rows), border=None, cellpadding=3, cellspacing=0))
        w(htmllib.P())

        w(htmllib.P())
        name = 'Figure 1: This pca plot shows the similarities among your samples'
        w(htmllib.B(name))
        w(htmllib.P())
        w(htmllib.A(htmllib.IMG(height=500,
                src=result_files[3]), href=result_files[3]))
        w(htmllib.P())
        name = 'Figure 2: This boxplot shows the distribution of signal values'
        w(htmllib.B(name))
        w(htmllib.P())
        w(htmllib.A(htmllib.IMG(height=500,
                src=result_files[4]), href=result_files[4]))
        w(htmllib.P())
        name = 'Figure 3: This plot shows the values of ACTB and TUBB genes'
        w(htmllib.B(name))
        w(htmllib.P())
        
        w(htmllib.A(htmllib.IMG(height=500,
                src=result_files[5]), href=result_files[5]))
        name = 'Figure 4: This plot shows the average values control genes'
        w(htmllib.P())
        w(htmllib.B(name))
        
        w(htmllib.HR())
        w(htmllib.A("<methods_normalization>",name="methods_normalization"))
        w(htmllib.CENTER(htmllib.H2("Methods")))
        w(htmllib.H3("1.Normalization File"))
        w('To generate this file, I ran the following analysis:')
        w(htmllib.P())
        bie3.plot_network_gv(os.path.join(outfile_folder,"network.png"), network)
        w(htmllib.A(htmllib.IMG(height=500,
            src="network.png"), href="network.png"))
        
        w('I used the following parameters:')
        rows = []
        x = htmllib.TR(
            htmllib.TH("Parameter", align="LEFT") +
            htmllib.TH("Value", align="LEFT") 
            )
        rows.append(x)
        for key in data_node1.data.attributes.keys():
            x = htmllib.TR(
            htmllib.TD(key, align="LEFT") +
            htmllib.TD(data_node1.data.attributes[key], align="LEFT") 
            )
            rows.append(x)
        w(htmllib.TABLE("\n".join(rows), border=1, cellpadding=3, cellspacing=0))
        w(htmllib.P())
        w(htmllib.H3("2. PCA analysis"))
        w('I made a principal component plot that shows the similarities among your samples.')
        w(htmllib.P())
        w(htmllib.H3("3. Signal distribution"))
        w('I made a box plot that shows the distribution of signal values.')
        w(htmllib.P())
        w(htmllib.H3("4. Control signal"))
        w('I made two plots that show the values of control signal.')
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
    out_node = bie3.Data(rulebase.ReportFile,**parameters)
    out_object = module_utils.DataObject(out_node,outfile)
    return out_object
    
def name_outfile(in_nodes,user_input):
    filename = 'report' 
    outfile = os.path.join(os.getcwd(), filename)
    return outfile

    
def get_out_attributes(parameters,in_nodes):
    return parameters

def make_unique_hash(in_nodes,pipeline,parameters,user_input):
    data_node1, data_node2, data_node3, data_node4,data_node5, data_node6 = in_nodes
    identifier = data_node1.identifier
    return module_utils.make_unique_hash(identifier,pipeline,parameters,user_input)

def find_antecedents(network, module_id,data_nodes,parameters):
    data_node1 = module_utils.get_identifier(network, module_id,
                                            data_nodes,datatype='SignalFile')
    data_node2, data_node3 = module_utils.find_pcaplots(network,data_nodes,module_id,rma=True)
    data_node4 = module_utils.get_identifier(network, module_id, data_nodes,
                                           datatype='IntensityPlot')
    data_node5 = module_utils.get_identifier(network, module_id, data_nodes,
                                           datatype='ActbPlot')
    data_node6 = module_utils.get_identifier(network, module_id, data_nodes,
                                           datatype='ControlPlot')
    return data_node1, data_node2, data_node3, data_node4,data_node5, data_node6


