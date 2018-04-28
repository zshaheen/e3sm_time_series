import os
import argparse
import cdutil
import cdms2

value = 0
cdms2.setNetcdfShuffleFlag(value) ## where value is either 0 or 1
cdms2.setNetcdfDeflateFlag(value) ## where value is either 0 or 1
cdms2.setNetcdfDeflateLevelFlag(value) ## where value is a integer between 0 and 9 included


input_dir = '/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/model-output/mon/ens1/v1'
output_dir = '~/e3sm_diags_timeseries'

# os.path.expanduser() is for paths with `~`
input_dir = os.path.abspath(os.path.expanduser(input_dir))
output_dir = os.path.abspath(os.path.expanduser(output_dir))

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

start_year = 2
end_year = 2

start_year = '{:04d}'.format(start_year)
end_year = '{:04d}'.format(end_year)


# h0_file = '20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-12.nc'
monthly_files = [
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-01.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-02.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-03.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-04.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-05.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-06.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-07.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-08.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-09.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-10.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-11.nc',
'20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-12.nc'
]

variables = ['FLNT']
output_files = []  # a list of cdms FileVariables

if variables == []:
    # open the first file and get a list of variables.
    f = cdms2.open(monthly_files[0], 'r')
    variables = list(f.variables.keys())  # f.getVariables() might also work

print('Using variables: {}'.format(variables))

# '''
for month_file_nm in monthly_files:
    pth = os.path.join(input_dir, month_file_nm)
    print('Examining file: {}'.format(pth))
    month_file = cdms2.open(pth)
    # For each variable in the month_file, add the data for this variable
    # to the appropriate output file
    for i, var in enumerate(variables):
        if i >= len(output_files):
            # create a new file
            # file naming format is FLNS_000201_000212.nc
            fnm = '{}_{}01_{}12.nc'.format(var, start_year, end_year)
            fnm = os.path.join(output_dir, fnm)
            output_files.append(cdms2.open(fnm, 'w'))  # O(1)

        data = month_file(var)
        print('Data has shape: {}'.format(data.shape))
        print('WRITING DATA TO A FILE')
        out_file = output_files[i]
        #if data.id in out_file.variables:
        #        data.setAxis(-1,out_file[data.id].getAxis(-1).clone())
        #        data.setAxis(-2,out_file[data.id].getAxis(-2).clone())
        out_file.sync()
        out_file.write(data)
'''
var = variables[0]
fnm = '{}_{}01_{}12.nc'.format(var, start_year, end_year)
fnm = os.path.join(output_dir, fnm)
out_file = cdms2.open(fnm, 'w')
for month_file_nm in monthly_files[:1]:
    pth = os.path.join(input_dir, month_file_nm)
    print('Examining file: {}'.format(pth))
    month_file = cdms2.open(pth)
    data = month_file(var)
    #d = data['FLNT']
    print(data.shape)
    print('WRITING TO FILE')
    out_file.write(data)
'''
