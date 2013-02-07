#!/usr/bin/env python

platform2gpplatform = {
    "HG_U133A" : "HG_U133A.chip",
    "HG_U133A_2" : "HG_U133A_2.chip",
    "HG_U133_Plus_2" : "HG_U133_Plus_2.chip",
    "Entrez_symbol_human" : "GENE_SYMBOL.chip",
    }

def guess_chip_platform(M):
    # Return the GenePattern chip.platform for this matrix.
    from genomicode import arrayplatformlib
    
    platform = arrayplatformlib.identify_platform_of_matrix(M)
    chipname = platform2gpplatform.get(platform)
    return chipname

DATABASE2GENESET = {
    "positional" : "c1.all.v3.0.symbols.gmt [Positional]",
    "curated" : "c2.all.v3.0.symbols.gmt [Curated]",
    "curated:canonical" : "c2.cp.v3.0.symbols.gmt [Curated]",
    "curated:biocarta" : "c2.cp.biocarta.v3.0.symbols.gmt [Curated]",
    "curated:kegg" : "c2.cp.kegg.v3.0.symbols.gmt [Curated]",
    "curated:reactome" : "c2.cp.reactome.v3.0.symbols.gmt [Curated]",
    "motif" : "c3.all.v3.0.symbols.gmt [Motif]",
    "motif:tfactor" : "c3.tft.v3.0.symbols.gmt [Motif]",
    "computational" : "c4.all.v3.0.symbols.gmt [Computational]",
    "gene_ontology" : "c5.all.v3.0.symbols.gmt [Gene Ontology]",
    "gene_ontology:process" : "c5.bp.v3.0.symbols.gmt [Gene Ontology]",
    }
DEFAULT_DATABASE = "gene_ontology:process"

def format_gene_set_database(database):
    # Valid values for GenePattern gene.set.database:
    # c1.all.v3.0.symbols.gmt [Positional]
    # c2.all.v3.0.symbols.gmt [Curated]
    # c2.cgp.v3.0.symbols.gmt [Curated]        chemical & genetic pertubations
    # c2.cp.v3.0.symbols.gmt [Curated]            canonical pathways
    # c2.cp.biocarta.v3.0.symbols.gmt [Curated]   Biocarta
    # c2.cp.kegg.v3.0.symbols.gmt [Curated]       KEGG
    # c2.cp.reactome.v3.0.symbols.gmt [Curated]   Reactome
    # c3.all.v3.0.symbols.gmt [Motif]
    # c3.mir.v3.0.symbols.gmt [Motif]             miRNA targets
    # c3.tft.v3.0.symbols.gmt [Motif]             transcription factor targets
    # c4.all.v3.0.symbols.gmt [Computational]
    # c4.cgn.v3.0.symbols.gmt [Computational]     cancer gene neighborhoods
    # c4.cm.v3.0.symbols.gmt [Computational]      cancer modules
    # c5.all.v3.0.symbols.gmt [Gene Ontology]
    # c5.bp.v3.0.symbols.gmt [Gene Ontology]      biological process
    # c5.cc.v3.0.symbols.gmt [Gene Ontology]      cellular component
    # c5.mf.v3.0.symbols.gmt [Gene Ontology]      molecular function
    assert database in DATABASE2GENESET, "Unknown database: %s" % database
    return DATABASE2GENESET[database]


def read_cls_file(filename):
    # Only handles categorical CLS files with 2 classes.
    from genomicode import filelib
    
    # Space or tab-delimited format.
    # <num samples> <num classes> 1
    # # <class name 0> <class name 1> ...
    # <0/1 or class name> ...
    handle = filelib.openfh(filename)
    x = [x for x in handle if x.strip()]
    assert len(x) == 3, "CLS file should contain 3 lines."
    line1, line2, line3 = x

    # Parse the first line.
    x = line1.strip().split()
    assert len(x) == 3
    assert x[2] == "1"
    num_samples, num_classes = int(x[0]), int(x[1])

    # Parse the second line.
    x = line2.strip().split()
    assert x
    assert x[0] == "#"
    assert len(x) == num_classes+1
    class_names = x[1:]

    # Parse the third line.
    x = line3.strip().split()
    assert len(x) == num_samples
    classes = x
    for x in classes:
        assert x in class_names or \
            (int(x) >= 0 and int(x) < num_classes)

    return class_names, classes
    
def write_cls_file(outhandle, name0, name1, classes):
    # Only handles categorical CLS files with 2 classes.
    # classes should be a list of 0/1 or class names.
    for x in classes:
        assert x in [0, 1, "0", "1", name0, name1]
    
    if type(outhandle) is type(""):
        outhandle = open(outhandle, 'w')

    # Space or tab-delimited format.
    # <num samples> <num classes> 1
    # # <class name 0> <class name 1> ...
    # <0/1 or class name> ...
    num_samples = len(classes)
    x = [num_samples, 2, 1] + [""]*(num_samples-3)
    print >>outhandle, "\t".join(map(str, x))

    x = ["#", name0, name1] + [""]*(num_samples-3)
    print >>outhandle, "\t".join(map(str, x))

    print >>outhandle, "\t".join(map(str, classes))


def make_cls_file(outhandle, MATRIX, indexes1, count_headers, name1, name2):
    # indexes is a string.
    from genomicode import parselib
    
    if type(outhandle) is type(""):
        outhandle = open(outhandle, 'w')
        
    max_index = MATRIX.ncol()
    num_headers = len(MATRIX._row_names)
    
    assert indexes1 and type(indexes1) is type("")
    name1 = name1 or "group1"
    name2 = name2 or "group2"
    if name1 == name2:
        name1 = "%s-1" % name1
        name2 = "%s-2" % name2

    I = []
    for s, e in parselib.parse_ranges(indexes1):
        if count_headers:
            s, e = s - num_headers, e - num_headers
        assert s >= 1, "Index out of range: %s" % s
        assert e <= max_index, "Index out of range: %s" % e
        s, e = s - 1, min(e, max_index)
        I.extend(range(s, e))

    classes = [1]*MATRIX.ncol()
    for i in I:
        classes[i] = 0
    write_cls_file(outhandle, name1, name2, classes)
    

def main():
    import os
    import argparse
    import subprocess
    import StringIO
    import tempfile
    import zipfile

    import arrayio
    from genomicode import config
    
    parser = argparse.ArgumentParser(description="Do a GSEA analysis.")
    parser.add_argument("expression_file", help="Gene expression file.")
    parser.add_argument("outpath", help="Where to save the files.")
    
    group = parser.add_argument_group(title="Class Labels")
    group.add_argument(
        "--cls_file", default=None, help="Class label file.")
    group.add_argument(
        "--indexes1", default=None,
        help="Which columns in group 1, E.g. 1-5,8 (1-based, "
        "inclusive).  All other samples will be in group 2.")
    group.add_argument(
        "--indexes_include_headers", default=False, action="store_true",
        help="If not given (default), then column 1 is the first column "
        "with data.  If given, then column 1 is the very first column in "
        "the file, including the headers.")
    group.add_argument("--name1", default=None, help="Name for group 1.")
    group.add_argument("--name2", default=None, help="Name for group 2.")

    group = parser.add_argument_group(title="Other Parameters")
    group.add_argument(
        "--platform", default=None,
        help="The platform (GenePattern chip) of the expression data, "
        "e.g. GENE_SYMBOL.chip, HG_U133A_2.chip")
    x = sorted(DATABASE2GENESET)
    x = [x.replace(DEFAULT_DATABASE, "%s (DEFAULT)" % x) for x in x]
    x = ", ".join(x)
    x = "Which database to search.  Possible values are: %s." % x
    group.add_argument("--database", default=DEFAULT_DATABASE, help=x)
    group.add_argument("--database_file", default=None,
        help="Search a GMT or GMX file instead of the default databases.")
    group.add_argument(
        "--no_collapse_dataset", default=False, action="store_true",
        help="See GenePattern documentation.  You probably will not have "
        "to change this.")

    args = parser.parse_args()
    assert os.path.exists(args.expression_file), \
        "File not found: %s" % args.expression_file
    # Must have either the indexes or the cls_file, but not both.
    assert args.cls_file or args.indexes1, (
        "Must provide either CLS file or the indexes for one group.")
    assert not (args.cls_file and args.indexes1), (
        "Cannot provide both a CLS file and the indexes.")
    if args.cls_file:
        assert os.path.exists(args.cls_file), \
            "File not found: %s" % args.cls_file
        assert not args.name1
        assert not args.name2
    assert args.outpath, "Please specify an outpath."
    if not os.path.exists(args.outpath):
        os.mkdir(args.outpath)

    MATRIX = arrayio.read(args.expression_file)
    MATRIX = arrayio.convert(MATRIX, to_format=arrayio.gct_format)

    # Make a CLS file, if necessary.
    if args.cls_file:
        names, classes = read_cls_file(args.cls_file)
        assert len(names) == 2, "I must have 2 classes."
        handle = StringIO.StringIO()
        write_cls_file(handle, names[0], names[1], classes)
        cls_data = handle.getvalue()
    else:
        handle = StringIO.StringIO()
        make_cls_file(
            handle, MATRIX, args.indexes1, args.indexes_include_headers,
            args.name1, args.name2)
        cls_data = handle.getvalue()

    # Figure out the platform.
    platform = args.platform
    if platform is None:
        platform = guess_chip_platform(MATRIX)
    assert platform, "I could not find a platform for this file."
    #print platform

    database_file = None
    if args.database_file:
        database_file= os.path.realpath(args.database_file)
        assert os.path.exists(database_file), (
            "I could not find file: %s" % database_file)
    else:
        gene_set_database = format_gene_set_database(args.database)

    # Set up file names.
    opj = os.path.join
    x = os.path.splitext(os.path.split(args.expression_file)[1])[0]
    x = x.replace(" ", "_")  # GenePattern cannot work with spaces.
    assert x, "empty file name"
    gct_file = "%s.gct" % x
    cls_file = "%s.cls" % x
    out_file = "%s.zip" % x  # GenePattern saves output to <file>.zip.
    gct_full = opj(args.outpath, gct_file)
    cls_full = opj(args.outpath, cls_file)
    out_full = opj(args.outpath, out_file)

    # Write the gene expression and class label files.
    arrayio.gct_format.write(MATRIX, open(gct_full, 'w'))
    open(cls_full, 'w').write(cls_data)

    collapse_dataset = "true"
    if args.no_collapse_dataset:
        collapse_dataset = "false"

    # Set up the analysis.
    params = {
        "expression.dataset" : gct_file,
        "phenotype.labels" : cls_file,
        "chip.platform" : platform,
        "collapse.dataset" : collapse_dataset,
        }
    if database_file:
        params["gene.sets.database.file"] = database_file
    else:
        params["gene.sets.database"] = gene_set_database

    cmd = [
        config.genepattern,
        "-o", ".",
        "GSEA"
        ]
    for (key, value) in reversed(list(params.iteritems())):
        x = ["--parameters", "%s:%s" % (key, value)]
        cmd.extend(x)

    # Run the analysis in the outpath.  GSEA leaves a file
    # "System.out" in the current directory.
    cwd = os.getcwd()
    try:
        os.chdir(args.outpath)
        p = subprocess.Popen(
            cmd, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            close_fds=True)
        p.wait()
    finally:
        os.chdir(cwd)

    error_file = os.path.join(args.outpath, "stderr.txt")
    assert not os.path.exists(error_file), (
        "Error generated by GenePattern:\n%s" % open(error_file).read())

    # Unzip the zipped results in the outpath.
    assert os.path.exists(out_full), "Output file is missing: %s" % out_full
    zfile = zipfile.ZipFile(out_full)
    zfile.extractall(args.outpath)
    os.unlink(out_full)
                
    x = os.path.join(args.outpath, "index.html")
    assert os.path.exists(x), "I could not find the GSEA output: %s" % x
                                    
if __name__ == '__main__':
    main()
