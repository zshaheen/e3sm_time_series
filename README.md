# E3SM Timeseries and climatology stuff

## Problem statement
The goal of this demo is to create both the **timeseries** and **climatology** given a set of monthly model data. We compare `cdms2` with `nclimo` to find the most performant one.

## Model files, climatology, and timeseries

* We are using the model files (`h0` files) located at `/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/` on `acme1`.
  * An example output file is `20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0001-01.nc`. The format is `*.h0.<year>-<month>.nc`. So in the example, the data of the first month of the first year.
  * `/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/model-output/mon/ens1/v1/` has 6000 files. The years are in the range `[0001, 0500]`, and the months are in the range `[01, 12]`.

* The climatology is a set of 17 files: `*_01.nc`, `*_02.nc`, ..., `*_12.nc`, `*_ANN.nc`, ..., `*_SON.nc`.
  * So `*_01.nc` is the mean for January, while `*_ANN.nc` is the annual mean. Files with `DJF`, `MAM`, `JJA`, and `SON` are seasonal means.
* Timeseries files are files with one or more variable per file. It's just all of the monthly files put into one huge file.
   * Ex: On `acme1`, we have `/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/time-series/mon/ens1/v1/FLNS_000101_050012.nc`
       * In this time-series file, the format is `FLNS_<year><month>_<year><month>.nc`
           * So `FLNS_000101_050012.nc`, the data from 01 (Jan) of the first year (0001) to 12(Dec) of the 500th year (500) are concatenated.
           * So there are 6000 individual means for FLNS. The shape is `(6000, lat, lon)`.

## ncclimo
Information taken from [here](https://acme-climate.atlassian.net/wiki/spaces/SIM/pages/31129737/Generate+Regrid+and+Split+Climatologies+climo+files+with+ncclimo+and+ncremap).

`ncclimo` takes monthly or annual timeseries of files and produces monthly means, seasonal means, and/or annual means. In timeseires reshaping mode, `ncclimo` will split the input data timeseires into per-variable files spanning the entire period.

### Creating climatology

`ncclimo -s=start_yr -e=end_yr -c=run_id -i=drc_in -o=drc_out`
`ncclimo --start=start_yr --end=end_yr --case=run_id --input=drc_in --output=drc_out`

`-C` for climatology mode. `mth` for monthly is default, you can use `ann` for annual.
* For this example, we don't set this value. So it defaults to `-C mth`, because the input data is split into monthly data

`-c` case id, or the simulation name. Given `20180129.DECKv1b_piControl.ne30_oEC.edison.cam.h0.0001-01.nc`, we do `-c 20180129.DECKv1b_piControl.ne30_oEC.edison`.
  * `cam` and `h0` are controlled by `-m` and `-h` respectively.

`-o` is where native grid climo files will be place.

`-O` is where regridded climo files will be placed. If not defined, it's stored where `-o` is defined.

`-v` is a list of variables. Regular expressions work as well.



**If we want all years from `0001` to `0002`, doesn't work b/c we need the previous year (`0000`) December (`*.h0.0000-12.nc`), a file that doesn't exist.**

We're trying to average over 1 year, so 000112 to 000211
```
ncclimo --start=0002 --end=0002 --case=20180129.DECKv1b_piControl.ne30_oEC.edison --input=/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/model-output/mon/ens1/v1 --output=/p/cscratch/acme/shaheen2/e3sm_timeseries_climo
```

For two years, we'd do ` --start=0002` and `--end=0003`, and we'd have from 000112 to 000311.

### Timeseries
**Without a v, it does all of the variables**
```
ncclimo -v FLNS -s 1 -e 9 -o $drc_out $drc_in/*mdl*000[1-9]*.nc
```

For years `0002` to `0002`, we need 12 files `*h0.0001-12.nc`, `*h0.0002-01.nc`, `*h0.0002-11.nc`
```
cd /p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/model-output/mon/ens1/v1/
ncclimo --vars=FLNS --start=0002 --end=0002 --output=/p/cscratch/acme/shaheen2/e3sm_timeseries_climo/timeseries *0001-12.nc *0002-0*.nc *0002-10.nc *0002-11.nc

ncclimo --vars=FLNS --start=0002 --end=0002 --output=/p/cscratch/acme/shaheen2/e3sm_timeseries_climo/timeseries *0002-*.nc
```

Another way
```
ls /p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/model-output/mon/ens1/v1/*.nc | ncclimo -s 2 -e 2 -o /p/cscratch/acme/shaheen2/e3sm_timeseries_climo/
```