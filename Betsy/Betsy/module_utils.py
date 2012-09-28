#module_utils.py
import hash_method
import arrayio
from genomicode import binreg,Matrix,jmath,matrixlib,mplgraph,arrayannot
import os
import read_label_file
import config
import json
import math
from xml.dom.minidom import parseString

"""contain some functions that are called by many modules"""
class Analysis:
    def __init__(self,name,parameters):
        self.name = name
        self.parameters = parameters
        
class DataObject:
    def __init__(self,objecttype,attributes,identifier):
        self.objecttype = objecttype
        self.attributes = attributes
        self.identifier = identifier
        
def get_inputid(identifier):
    old_filename = os.path.split(identifier)[-1]
    old_filename_no_ext = os.path.splitext(old_filename)[-2]
    inputid = old_filename_no_ext.split('_')[-1]
    return inputid

def make_unique_hash(identifier,pipeline,parameters):
    parameters = renew_parameters(parameters,['status'])
    input_file= os.path.split(identifier)[-1]
    new_parameters = parameters.copy()
    new_parameters['filesize'] = os.path.getsize(identifier)
    new_parameters['checksum'] = hash_method.get_input_checksum(identifier)
    hash_result = hash_method.hash_parameters(
        input_file,pipeline,**new_parameters)
    return hash_result


def get_newobjects(outfile,out_objecttype,parameters,objects,single_object):
    parameters = renew_parameters(parameters,['status'])
    attributes = parameters.values()
    new_object = DataObject(out_objecttype,attributes,outfile)
    new_objects = objects[:]
    new_objects.remove(single_object)
    new_objects.append(new_object)
    return new_objects

    
def merge_two_files(A_file,B_file,handle):
    """input two files and merge,write the output to handle"""
    M_A = arrayio.read(A_file)
    M_B = arrayio.read(B_file)
    assert arrayio.tab_delimited_format.is_matrix(M_A)
    assert arrayio.tab_delimited_format.is_matrix(M_B)
    [M_A,M_B] = matrixlib.align_rows(M_A,M_B)
    assert M_A.nrow() > 0, 'there is no common genes between two files'
    X = []
    for i in range(M_A.dim()[0]):
        x = M_A._X[i]+M_B._X[i]
        X.append(x)
    row_names = M_A._row_names
    row_order = M_A._row_order
    col_names = {}
    for name in M_A._col_names:
        if name not in M_B._col_names:
            continue
        newsample_list = []
        for sample in M_B._col_names[name]:
            if sample in M_A._col_names[name]:
                newsample = sample + '_2'
            else:
                newsample = sample
            newsample_list.append(newsample)
        #x = M_A._col_names[name] + M_B._col_names[name]
        x = M_A._col_names[name] + newsample_list 
        col_names[name] = x
    M_c = Matrix.InMemoryMatrix(X,row_names,col_names,row_order)
    #M_c = arrayio.convert(M,to_format=arrayio.pcl_format)
    arrayio.tab_delimited_format.write(M_c,handle)
    
def which(program):
    
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    
    def ext_candidates(fpath):
        yield fpath
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            yield fpath + ext
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            for candidate in ext_candidates(exe_file):
                if is_exe(candidate):
                    return candidate
    return None
        
def format_convert(X):
    data = []
    for i in range(X.dim()[1]):
        data.append(X.value(None,i))
    return data

def write_Betsy_parameters_file(parameters,single_object,pipeline,outfile):
    f = file(os.path.join(os.getcwd(),'Betsy_parameters.txt'),'w')
    if isinstance(single_object,list):
        text = ['Module input:',[(i.objecttype,i.identifier) for i in single_object],
            'Module output:',outfile,
            'Module output parameters:',parameters,'Pipeline module sequence:',
            pipeline]
    else:
        text = ['Module input:',(single_object.objecttype,single_object.identifier),
                'Module output:',outfile,
                'Module output parameters:',parameters,'Pipeline module sequence:',
                pipeline]
    newtext = json.dumps(text,sort_keys=True, indent=4)
    f.write(newtext)
    f.close()
    

def find_object(parameters,objects,objecttype,attribute_key,opt_attribute=None):
    single_object = None
    attribute_keys = attribute_key.split(',') # split the compared parameter key
    compare_attribute = [parameters[i] for i in attribute_keys]
    if opt_attribute:
        compare_attribute.extend(opt_attribute)
    for single_object in objects:
        flag = True
        if objecttype == single_object.objecttype:
            for i in compare_attribute:
                if i not in single_object.attributes:
                    flag=False
            if flag:
                return single_object
    return None

def exists_nz(filename):
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        if size > 0:
            if not os.path.isdir(filename):
                return True
            else:
                if os.listdir(filename):
                    return True
                else:
                    return False
        else:
            return False
    else:
        return False

def plot_line_keywds(filename,keywords,outfile):
    M = arrayio.read(filename)
    header = M.row_names()
    label = M._col_names['_SAMPLE_NAME']
    outfiles=[]
    for keyword in keywords:
        out=keyword+'.png'
        lines= []
        data=[]
        legend_name = []
        for i in range(M.dim()[0]):
            if M.row_names(header[1])[i] == keyword:
                data.append(M.slice()[i])
                legend_name.append(M.row_names(header[0])[i])
        assert len(data)>0,'cannot find the keywords %s in the file %s'%(keywords,filename)
        for i in range(len(data)):
            line = [(j,data[i][j]) for j in range(len(data[i]))]
            lines.append(line)
        fig=mplgraph.lineplot(*lines,legend=legend_name,box_label=label,ylim_min=0,ylabel=keyword,left=0.1)
        fig.savefig(out)
        outfiles.append(out)
    import Image
    img_w_list=[]
    img_h_list=[]
    imgs=[]
    for i in range(len(outfiles)):
        img=Image.open(outfiles[i],'r')
        img_w,img_h=img.size
        img_w_list.append(img_w)
        img_h_list.append(img_h)
        imgs.append(img)
        
    total_w=max(img_w_list)+30
    total_h=sum(img_h_list)+10
    
    background = Image.new('RGBA', (total_w,total_h), (255, 255, 255, 255))
    bg_w,bg_h=background.size
    offset_w = (bg_w-max(img_w_list))/2
    offset_h_list=[]
    for i in range(len(img_h_list)):
        offset_h= bg_h-sum(img_h_list[i:])
        offset_h_list.append(offset_h)
    for img,offset_h in zip(imgs,offset_h_list):
        background.paste(img,(offset_w,offset_h))
    background.save(outfile)
    assert exists_nz(outfile),'the plot_line_keywds fails'
    
def renew_parameters(parameters,key_list):
    newparameters = parameters.copy()
    for key in key_list:
        if key in newparameters.keys():
            del newparameters[key]
    return newparameters
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def download_ftp(host,path,filename):
    from ftplib import FTP
    try:
        ftp = FTP(host)
        ftp.login()
    except Exception,e:
        raise ValueError(e)
    try:
        ftp.cwd(path)
    except FTP.error_perm,x:
        if str(x).find('No such file')>=0:
            raise AssertionError,'cannot find the %s' %path
    filelist = [] #to store all files
    ftp.retrlines('NLST',filelist.append)
    if filename in filelist:
        f = open(filename,'wb')
        ftp.retrbinary('RETR '+filename,f.write)
        f.close()
        ftp.close()
    else:
        ftp.close()
        raise AssertionError,'cannot find %s in %s' %(filename,host)
    
 
def download_dataset(GSEID):
    import tarfile
    #download the tar folder from geo
    host = 'ftp.ncbi.nih.gov'
    GSE_directory = 'pub/geo/DATA/supplementary/series/'+GSEID
    download_rarfile = GSEID+'_RAW.tar'
    download_ftp(host,GSE_directory,download_rarfile)
    #untar the data folder
    GSEID_path = GSEID
    if not tarfile.is_tarfile(download_rarfile):
        raise ValueError('download file is not tar file')
    tar = tarfile.open(download_rarfile)
    tar.extractall(path=GSEID_path)
    tar.close()
    os.remove(download_rarfile)
    assert os.path.exists(GSEID_path),'the download file %s\
                        does not exist'%GSEID_path
    assert len(os.listdir(GSEID_path))>0, 'the untar in \
           download_geo_dataset_GPL %s fails'%GSEID_path
    return GSEID_path

def gunzip(filename):
    import gzip
    if filename.endswith('.gz'):
        newfilename =os.path.join(os.getcwd(),os.path.split(os.path.splitext(filename)[0])[-1])
        #unzip the gz data
        fileObj = gzip.GzipFile(filename, 'rb');
        fileObjOut = file(newfilename, 'wb');
        while 1:
            line = fileObj.readline()
            if line == '':
                break
            fileObjOut.write(line)
        fileObj.close()
        fileObjOut.close()
        assert os.path.exists(newfilename),'unzip the file %s fails'%filename
        return newfilename
    

def high_light_path(network_file,pipeline,out_file):
    f = open(network_file,'r')
    data = f.read()
    f.close()
    dom = parseString(data)
    nodes=dom.getElementsByTagName('node')
    edges=dom.getElementsByTagName('edge')
    for analysis in pipeline:
        for node in nodes:
            nodecontents = node.toxml()
            if analysis in nodecontents:
                node.childNodes[3].attributes['fill'] = '#ffff00'
    for i in range(len(pipeline[:-1])):
        label = '"'+pipeline[i]+' (pp) ' + pipeline[i+1]  +'"'
        for edge in edges:
            edgecontents = edge.toxml()
            if label in edgecontents:
                #edge.childNodes[5].attributes['fill'] = 'ffff66'
                edge.childNodes[5].attributes['width']='4'
                
    xmlstr = dom.toxml('utf-8')
    f = open(out_file, 'w')
    f.write(xmlstr)
    f.close()
    
def convert_gene_list_platform(genes,platform):
    assert platform in platform2attributes,'we cannot convert to the platform %s'%platform
    chip = arrayannot.guess_chip_from_probesets(genes)
    assert chip, 'we cannot guess the platform for the input file'
    in_attribute,in_mart = platform2attributes[chip]
    out_attribute,out_mart = platform2attributes[platform]
    gene_id = ['"'+i+'"' for i in genes]
    R = jmath.start_R()
    jmath.R_equals_vector(gene_id,'gene_id')
    R('library(biomaRt)')
    jmath.R_equals('"'+in_attribute+'"','in_attribute')
    jmath.R_equals('"'+in_attribute+'"','filters')
    jmath.R_equals('"'+in_mart+'"','in_mart')
    R('old=useMart("ensembl",in_mart)')
    jmath.R_equals('"'+out_attribute+'"','out_attribute')
    jmath.R_equals('"'+out_mart+'"','out_mart')
    R('new=useMart("ensembl",out_mart)')
    R('homolog = getLDS(attributes=in_attribute,filters=filters,values=gene_id,mart=old,attributesL=out_attribute,martL=new)')
    homolog = R['homolog']
    old_id = [str(i) for i in homolog[0]]
    human_id = [str(i) for i in homolog[1]]
    return human_id

def convert_to_same_platform(filename1, filename2, platform=None):
    M1 = arrayio.read(filename1)
    platform1 = arrayannot.identify_platform_of_matrix(M1)
    M2 = arrayio.read(filename2)
    platform2 = arrayannot.identify_platform_of_matrix(M2)
    if platform1 == platform2:
        return filename1, filename2
    else:
        import subprocess
        import config
        Annot_path = config.ANNOTATE_MATRIX
        Annot_BIN = which(Annot_path)
        assert Annot_BIN,'cannot find the %s' % Annot_path
        if platform1 == platform:
            filename = filename2
            newfilename1 = filename1
            newfilename2 = 'tmp'
        elif platform2 == platform:
            filename = filename1
            newfilename1 = 'tmp'
            newfilename2 = filename2
        if platform:
            command = ['python', Annot_BIN, '-f', filename, '-o', 'tmp', "--platform",
               platform]
            process = subprocess.Popen(command, shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            error_message = process.communicate()[1]
            if error_message:
                raise ValueError(error_message)
            assert module_utils.exists_nz('tmp'),'the platform conversion fails'
    return newfilename1,newfilename2

platform2attributes = {
             'HG_U133_Plus_2':("affy_hg_u133_plus_2","hsapiens_gene_ensembl"),
             'HG_U133B':("affy_hg_u133b","hsapiens_gene_ensembl"),
             'HG_U133A':("affy_hg_u133a","hsapiens_gene_ensembl"),
             'HG_U133A_2':("affy_hg_u133a_2","hsapiens_gene_ensembl"),
             'HG_U95A':("affy_hg_u95a","hsapiens_gene_ensembl"),
             'HumanHT_12':("illumina_humanht_12","hsapiens_gene_ensembl"),
             'HG_U95Av2':("affy_hg_u95av2","hsapiens_gene_ensembl"),
             'entrez_ID_human':("entrezgene","hsapiens_gene_ensembl"),
             'entrez_ID_symbol_human':("hgnc_symbol","hsapiens_gene_ensembl"),
             'Hu6800':("affy_hugenefl","hsapiens_gene_ensembl"),
             
             'Mouse430A_2':('affy_mouse430a_2',"mmusculus_gene_ensembl"),
             'MG_U74Cv2':('affy_mg_u74cv2',"mmusculus_gene_ensembl"),
             'Mu11KsubB':("affy_mu11ksubb","mmusculus_gene_ensembl"),
             'Mu11KsubA':('affy_mu11ksuba',"mmusculus_gene_ensembl"),
             'MG_U74Av2':("affy_mg_u74av2","mmusculus_gene_ensembl"),
             'Mouse430_2':('affy_mouse430_2',"mmusculus_gene_ensembl"),
             'MG_U74Bv2':('affy_mg_u74bv2',"mmusculus_gene_ensembl"),
             'entrez_ID_mouse':("entrezgene","mmusculus_gene_ensembl"),
             'MouseRef_8':("illumina_mousewg_6_v2","mmusculus_gene_ensembl"),
             'entrez_ID_symbol_mouse':("mgi_symbol","mmusculus_gene_ensembl"),
             
             'RG_U34A':('affy_rg_u34a',"rnorvegicus_gene_ensembl"),
             'RAE230A':('affy_rae230a',"rnorvegicus_gene_ensembl")}

def plot_pca(filename,result_fig,opts='b',legend=None):
    from genomicode import jmath,mplgraph
    import arrayio
    R=jmath.start_R()
    jmath.R_equals("\'"+filename+"\'",'filename')
    M = arrayio.read(filename)
    labels=M._col_names['_SAMPLE_NAME']
    data = M.slice()
    jmath.R_equals(data,'X')
    R('NUM.COMPONENTS <- 2')
    R('S <- svd(X)')
    R('U <- S$u[,1:NUM.COMPONENTS]')
    R('D <- S$d[1:NUM.COMPONENTS]')
    # Project the data onto the first 2 components.
    R('x <- t(X) %*% U %*% diag(D)')
    x1=R['x'][0:M.ncol()]
    x2=R['x'][M.ncol():]
    if len(opts)>1:
        fig=mplgraph.scatter(x1,x2,xlabel='Principal Component 1',
                         ylabel='Principal Component 2',color=opts,legend=legend)
    else:
        fig=mplgraph.scatter(x1,x2,label=labels,xlabel='Principal Component 1',
                         ylabel='Principal Component 2',color=opts)
    fig.savefig(result_fig)
    assert exists_nz(result_fig),'the plot_pca.py fails'