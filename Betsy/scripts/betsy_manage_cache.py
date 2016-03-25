#!/usr/bin/env python

# TODO:
# - Should detect version
# - Figure out if files are in progress or completed.

def main():
    import os
    import sys
    import time
    import argparse
    from genomicode import parselib
    from Betsy import config
    from Betsy import rule_engine_bie3
    from Betsy import module_utils as mlib
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", default=0, action="count")
    parser.add_argument(
        "--running", action="store_true", help="Show only running processes.")
    args = parser.parse_args()

    output_path = config.OUTPUTPATH
    if not os.path.exists(output_path):
        return
    output_path = os.path.realpath(output_path)

    print "BETSY cache path: %s" % output_path
    print
    
    sizes = []  # sizes of each directory

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
        assert len(x) == 3, path
        module_name, version, hash_ = x

        # Format the directory size.
        size = mlib.get_dirsize(path)
        size_str = parselib.pretty_filesize(size)
        sizes.append(size)

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

        status = None
        start_time = None
        if params:
            start_time = params.get("start_time")
            assert start_time, "Missing: start_time"
            start_time = time.strptime(start_time, rule_engine_bie3.TIME_FMT)

            # Format the time.
            time_str = time.strftime("%a %m/%d %I:%M %p", start_time)
            run_time = params.get("elapsed_pretty")
            assert run_time, "Missing: elapsed_pretty"
            if run_time == "instant":
                x = "ran instantly"
            else:
                x = "took %s" % run_time
            status = "DONE"
        elif IN_PROGRESS:
            # Get time that path was created.
            create_time = os.path.getctime(path)
            x = time.localtime(create_time)
            time_str = time.strftime("%a %m/%d %I:%M %p", x)
            status = "RUNNING"
        else:
            # Get time that path was created.
            create_time = os.path.getctime(path)
            x = time.localtime(create_time)
            time_str = time.strftime("%a %m/%d %I:%M %p", x)
            status = "BROKEN?"

        if status == "DONE":
            x = "[%s]  %s (%s; %s) %s" % (
                time_str, module_name, size_str, run_time, hash_)
        elif status == "RUNNING":
            x = "[%s]  %s (%s; %s) %s" % (
                time_str, module_name, size_str, "RUNNING", hash_)
        elif status == "BROKEN?":
            x = "[%s]  %s (%s; %s) %s" % (
                time_str, module_name, size_str, "BROKEN?", hash_)
        else:
            raise AssertionError
        parselib.print_split(x, prefixn=2)

        if status == "RUNNING" and args.verbose >= 1:
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
        sys.stdout.flush()

    print
    
    # BUG: Does not account for size in tmp directories.
    total_size = sum(sizes)
    x = parselib.pretty_filesize(total_size)
    print "Total size: %s" % x

    x = os.statvfs(output_path)
    free_size = x.f_bavail*x.f_frsize
    x = parselib.pretty_filesize(free_size)
    print "Free space: %s" % x
    


if __name__ == '__main__':
    main()
