#!/usr/bin/env python

# TODO:
# - Should detect version

# Possible states.
S_DONE = "DONE"
S_RUNNING = "RUNNING"
S_BROKEN = "BROKEN?"


def get_clear_priority(info):
    # Return a tuple for sorting based on priority.  Lower number
    # should be cleared first.
    state2p = {
        S_BROKEN : 0,
        S_DONE : 1,
        S_RUNNING : 2,
        }
    assert info.status in state2p
    p = state2p[info.status]
    return p, info.last_accessed


def format_module_summary(info):
    import time
    from genomicode import parselib
    
    if info.status == S_DONE:
        run_time = info.run_time
    elif info.status == S_RUNNING:
        run_time = "RUNNING"
    elif info.status == S_BROKEN:
        run_time = "BROKEN?"
    else:
        raise AssertionError

    time_str = time.strftime("%a %m/%d %I:%M %p", info.time_)
    size_str = parselib.pretty_filesize(info.size)

    x = "[%s]  %s (%s; %s) %s" % (
        time_str, info.module_name, size_str, run_time, info.hash_)
    return x

    
    
def parse_clear_cache(clear_cache):
    multiplier = {
        "k" : 1024,
        "kb" : 1024,
        "m" : 1024**2,
        "mb" : 1024**2,
        "g" : 1024**3,
        "gb" : 1024**3,
        "t" : 1024**4,
        "tb" : 1024**4,
        }
    
    x = clear_cache
    x = x.strip()
    x = x.replace(" ", "")
    x = x.replace(",", "")
    mult = 1
    for k, v in multiplier.iteritems():
        if x.lower().endswith(k):
            x = x[:-len(k)]
            mult = v
            break
    b = int(float(x) * mult)
    return b


def main():
    import os
    import sys
    import time
    import argparse
    import shutil
    from genomicode import parselib
    from genomicode import filelib
    from Betsy import config
    from Betsy import rule_engine_bie3
    from Betsy import module_utils as mlib
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", default=0, action="count")
    parser.add_argument(
        "--running", "--run", dest="running", action="store_true",
        help="Show only running processes.")
    parser.add_argument(
        "--broken", action="store_true",
        help="Show only broken processes.")
    #parser.add_argument(
    #    "--clean_broken", action="store_true",
    #    help="Remove all broken analyses.")
    
    parser.add_argument(
        "--clear_cache",
        help="Clear out old analyses in the cache.  Argument is the "
        "amount of bytes to be cleared.  Examples: 1000, 1Tb, 500G, 1024Mb."
        )
    parser.add_argument(
        "--dry_run", action="store_true",
        help="Used for --clear_acche.  Just show the directories to clear "
        "rather than actually clearing them.")
    

    args = parser.parse_args()
    args.clean_broken = False

    bytes_to_clear = None
    if args.clear_cache:
        bytes_to_clear = parse_clear_cache(args.clear_cache)
        #print "Clearing %d bytes" % bytes_to_clear
    

    output_path = config.OUTPUTPATH
    if not os.path.exists(output_path):
        return
    output_path = os.path.realpath(output_path)

    print "BETSY cache path: %s" % output_path
    print

    # GenericObject with path, size, status, last_accessed.
    path_info = []

    # Don't sort.  Just print as it comes out for speed.
    for x in os.listdir(output_path):
        if x.startswith("tmp"):  # OBSOLETE
            continue
        x = os.path.join(output_path, x)
        if not os.path.isdir(x):
            continue
        path = x

        p, f = os.path.split(path)
        # index_bam_folder__B006__617b92ee4d313bcd0148b1ab6a91b12f
        x = f.split("__")
        if len(x) != 3:
            print "Unrecognized path: %s" % path
            continue
        module_name, version, hash_ = x

        # Format the directory size.
        size = mlib.get_dirsize(path)

        # See if this module is still running.
        f = os.path.join(path, rule_engine_bie3.IN_PROGRESS_FILE)
        IN_PROGRESS = os.path.exists(f)

        if args.running and not IN_PROGRESS:
            continue
        

        # Read the parameter file.
        params = {}
        x = os.path.join(path, rule_engine_bie3.BETSY_PARAMETER_FILE)
        if os.path.exists(x):
            params = rule_engine_bie3._read_parameter_file(x)
        assert params.get("module_name", module_name) == module_name

        # Figure out the state of this module.
        status = None
        start_time = None
        if params:
            status = S_DONE
            start_time = params.get("start_time")
            assert start_time, "Missing: start_time"
            time_ = time.strptime(start_time, rule_engine_bie3.TIME_FMT)
            #time_str = time.strftime("%a %m/%d %I:%M %p", start_time)
            run_time = params.get("elapsed_pretty")
            if not run_time:
                run_time = "unknown"
            #assert run_time, "Missing elapsed_pretty: %s" % path
            #if run_time == "instant":
            #    x = "ran instantly"
            #else:
            #    x = "took %s" % run_time
        elif IN_PROGRESS:
            status = S_RUNNING
            # Get time that path was created.
            time_ = time.localtime(os.path.getctime(path))
            run_time = None
            #time_str = time.strftime("%a %m/%d %I:%M %p", x)
        else:
            # Get time that path was created.
            status = S_BROKEN
            time_ = time.localtime(os.path.getctime(path))
            #time_ = time.localtime(create_time)
            #time_ = time.strftime("%a %m/%d %I:%M %p", x)
            run_time = None

        if args.broken and status != S_BROKEN:
            continue

        # Figure out the last accessed time.
        last_accessed = None   # seconds since epoch
        x = os.path.join(path, rule_engine_bie3.LAST_ACCESSED_FILE)
        if os.path.exists(x):
            last_accessed = os.path.getmtime(x)
        # If I can't find the LAST_ACCESSED_FILE, then use the
        # parameters file.
        x = os.path.join(path, rule_engine_bie3.BETSY_PARAMETER_FILE)
        if not last_accessed and os.path.exists(x):
            last_accessed = os.path.getmtime(x)
        # Otherwise, use the path time.
        if not last_accessed:
            last_accessed = os.path.getmtime(path)

        # Update sizes.
        x = filelib.GenericObject(
            module_name=module_name, path=path, time_=time_, size=size,
            status=status, last_accessed=last_accessed, hash_=hash_,
            run_time=run_time)
        path_info.append(x)

        # Print out the time stamp and state.
        if not args.clear_cache:
            x = format_module_summary(x)
            parselib.print_split(x, prefixn=2)

        if status == S_RUNNING and args.verbose >= 1:
            # Print out the files in the directory.
            for x in os.walk(path):
                dirpath, dirnames, filenames = x
                filenames = [os.path.join(dirpath, x) for x in filenames]

                all_files = []  # tuple of (mod time, relative_file, filename)
                for filename in filenames:
                    file_ = os.path.relpath(filename, path)
                    if file_ == rule_engine_bie3.IN_PROGRESS_FILE:
                        continue
                    mtime = os.path.getmtime(filename)
                    all_files.append((mtime, file_, filename))
                # Sort by decreasing modification time.
                schwartz = [(-x[0], x) for x in all_files]
                schwartz.sort()
                all_files = [x[-1] for x in schwartz]

                for (mtime, relfile, filename) in all_files:
                    x = time.localtime(mtime)
                    mtime = time.strftime("%a %m/%d %I:%M %p", x)
                    x = os.path.getsize(filename)
                    size = parselib.pretty_filesize(x)
                    x = "[%s]  %s (%s)" % (mtime, relfile, size)
                    parselib.print_split(x, prefix1=2, prefixn=4)

        # Print out the metadata.
        metadata = params.get("metadata", {})
        if args.verbose >= 1:
            for key, value in metadata.iteritems():
                if key in ["commands"]:
                    continue
                x = "%s: %s" % (key.upper(), value)
                parselib.print_split(x, prefix1=2, prefixn=4)
        if args.verbose >= 2:
            for x in metadata.get("commands", []):
                x = "COMMAND: %s" % x
                parselib.print_split(x, prefix1=2, prefixn=4)
                #print "  %s" % x

        if status == S_BROKEN and args.clean_broken:
            shutil.rmtree(path)
                
        sys.stdout.flush()


    # Figure out which paths to delete.
    if args.clear_cache:
        assert bytes_to_clear
        
        # Sort the paths by priority.
        x = path_info
        x = [x for x in x if x.status != S_RUNNING]
        schwartz = [(get_clear_priority(x), x) for x in x]
        schwartz.sort()
        x = [x[-1] for x in schwartz]
        # Add up the sizes until I reach the desired output.
        to_delete = []
        num_bytes = 0
        for i in range(len(x)):
            if num_bytes >= bytes_to_clear:
                break
            to_delete.append(x[i])
            num_bytes += x[i].size
        for info in to_delete:
            x = format_module_summary(info)
            parselib.print_split(x, prefixn=2)
            if args.dry_run:
                continue
            shutil.rmtree(info.path)
            i = path_info.index(info)
            path_info.pop(i)

    print
    
    # BUG: Does not account for size in tmp directories.
    x = [x.size for x in path_info]
    total_size = sum(x)
    x = parselib.pretty_filesize(total_size)
    print "Used: %s" % x

    x = os.statvfs(output_path)
    free_size = x.f_bavail*x.f_frsize
    x = parselib.pretty_filesize(free_size)
    print "Free: %s" % x


if __name__ == '__main__':
    main()
