import os
import argparse
import glob
import cdutil
import cdms2

value = 0
cdms2.setNetcdfShuffleFlag(value) ## where value is either 0 or 1
cdms2.setNetcdfDeflateFlag(value) ## where value is either 0 or 1
cdms2.setNetcdfDeflateLevelFlag(value) ## where value is a integer between 0 and 9 included

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
    monthly_files = get_input_files(args, climo=False)  # uses args.input_dir
    output_dir = args.output_dir
    output_dir = os.path.join(output_dir, 'cdat_timeseries_results')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    variables = args.vars
    if variables == []:
        # open the first file and get a list of variables.
        f = cdms2.open(monthly_files[0], 'r')
        variables = list(f.variables.keys())  # f.getVariables() might also work

    print('Using variables: {}'.format(variables))

    start_year, end_year = args.start_yrs, args.end_yrs
    output_files = {}  # a dict of var: FileVariables

    for month_file_nm in monthly_files:
        print('\nUsing {}'.format(month_file_nm))

        with cdms2.open(month_file_nm) as month_file:
            # For each variable in the month_file, add the data for this variable
            # to the appropriate output file
            for var in variables:
                fnm = '{}_{:04d}01_{:04d}12.nc'.format(var, start_year, end_year)
                fnm = os.path.join(output_dir, fnm)

                if var not in output_files:
                    # create a new file
                    # file naming format is FLNS_000201_000212.nc
                    output_files[var] = cdms2.open(fnm, 'w')  # Do we use 'a' instead of 'w'?

                print('Writing timeseries file {} with {}'.format(fnm, var))
                data = month_file(var)
                output_files[var].write(data)

