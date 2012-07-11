#arrayannot.py

import os
from genomicode import filelib
import Betsy_config
import re

GUESS_CHIP_CHIP2PSID = None

def guess_chip(filename):
    import arrayio
    from arrayio import const
    
    global GUESS_CHIP_CHIP2PSID
    if not GUESS_CHIP_CHIP2PSID:
        chip2psid = {}  # chip -> psid -> 1
        psid2chip = Betsy_config.PSID2CHIP
        assert os.path.exists(psid2chip),'the %s does not exisits'%psid2chip
        for d in filelib.read_row(psid2chip, "chip:s psid:s llid:s"):
            chip2psid.setdefault(d.chip, {})[d.psid] = 1
        # Make a HG_U133AB chip, if the data set is a combination of them both.
        chip2psid = chip2psid.copy()
        chip2psid["HG_U133AB"] = {}
        for chip in ["HG_U133A", "HG_U133B"]:
            for psid in chip2psid[chip]:
                chip2psid["HG_U133AB"][psid] = 1
        GUESS_CHIP_CHIP2PSID = chip2psid
    chip2psid = GUESS_CHIP_CHIP2PSID

    # Read the probe sets from the file.
    #handle = filelib.read_cols(filelib.openfh(filename))
    #header = handle.next()
    #assert header[:4] == [
    #    "Probe.Set.ID", "Description", "LocusLink", "Gene.Symbol"]
    #probesets = [cols[0] for cols in handle]
    #probesets = {}.fromkeys(probesets)
    DATA = arrayio.read(filename)
    x = DATA.row_names(const.ROW_ID)
    probesets = {}.fromkeys(x)

    # Make a list of all the chips that contain every probeset in the
    # data set.
    possible_chips = []
    for chip in chip2psid:
        for psid in probesets:
            if psid not in chip2psid[chip]:
                break
        else:
            possible_chips.append(chip)
    assert possible_chips, "No match"

    # Sort the chips by size, from smallest to largest.
    schwartz = [(len(chip2psid[chip]), chip) for chip in possible_chips]
    schwartz.sort()
    possible_chips = [x[-1] for x in schwartz]

    # Choose the smallest chip that contains all these probe sets.
    return possible_chips[0]

def hash_chipname(filename):
    x = os.path.split(filename)[1]
    x = x.replace(".gz", "")
    x = x.replace(".csv", "")
    x = x.replace(".annot", "")
    x = x.replace("_annot", "")
    x = x.replace("-", "_")
    version = 0
    m = re.search(r".na(\d+)",x)
    if m:
        version = m.group(1)
        x = x.replace(m.group(0),'')
    return x,version

def chipname2filename(chipname):
    filename = chipname2filename_affy(chipname)
    if not filename:
        filename = chipname2filename_illu(chipname)
    return filename

def chipname2filename_illu(chipname):
    filename = None
    path = Betsy_config.ANNOT_DATA_ILLU
    assert os.path.exists(path),'%s does not exist'%path
    for file in os.listdir(path):
        if chipname in file:
            filename = os.path.join(path, file)
    return filename

def chipname2filename_affy(chipname):
    filename = None
    path = Betsy_config.ANNOT_DATA_AFFY
    assert os.path.exists(path),'%s does not exist'%path
    chip2file = {}
    for file in os.listdir(path):
        filename1 = os.path.join(path, file)
        chipname1,version = hash_chipname(filename1)
        if chipname1 in chip2file.keys():
            if version > chip2file[chipname1][0]:
                chip2file[chipname1] = (version,filename1)
        else:
            chip2file[chipname1] = (version,filename1)
    if chipname in chip2file.keys():
        version,filename = chip2file[chipname]
    return filename
