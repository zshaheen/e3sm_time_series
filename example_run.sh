# input_dir='/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/model-output/mon/ens1/v1'
input_dir='~/climo_timeseries_data'
output_dir='~/e3sm_diags_timeseries'
start_year=2
end_year=2
variables='FLNT FSNTOAC'

# ex:
# python run_tests.py -i ~/climo_timeseries_data -o ~/e3sm_diags_timeseries -s 2 -e 2 -v FLNT FSNTOAC
python run_tests.py -i $input_dir -o $output_dir -s $start_year -e $end_year -v $variables
