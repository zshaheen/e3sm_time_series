The goal of this demo is to create both the **timeseries** and **climatology** given a set of monthly model data (`h0` files).

We are using the model files located at `/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/` on `acme1`.
* The climatology is a set of 17 files `*_01.nc`, `*_02.nc`, ..., `*_12.nc`, `*_ANN.nc`, ..., `*_SON.nc`.
  * So `*_01.nc` is the mean for January, while `*_ANN.nc` is the annual mean. Files with `DJF`, `MAM`, `JJA`, `SON` are seasonal means.
* Time-series files are files with one or more variable per file. It's just all of the monthly files puting into one huge file.
   * Ex: On acme1, we have `/p/user_pub/work/E3SM/1_0/piControl/1deg_atm_60-30km_ocean/atmos/129x256/time-series/mon/ens1/v1/FLNS_000101_050012.nc`
       * In this time-series file, the format is `FLNS_<year><month>_<year><month>.nc`
           * So `FLNS_000101_050012.nc`, the data from 01 (Jan) of the first year (0001) to 12(Dec) of the 500th year (500) are concatenated.
           * So there are 6000 individual means for FLNS.

