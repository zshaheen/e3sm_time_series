import os
import glob
import cdms2
import numpy as np
import numpy.ma as ma
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

plotTitle = {'fontsize': 11.5}
plotSideTitle = {'fontsize': 9.5}

panel = [(0.1691, 0.6810, 0.6465, 0.2258),
         (0.1691, 0.3961, 0.6465, 0.2258),
         (0.1691, 0.1112, 0.6465, 0.2258),
         ]

def add_cyclic(var):
    lon = var.getLongitude()
    print('type(lon): {}'.format(type(lon)))
    return var(longitude=(lon[0], lon[0] + 360.0, 'coe'))


def get_ax_size(fig, ax):
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height
    width *= fig.dpi
    height *= fig.dpi
    return width, height


def plot_panel(n, fig, proj, var, title):
    #var = add_cyclic(var)
    lon = var.getLongitude()
    lat = var.getLatitude()
    var = ma.squeeze(var.asma())

    # Contour levels

    # Contour plot
    ax = fig.add_axes(panel[n], projection=proj)
    ax.set_global()
    p1 = ax.contourf(lon, lat, var,
                     transform=ccrs.PlateCarree(),
                     extend='both',
                     )
    
    ax.set_aspect('auto')
    ax.coastlines(lw=0.3)
    ax.set_title(title, fontdict=plotTitle)
    ax.set_xticks([0, 60, 120, 180, 240, 300, 359.99], crs=ccrs.PlateCarree())
    ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(
        zero_direction_label=True, number_format='.0f')
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.tick_params(labelsize=8.0, direction='out', width=1)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Color bar
    cbax = fig.add_axes(
        (panel[n][0] + 0.6635, panel[n][1] + 0.0215, 0.0326, 0.1792))
    cbar = fig.colorbar(p1, cax=cbax)
    w, h = get_ax_size(fig, cbax)

    cbar.ax.tick_params(labelsize=9.0, length=0)


def plot(test, reference, diff, parameter, fnm):

    # Create figure, projection
    figsize = [8.5, 11]
    dpi = 150
    fig = plt.figure(figsize=figsize, dpi=dpi)
    proj = ccrs.PlateCarree(central_longitude=180)

    # First two panels
    plot_panel(0, fig, proj, test, parameter.test_title)

    plot_panel(1, fig, proj, reference, parameter.reference_title)

    # Third panel
    plot_panel(2, fig, proj, diff, parameter.diff_title)

    # Figure title
    fig.suptitle(parameter.main_title, x=0.5, y=0.96, fontsize=14)

    # Save figure
    print('Saving diff plot: {}'.format(fnm + '.png'))
    plt.savefig(fnm + '.png')


def run(args):
    variables = args.vars
    output_dir = args.output_dir
    start_yr = args.start_yrs
    end_yr = args.end_yrs

    ###cdat_p = '/export/shaheen2/e3sm_diags_timeseries/cdat_climo_results/20180129.DECKv1b_piControl.ne30_oEC.edison_SON_climo.nc' 
    #cdat_p = '/export/shaheen2/e3sm_diags_timeseries/ncclimo_climo_results/20180129.DECKv1b_piControl.ne30_oEC.edison_SON_climo.nc' 
    ###nco_p = '/export/shaheen2/e3sm_diags_timeseries/ncclimo_climo_results/20180129.DECKv1b_piControl.ne30_oEC.edison_SON_climo.nc'

    cdat_paths = glob.glob(os.path.join(output_dir, 'cdat_climo_results', '*'))
    # nco_paths = glob.glob(os.path.join(output_dir, 'ncclimo_climo_results', '*'))
    nco_path_dir = os.path.join(output_dir, 'ncclimo_climo_results')
    
    output_dir = os.path.join(output_dir, 'diff_results')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    class Namespace:
        pass
    
    p = Namespace()
    p.test_title = 'CDAT'
    p.reference_title = 'ncclimo'
    p.diff_title = 'CDAT - ncclimo'

    for cdat_p in cdat_paths:
        f = cdat_p.split('/')[-1]
        nco_p = os.path.join(nco_path_dir, f)
        if not os.path.exists(nco_p):
            print('File not found, skipping plot for: {}'.format(nco_p))
            continue

        case_id = cdat_p.split('/')[-1]
        season = case_id.split('_')[-2]
        case_id = case_id.split('_')[0:-3]
        case_id = '.'.join(case_id)

        cdat_f = cdms2.open(cdat_p)
        nco_f = cdms2.open(nco_p)
        print(cdat_f.variables)
        print(nco_f.variables)

        for v in variables:
            print('\ncdat file: {}'.format(cdat_p))
            print('nco file: {}'.format(nco_p))
            print('variable: {}'.format(v))
            cdat_data = cdat_f(v)
            nco_data = nco_f(v)
            diff = cdat_data - nco_data
            p.main_title = '{} {} {}, {} to {}'.format(case_id, season, v, start_yr, end_yr)
            fnm = os.path.join(output_dir, 'diff_{}_{}_{}_{}_{}'.format(case_id, season, v, start_yr, end_yr))

            plot(cdat_data, nco_data, diff, p, fnm)

