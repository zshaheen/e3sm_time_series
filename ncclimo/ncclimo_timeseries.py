import os
import subprocess
import glob

def get_input_files(args, climo=True):
    """
    Given the input arguments, return the list of files
    to be opened to create a climatology.
    """
    files = []

    # Use the explicitly defined files from the user
    if args.input_files:
        for input_file in args.input_files:
            input_dir = os.path.expanduser(args.input_dir)
            pth = os.path.join(input_dir, input_file)
            for file_found in glob.glob(pth):
                files.append(file_found)

    else:
        # Otherwise, use start and end year, along with case, to get the files
        s_yr, e_yr, case = args.start_yrs, args.end_yrs, args.case

        if climo:
            # Add the last month of the last year
            fnm = '{}.cam.h0.{:04d}-12.nc'.format(case, s_yr-1)
            fnm = os.path.join(args.input_dir, fnm)
            if os.path.exists(fnm):
                files.append(fnm)

        # Add everything from s_yr to e_yr.
        # +1 is because e_yr is inclusive.
        for yr in range(s_yr, e_yr+1):
            # glob only gets files that exist, so no need to check for that
            found_files = glob.glob(os.path.join(args.input_dir, '{}.cam.h0.{:04d}*nc'.format(case, yr)))
            files.extend(found_files)

        if climo:
            # Remove the last file, which is *h0.e_yr-12.nc, since we don't need the 12th month
            if len(files) >= 1:
                files.pop()

    print('Using files:')
    files.sort()
    for f in files:
        print(f)
    
    # Check that the required number of files were given
    expected_files = 12*(e_yr-s_yr+1)
    if len(files) != expected_files:
        msg = 'We expected {} files, but only found {} for the years from {} to {}.'
        raise Exception(msg.format(expected_files, len(files), s_yr, e_yr))

    return files

def run_cmd(cmd):
    """
    Run a command while printing and returning the stdout and stderr
    """
    print('+ {}'.format(cmd))
    if isinstance(cmd, str):
        cmd = cmd.split()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    print(output)
    print(err)
    return output, err

def run(args):
    output_dir = args.output_dir
    output_dir = os.path.join(output_dir, 'ncclimo_timeseries_results')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    start_year = args.start_yrs
    end_year = args.end_yrs

    variables = ','.join(v for v in args.vars)
    # case = args.case  # '20180129.DECKv1b_piControl.ne30_oEC.edison'
    input_files = get_input_files(args, climo=False)
    input_files = ' '.join(input_files)

    cmd = 'ncclimo --vars={} --start={} --end={} --output={} {}'
    cmd = cmd.format(variables, start_year, end_year, output_dir, input_files)
    run_cmd(cmd)

