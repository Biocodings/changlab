#!/usr/bin/env python

# make_file_layout
# init_paths
#
# align_dataset
# write_dataset
# write_selap_dataset
# write_model
# check_model
# 
# make_model
# predict_subgroups
# 
# summarize_predictions
# summarize_heatmap
# summarize_subgroups


# A SELAP model file contains:
# mu.txt      SELAPver3   nvar x nclust
# sig.txt     SELAPver3   nvar**2 x nclust
# prob.txt    SELAPver3   1 x nclust
# var.txt     this code   Name for the variables (pathways), one per line.
# clust.txt   this code   Name for the clusters, one per line.

import os, sys

def make_file_layout(outpath, num_analyses, penalty):
    from genomicode import filelayout

    outpath = outpath or "."
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    outpath = os.path.realpath(outpath)

    Path, File = filelayout.Path, filelayout.File
    
    # Have only one set of these files for the whole analysis.
    GLOBAL_FILES = [
        File.DATASET("dataset.gct"),
        ]
    # These files are specific to the penalty.
    LOCAL_FILES = [
        File.PREDICTIONS_PCL("predictions.pcl"),
        File.PREDICTIONS_CDT("predictions.cdt"),  # generated by arrayplot
        File.PREDICTIONS_ATR("predictions.atr"),
        File.PREDICTIONS_PNG("predictions.png"),
        Path.ATTIC("attic"),
        Path.SELAP("selap",
            File.SELAP_DATASET("dataset.txt"),
            File.SELAP_PREDICT("predict.txt"),
            File.SELAP_MU("mu.txt"),
            File.SELAP_SIG("sig.txt"),
            File.SELAP_PROB("prob.txt"),
            ),
        File.SMODEL_ZIP("subtype_model.zip")
        ]

    if num_analyses > 1:
        analysis = "PENALTY_%+03d" % penalty
        LOCAL_FILES = [Path.ANALYSIS(analysis, *LOCAL_FILES)]
        GLOBAL_FILES = GLOBAL_FILES + [
            File.GLOBAL_PREDICTIONS_PCL("predictions.%+03d.pcl" % penalty),
            File.GLOBAL_PREDICTIONS_PNG("predictions.%+03d.png" % penalty),
            ]
        GLOBAL_FILES = GLOBAL_FILES + [
            File.SUMMARY("summary.txt"),
            ]
    
    file_layout = Path.OUTPATH(outpath, *(GLOBAL_FILES+LOCAL_FILES))
    return file_layout

def init_paths(file_layout):
    from genomicode import filelayout

    for x in filelayout.walk(file_layout):
        dirpath, dirnames, filenames = x
        if os.path.exists(dirpath):
            continue
        os.mkdir(dirpath)

def align_dataset(MATRIX, model_file):
    import zipfile
    import arrayio
    from genomicode import jmath
    from genomicode import archive

    s2f = archive.unzip_dict(model_file)
    zfile = zipfile.ZipFile(model_file)
    x = zfile.open(s2f["var.txt"]).readlines()
    var_names = [x.strip() for x in x]

    # MATRIX is var x sample.
    assert len(var_names) == MATRIX.nrow(), \
           "Dataset contains %d variables, but model requires %d." % (
        MATRIX.nrow(), len(var_names))
    I = jmath.match(var_names, MATRIX.row_names(arrayio.ROW_ID))
    missing = []
    for i, index in enumerate(I):
        if index == None:
            missing.append(var_names[i])
    assert not missing, (
        "I could not find all the variables in the model.\n"
        "The data set is missing:\n" % ", ".join(missing))
    
    MATRIX = MATRIX.matrix(I, None)
    assert var_names == MATRIX.row_names(arrayio.ROW_ID)
    return MATRIX

def write_dataset(filename, matrix):
    import arrayio
    arrayio.gct_format.write(matrix, open(filename, 'w'))

def write_selap_dataset(file_layout):
    import arrayio
    from genomicode import jmath

    matrix = arrayio.read(file_layout.DATASET)

    # Align the matrix to the SELAP model.

    # Make a matrix for SELAP.
    X_selap = jmath.transpose(matrix._X)
    handle = open(file_layout.SELAP_DATASET, 'w')
    for x in X_selap:
        print >>handle, "\t".join(map(str, x))
    handle.close()

def write_model(filename, file_layout):
    check_model(filename)
    x = open(filename).read()
    open(file_layout.SMODEL_ZIP, 'w').write(x)
    
def check_model(filename):
    # Check the model file to make sure it's complete.  Return a
    # dictionary of the shortname2fullname.
    import zipfile
    import arrayio
    from genomicode import archive

    s2f = archive.unzip_dict(filename)
    zfile = zipfile.ZipFile(filename)

    FILES = [
        "mu.txt",
        "sig.txt",
        "prob.txt",
        "var.txt",
        "clust.txt",
        ]
    for file in FILES:
        assert file in s2f, "Model is missing file: %s." % file

    # Check the consistency of the files in the model.
    tdf = arrayio.tab_delimited_format
    X = tdf.read(zfile.open(s2f["mu.txt"]))
    num_vars, num_subgroups = X.dim()
    X = tdf.read(zfile.open(s2f["sig.txt"]))
    assert X.dim() == (num_vars*num_vars, num_subgroups)
    X = tdf.read(zfile.open(s2f["prob.txt"]))
    assert X.dim() == (1, num_subgroups)
    lines = zfile.open(s2f["var.txt"]).readlines()
    assert len(lines) == num_vars
    lines = zfile.open(s2f["clust.txt"]).readlines()
    assert len(lines) == num_subgroups

def make_model(selap_path, penalty, file_layout, matlab):
    import arrayio
    from genomicode import parselib
    from genomicode import archive
    from genomicode import selap

    print "Generating subgroups with penalty %d." % penalty
    x = selap.selap_make_raw(
        file_layout.SELAP_DATASET, penalty, matlab_bin=matlab,
        selap_path=selap_path, outpath=file_layout.SELAP)
    print x

    # Make sure SELAP ran correctly.
    msg = "Missing file.  SELAPver3 did not run correctly."
    assert os.path.exists(file_layout.SELAP_MU), msg
    assert os.path.exists(file_layout.SELAP_SIG), msg
    assert os.path.exists(file_layout.SELAP_PROB), msg

    # Figure out the number of variables and the number of subgroups.
    X = arrayio.read(file_layout.SELAP_MU)
    num_vars, num_subgroups = X.dim()

    # Make the model file.
    opj = os.path.join
    path = file_layout.SMODEL_ZIP.replace(".zip", "")
    if not os.path.exists(path):
        os.mkdir(path)

    # Move over the files generated by SELAP.
    os.rename(file_layout.SELAP_MU, opj(path, "mu.txt"))
    os.rename(file_layout.SELAP_SIG, opj(path, "sig.txt"))
    os.rename(file_layout.SELAP_PROB, opj(path, "prob.txt"))

    # Generate the var.txt file.
    M = arrayio.read(file_layout.DATASET)
    assert M.nrow() == num_vars
    names = M.row_names(arrayio.ROW_ID)
    assert len(names) == num_vars
    handle = open(opj(path, "var.txt"), 'w')
    for x in names:
        print >>handle, x
    handle.close()
    
    # Generate the clust.txt file.
    # Set the names of the subgroups to a reasonable default.
    x = ["GROUP%s" % x for x in parselib.pretty_range(0, num_subgroups)]
    group_names = x
    handle = open(opj(path, "clust.txt"), 'w')
    for x in group_names:
        print >>handle, x
    handle.close()
    
    archive.zip_path(path, noclobber=False)
    assert os.path.exists(file_layout.SMODEL_ZIP)
    check_model(file_layout.SMODEL_ZIP)

def predict_subgroups(selap_path, file_layout, matlab):
    import zipfile
    import arrayio
    from genomicode import selap
    from genomicode import archive

    print "Predicting subgroups."

    # Write the model files for SELAP.
    s2f = archive.unzip_dict(file_layout.SMODEL_ZIP)
    zfile = zipfile.ZipFile(file_layout.SMODEL_ZIP)
    open(file_layout.SELAP_MU, 'w').write(zfile.read(s2f["mu.txt"]))
    open(file_layout.SELAP_SIG, 'w').write(zfile.read(s2f["sig.txt"]))
    open(file_layout.SELAP_PROB, 'w').write(zfile.read(s2f["prob.txt"]))
    zfile.close()

    # Make sure the dimensions of the model agree with the dimensions
    # of the data set.
    tdf = arrayio.tab_delimited_format
    X_ds = tdf.read(file_layout.SELAP_DATASET)  # nsamples x nvars
    X_mu = tdf.read(file_layout.SELAP_MU)       # nvars x nclust
    #print X_ds.dim(), X_mu.dim()
    assert X_ds.ncol() == X_mu.nrow(), \
           "Dataset contains %d variables, but model requires %d." % (
        X_ds.ncol(), X_mu.nrow())

    x = selap.selap_predict_raw(
        file_layout.SELAP_DATASET, file_layout.SELAP_MU,
        file_layout.SELAP_SIG, file_layout.SELAP_PROB, 
        matlab_bin=matlab, selap_path=selap_path, outpath=file_layout.SELAP)
    print x

    assert os.path.exists(file_layout.SELAP_PREDICT)

def summarize_predictions(file_layout):
    import zipfile
    import arrayio
    from genomicode import archive
    
    # Load the original dataset.  Should be pathway x sample.
    M_data = arrayio.read(file_layout.DATASET)
    sample_names = M_data.col_names(arrayio.COL_ID)

    # Read the predictions.  Will be a sample x probability matrix.
    M_predict = arrayio.read(file_layout.SELAP_PREDICT)
    assert M_predict.nrow() == len(sample_names)
    num_subgroups = M_predict.ncol()

    # Read the cluster names from the model.
    s2f = archive.unzip_dict(file_layout.SMODEL_ZIP)
    assert "clust.txt" in s2f
    zfile = zipfile.ZipFile(file_layout.SMODEL_ZIP)
    #x = [x.strip() for x in zfile.open(s2f["names.txt"]).readlines()]
    x = zfile.open(s2f["clust.txt"]).readlines()
    assert len(x) == num_subgroups, "I have %d subgroups but %d names." % (
        num_subgroups, len(x))
    clust_names = x

    # Save a subgroup x sample matrix.
    handle = open(file_layout.PREDICTIONS_PCL, 'w')
    x = ["Subgroup"] + sample_names
    x = arrayio.tab_delimited_format._clean_many(x)
    print >>handle, "\t".join(x)
    for i in range(num_subgroups):
        probs = M_predict.value(None, i)
        x = [clust_names[i]] + probs
        x = arrayio.tab_delimited_format._clean_many(map(str, x))
        print >>handle, "\t".join(x)
    handle.close()

def summarize_heatmap(python, arrayplot, cluster, file_layout, libpath=[]):
    import subprocess
    import arrayio
    from genomicode import graphlib

    M_predict = arrayio.read(file_layout.PREDICTIONS_PCL)
    nrow, ncol = M_predict.dim()

    # Set the size of the plot.
    x = graphlib.find_wide_heatmap_size(
        nrow, ncol, min_box_width=12, min_box_height=12,
        height_width_ratio=nrow*1.618/ncol)
    xpix, ypix = x

    x = graphlib.plot_heatmap(
        file_layout.PREDICTIONS_PCL, file_layout.PREDICTIONS_PNG, xpix, ypix,
        color="bild", show_colorbar=True, show_grid=True,
        scale=-0.5, gain=1.5, no_autoscale=True,
        gene_label=True, array_label=True, cluster_arrays=True,
        python=python, arrayplot=arrayplot, cluster=cluster, libpath=libpath)
    print x

    # If arrayplot generated predictions.cdt file, remove it.
    # Actually, don't remove it.  It might be required if people want
    # to plot it themselves with other plotting software.  Maybe can
    # move it to the attic.  There may also be a predictions.atr file.
    #if os.path.exists(file_layout.PREDICTIONS_CDT):
    #    os.unlink(file_layout.PREDICTIONS_CDT)

    # Clean up some of the cluster files.
    if os.path.exists(file_layout.PREDICTIONS_CDT):
        src = file_layout.PREDICTIONS_CDT
        x = os.path.split(file_layout.PREDICTIONS_CDT)[1]
        dst = os.path.join(file_layout.ATTIC, x)
        os.rename(src, dst)
    if os.path.exists(file_layout.PREDICTIONS_ATR):
        src = file_layout.PREDICTIONS_ATR
        x = os.path.split(file_layout.PREDICTIONS_ATR)[1]
        dst = os.path.join(file_layout.ATTIC, x)
        os.rename(src, dst)

    # Make sure the signature was generated correctly.  An error could
    # mean that arrayplot.py or cluster is missing.
    assert os.path.exists(file_layout.PREDICTIONS_PNG), \
           "Failed to make predictions heatmap."

def summarize_subgroups(outpath, num_analyses, penalties):
    # Count the number of subgroups for each penalty.
    import arrayio

    if not penalties:
        return

    penalty2subgroups = {}
    for penalty in penalties:
        fl = make_file_layout(outpath, num_analyses, penalty)
        M = arrayio.read(fl.GLOBAL_PREDICTIONS_PCL)
        num_subgroups = M.nrow()
        penalty2subgroups[penalty] = num_subgroups

    # Write output, with penalties sorted from big to small.
    penalties = sorted(penalty2subgroups)
    penalties.reverse()
    fl = make_file_layout(outpath, num_analyses, penalties[0])
    handle = open(fl.SUMMARY, 'w')
    x = ["Penalty", "Num Subgroups"]
    print >>handle, "\t".join(x)
    for penalty in penalties:
        num_subgroups = penalty2subgroups[penalty]
        x = penalty, num_subgroups
        print >>handle, "\t".join(map(str, x))
    handle.close()

def main():
    from optparse import OptionParser, OptionGroup

    # matrix_file should be a pathway x sample file.
    usage = "usage: %prog [options] <dataset>"
    parser = OptionParser(usage=usage, version="%prog 01")

    parser.add_option(
        "", "--selap", dest="selap_path", default=None,
        help="Specify the path to SELAPv3.")
    parser.add_option(
        "", "--matlab", dest="matlab", default="matlab",
        help="Specify the command to run matlab.")
    parser.add_option(
        "", "--python", dest="python", default=None,
        help="Specify the command to run python (optional).")
    parser.add_option(
        "", "--arrayplot", dest="arrayplot", default="arrayplot.py",
        help="Specify the command to run arrayplot.")
    parser.add_option(
        "", "--cluster", dest="cluster", default=None,
        help="Specify the command to run cluster.")
    # This doesn't give as much control over exactly which python
    # version is run.
    #parser.add_option(
    #    "", "--binpath", dest="binpath", action="append", default=[],
    #    help="Add to the binary search path.")
    parser.add_option(
        "", "--libpath", dest="libpath", action="append", default=[],
        help="Add to the Python library search path.")
    parser.add_option(
        "-o", "--outpath", dest="outpath", type="string", default=None,
        help="Save files in this path.")
    parser.add_option(
        "-z", "--archive", dest="archive", action="store_true", default=None,
        help="Archive the raw output.  Helpful for GenePattern.")

    group = OptionGroup(parser, "Model Parameters")
    # Higher numbers have more groups.
    # Range from 0 and lower.
    group.add_option(
        "-p", "--penalty", dest="penalty", default="-33",
        help="Penalty for tuning number of subgroups (default -33).")
    group.add_option(
        "-m", "--model", dest="model_file", default=None,
        help="Specify a file that contains a pre-built subtype model.")
    parser.add_option_group(group)
    
    # Parse the input arguments.
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("Please specify a file with pathway probabilities.")
    filename, = args
    if not os.path.exists(filename):
        parser.error("I could not find file %s." % filename)

    if options.penalty.find(".") >= 0:
        parser.error("Penalties should be integers.")

    if options.libpath:
        sys.path = options.libpath + sys.path
    # Import after the library path is set.
    import arrayio
    from genomicode import genepattern
    from genomicode import archive
    from genomicode import parselib

    genepattern.fix_environ_path()

    # Maximum number of models that someone can create at a time.
    MAX_MODELS = 50
    
    # Allow people to supply more than one penalty.  Parse into a list
    # of ranges.  Penalties must be integers.
    penalties = []
    for (start, end) in parselib.parse_ranges(options.penalty):
        penalties.extend(range(start, end+1))
    assert len(penalties) <= MAX_MODELS, "Too many penalties (max is %d)." % \
           MAX_MODELS
    assert penalties, "At least one penalty must be specified."
    assert not (options.model_file and len(penalties) != 1)
    for p in penalties:
        assert p <= 0, "Penalties should be negative."

    num_analyses = len(penalties)

    # Set up the files.
    file_layout = make_file_layout(options.outpath, num_analyses, penalties[0])
    init_paths(file_layout)

    # Read the matrix and convert to GCT format.
    MATRIX = arrayio.read(filename)
    MATRIX = arrayio.convert(MATRIX, to_format=arrayio.gct_format)

    # Align this matrix to the SELAP model, if it already exists.
    if options.model_file:
        MATRIX = align_dataset(MATRIX, options.model_file)
    # Write out the data set.
    write_dataset(file_layout.DATASET, MATRIX)

    for penalty in penalties:
        # Set up the files.
        file_layout = make_file_layout(options.outpath, num_analyses, penalty)
        init_paths(file_layout)

        # Make the model.
        write_selap_dataset(file_layout)
        if options.model_file:
            write_model(options.model_file, file_layout)
        else:
            make_model(
                options.selap_path, penalty, file_layout, options.matlab)

        # Predict the subgroups.
        predict_subgroups(
            options.selap_path, file_layout, options.matlab)

        # Generate some files for output.
        summarize_predictions(file_layout)
        summarize_heatmap(
            options.python, options.arrayplot, options.cluster, file_layout,
            options.libpath)

        # Archive the SELAP stuff, and any other big files.
        if options.archive:
            print "Archiving results."
            archive.zip_path(file_layout.SELAP, noclobber=False)
            archive.zip_path(file_layout.ATTIC, noclobber=False)

        if num_analyses <= 1:
            continue
        # Now do some cleanup if multiple analyses were requested.

        # If there were multiple penalties specified, make a copy of
        # some files for convenience.
        fl = file_layout
        files_to_copy = [
            (fl.PREDICTIONS_PCL, fl.GLOBAL_PREDICTIONS_PCL),
            (fl.PREDICTIONS_PNG, fl.GLOBAL_PREDICTIONS_PNG),
            ]
        for src, dst in files_to_copy:
            assert os.path.exists(src)
            os.system("cp -p '%s' '%s'" % (src, dst))

        if options.archive:
            archive.zip_path(file_layout.ANALYSIS)
        sys.stdout.flush()

    if num_analyses > 1:
        summarize_subgroups(options.outpath, num_analyses, penalties)

    print "Done."


if __name__ == '__main__':
    main()
