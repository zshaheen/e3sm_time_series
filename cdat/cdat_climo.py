from __future__ import division

import os
import glob
import collections
import cdutil
import cdms2
import numpy
import MV2

value = 0
cdms2.setNetcdfShuffleFlag(value) ## where value is either 0 or 1
cdms2.setNetcdfDeflateFlag(value) ## where value is either 0 or 1
cdms2.setNetcdfDeflateLevelFlag(value) ## where value is a integer between 0 and 9 included


def what_seasons(fnm):
    """
    Given a file in the format:
        case_id.cam.h0.<year>.<month>.nc
    return the season that it belongs to.
    """
    month_to_season = {
        "01": "DJF",
        "02": "DJF",
        "03": "MAM",
        "04": "MAM",
        "05": "MAM",
        "06": "JJA",
        "07": "JJA",
        "08": "JJA",
        "09": "SON",
        "10": "SON",
        "11": "SON",
        "12": "DJF"
    }

    month = fnm[-5:-3]
    # Given *cam.h0.0001.01.nc, return ['01', 'DJF']
    return [month, month_to_season[month]] if month in month_to_season else []

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
    output_dir = os.path.join(output_dir, 'cdat_climo_results')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    variables = args.vars
    case = args.case  # ex: '20180129.DECKv1b_piControl.ne30_oEC.edison'

    first_file_pth = monthly_files[0]
    with cdms2.open(first_file_pth) as f:
        if variables == []:
            variables = list(f.variables.keys())
        # shape = f(variables[-1]).shape

    # A dict of {season: {var: [TransientVariable, count]}}
    # After it's filled, the final files are created from this.
    output_tvars = {}

    print('\nUsing variables: {}'.format(variables))
    for month_file_nm in monthly_files:
        print('\nUsing {}'.format(month_file_nm))
        seasons_of_file = what_seasons(month_file_nm)

        with cdms2.open(month_file_nm) as month_file:
            # For each variable in the month_file, add the data for this variable
            # to the appropriate output file
            for var in variables:
                var_data = month_file(var)
                for season in seasons_of_file:
                    print('Extracting variable {} and computing {} climo'.format(var, season))
                    if season not in output_tvars:
                        output_tvars[season] = {}

                    if var not in output_tvars[season]:
                        output_tvars[season][var] = [None, var_data, 0, 1]  # climo array, that season data for that year, N season to goto climo (how many DJF), N month stored for that year (that DJF)
                    else:
                        # if same year (i.e next month of same season
                        output_tvars[season][var][1] += var_data
                        output_tvars[season][var][3] += 1
                        # otherwise
                        if output_tvars[season][var][0] is None:
                            output_tvars[season][var][0] = var_data/output_tvars[season][var][3]
                            output_tvars[season][var][2] =1
                        else:
                            output_tvars[season][var][0] += var_data/output_tvars[season][var][3]
                            output_tvars[season][var][2] +=1



    # For all of the seasons and months, for all of the variables in them, average them.
    for season in output_tvars:
        for var in output_tvars[season]:
            fnm = '{}_{}_climo.nc'.format(case, season)
            fnm = os.path.join(output_dir, fnm)
            print('Writing climo file with {}: {}'.format(var, fnm))
            with cdms2.open(fnm, 'a') as f:
                data = output_tvars[season][var][0]
                count = output_tvars[season][var][1]
                result = data/count
                result.id = var  # this messes up without it
                f.write(result)

    print('Done creating climo!')
