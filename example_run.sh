input_dir='/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/model-output/mon/ens1/v1'
#input_dir='~/climo_timeseries_data'
output_dir='~/e3sm_diags_timeseries'
start_year=2
end_year=2
#variables='FLNT FSNTOAC FLUTC'
variables='FLNT'
case_id='20180129.DECKv1b_piControl.ne30_oEC.edison'
#input_files='20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0001-12.nc 20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0002-*nc'

# ex:
# python run_tests.py -i ~/climo_timeseries_data -o ~/e3sm_diags_timeseries -s 2 -e 2 -v FLNT FSNTOAC
# python run_tests.py -i $input_dir -o $output_dir -s $start_year -e $end_year -v $variables --input_files $input_files
set -o xtrace
python run_tests.py -i $input_dir -o $output_dir -s $start_year -e $end_year -v $variables -c $case_id
