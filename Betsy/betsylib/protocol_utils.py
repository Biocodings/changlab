#protocol_utils.py
import os
import shutil
import Betsy_config
import hash_method
import time
import imghdr

def get_result_folder(protocol,outfiles,parameters,pipeline):
    OUTPUTPATH = Betsy_config.OUTPUTPATH
    filename = os.path.split(outfiles[0][0])[-1]
    if '_BETSYHASH1_' in filename: 
        inputid = '_'.join(filename.split('_')[:-2])
    else:
        inputid = filename
    for i in range(len(outfiles[0])):
        result_files = []
        folder_string = hash_method.hash_parameters(
            inputid,pipeline[0][i],**parameters[0][i])
        folder_name = 'result_folder_BETSYHASH1_'+folder_string
        result_folder = os.path.join(OUTPUTPATH,folder_name)
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)
        for j in range(len(outfiles)):
            if len(outfiles[j]) == 1:
                final_output = os.path.split(outfiles[j][0])[-1]
                shutil.copyfile(outfiles[j][0],
                            os.path.join(result_folder,final_output))
                result_files.append(outfiles[j][0])
            elif len(outfiles[j]) > 1:
                final_output = os.path.split(outfiles[j][i])[-1]
                shutil.copyfile(outfiles[j][i],
                            os.path.join(result_folder,final_output))
                result_files.append(outfiles[j][i])
            elif len(outfiles[j]) == 0:
                result_files.append(None)
        summarize_report(protocol,result_files,result_folder,parameters[0][i],pipeline[0][i])

def format_prolog_query(
    predicate,dataset_id,content,parameters,modules):
    str_parameters = ','.join(parameters)
    output = str('['+dataset_id+'],[' + content + '],[' +
                 str_parameters + '],' + modules)
    query = predicate + '(' + output+')'
    return query

def import_protocol(protocol):
    protocol_name = 'protocols.'+protocol
    mod = __import__(protocol_name)
    mod = getattr(mod, protocol)
    return mod

def pretty_hostname():
    import subprocess
    cmd = "hostname"
    p = subprocess.Popen(
        cmd, shell=True, bufsize=0, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    wh, r = p.stdin, p.stdout
    wh.close()
    hostname = r.read().strip()
    assert hostname, "I could not get the hostname."
    return hostname

def summarize_report(protocol,result_files,result_folder,parameters,pipeline):
    import subprocess
    from genomicode import parselib
    from genomicode import htmllib

    def highlight(s):
        return htmllib.SPAN(s, style="background-color:yellow")
    def smaller(s):
        return htmllib.FONT(s, size=-1)
    cwd = os.getcwd()
    os.chdir(result_folder)
    try:
        lines = []
        w = lines.append
        w("<HTML>")
        title = "Pipeline Report"
        
        x = parselib.remove_all_tags(title)
        w(htmllib.HEAD(htmllib.TITLE(x)))
        w("<BODY>")
        w(htmllib.CENTER(htmllib.H1(title)))

        w(htmllib.H3("I.  Parameters"))

        # Make a table with each parameter.
        rows = []
        x = htmllib.TR(
            htmllib.TH("Parameter", align="LEFT") +
            htmllib.TH("Value", align="LEFT") 
            )
        rows.append(x)
        for key in parameters.keys():
            x = htmllib.TR(
            htmllib.TD(key, align="LEFT") +
            htmllib.TD(parameters[key], align="LEFT") 
            )
            rows.append(x)
        w(htmllib.TABLE("\n".join(rows), border=1, cellpadding=3, cellspacing=0))
        w(htmllib.P())
        w(htmllib.B("Table 1: Parameters set up."))
        w("The parameters of the result files are shown above")
        w(htmllib.P())
       #show the pipeline sequence
        w(htmllib.H3("II.  Pipeline Sequence"))
        w(htmllib.P())
        w("The modules run in the follow sequence:")
        w(htmllib.P())
        w(htmllib.P())
        w('--->'.join(pipeline))
        w(htmllib.P())
        #show all the figures
        module = import_protocol(protocol)
        all_description = {
            'cluster_heatmap':"In this heatmap, each row contains a signature and each column "
                               "contains a sample from your data set.",
             'cluster_file' : 'the expression value of the data set after clustering',
            'signal_file' : 'the expression value of the data set after normalization',
            'pca_plot_in' : 'the pca plot of the data set before normalization',
            'pca_plot_out' : 'the pca plot of the data set after normalization',
            'intensity_plot': 'the intersity of the signal in the data set after normalization',
            'biotin_plot': 'the value of biotin and housekeeping in different sample in the control file',
            'actb_plot': 'the value of ACTB and TUBB in different sample before normalization in the data set',
            'hyb_bar_plot': 'the value of hybridization controls in the data set'         
            }
        #put the image in the same folder
        w(htmllib.H3("III.  Results"))
        output_type = module.OUTPUTS
        for i in range(len(output_type)):
            result = result_files[i]
            if result:
                prob_file = os.path.split(result)[-1]
                if imghdr.what(prob_file) == 'png':
                    w(htmllib.P())
                    w(htmllib.A(htmllib.IMG(height=500,
                                src=prob_file), href=prob_file))
                    w(htmllib.P())
                    name = 'Figure:' + output_type[i]
                    w(htmllib.B(name))
                    w(all_description[output_type[i]])
                    w(htmllib.P())
                else:
                    w(all_description[output_type[i]]+'is shown in: %s'
                      % htmllib.A(prob_file, href=prob_file))

        # Write out the footer.
        time_str = parselib.pretty_date(time.time())
        hostname = pretty_hostname()
        w(htmllib.P())
        w(htmllib.HR())
        w(htmllib.EM(
            "This analysis was run on %s on %s. \n" %
            (time_str, hostname)))
        w("</BODY>")
        w("</HTML>")
        x = "\n".join(lines) + "\n"
        open('report.html', 'w').write(x)
    except:
        raise 
    finally:
        os.chdir(cwd)
