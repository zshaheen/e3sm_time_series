import os
import subprocess
import glob
import cdms2
import cdutil

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

        files.sort()
    
        if climo:
            # Remove the last file, which is *h0.e_yr-12.nc, since we don't need the 12th month
            if len(files) >= 1:
                files.pop()

    print('Using files:')
    for f in files:
        print(f)
    
    # Check that the required number of files were given
    expected_files = 12*(e_yr-s_yr+1)
    if len(files) != expected_files:
        msg = 'We expected {} files, but only found {} for the years from {} to {}.'
        raise Exception(msg.format(expected_files, len(files), s_yr, e_yr))

    return files

def run(args):
    monthly_files = get_input_files(args, climo=True)  # uses args.input_dir
    output_dir = args.output_dir
    output_results_dir = os.path.join(output_dir, 'cdat_climo_results')
    if not os.path.exists(output_results_dir):
        os.mkdir(output_results_dir)

    case = args.case  # ex: '20180129.DECKv1b_piControl.ne30_oEC.edison'

    cdutil_seasons = {
        'ANN': cdutil.ANNUALCYCLE,
        'DJF': cdutil.DJF,
        'MAM': cdutil.MAM,
        'JJA': cdutil.JJA,
        'SON': cdutil.SON,
        '01': cdutil.JAN,
        '02': cdutil.FEB,
        '03': cdutil.MAR,
        '04': cdutil.APR,
        '05': cdutil.MAY,
        '06': cdutil.JUN,
        '07': cdutil.JUL,
        '08': cdutil.AUG,
        '09': cdutil.SEP,
        '10': cdutil.OCT,
        '11': cdutil.NOV,
        '12': cdutil.DEC
    }
    seasons = list(cdutil_seasons.keys())
    # seasons = ['12', 'DJF', 'ANN']
    # Ex: {'01': '20180129.DECKv1b_piControl.ne30_oEC.edison_01_climo.nc', ... }
    output_files_names = {s: os.path.join(output_results_dir, '{}_{}_climo.nc'.format(case, s)) for s in seasons}
    output_files = {s: cdms2.open(output_files_names[s], 'a') for s in output_files_names}

    variables = args.vars
    if variables == []:
        first_file_pth = monthly_files[0]
        with cdms2.open(first_file_pth) as f:
            variables = list(f.variables.keys())

    combined_file_name = 'combined.nc'
    combined_file_name = os.path.join(output_dir, combined_file_name)
    cmd = 'ncrcat -O {} {}'  # The -O is to clobber existing combined files.
    cmd = cmd.format(' '.join(monthly_files), combined_file_name)
    print('\nCombining files into {}'.format(combined_file_name))
    run_cmd(cmd)

    with cdms2.open(combined_file_name) as combined_file:
        for v in variables:
            input_var = combined_file(v)
            for s in seasons:
                out_file = output_files[s]
                climo = cdutil_seasons[s].climatology(input_var)
                out_file.write(climo)
