##################################################################################
# sersic_profile_mass_VC/paper_plots.py                                          #
#                                                                                #
# Copyright 2018-2021 Sedona Price <sedona.price@gmail.com> / MPE IR/Submm Group #
# Licensed under a 3-clause BSD style license - see LICENSE.rst                  #
##################################################################################

import os
import copy

import dill as pickle

import numpy as np

import scipy.interpolate as scp_interp

import astropy.cosmology as apy_cosmo
import astropy.constants as apy_con

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, FixedLocator, FixedFormatter, LogLocator
import matplotlib.markers as mks
from matplotlib.legend_handler import HandlerLine2D
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
from matplotlib import colorbar
from matplotlib.patches import Rectangle


from sersic_profile_mass_VC import table_io
from sersic_profile_mass_VC import calcs
from sersic_profile_mass_VC import utils


__all__ = [ 'make_all_paper_plots' ]


# CONSTANTS
G = apy_con.G
Msun = apy_con.M_sun
pc = apy_con.pc

# ---------------------
# Plot settings
#mpl.rcParams['text.usetex'] = True
## displaystyle

fontsize_leg = 9.
fontsize_leg_sm = 8.
fontsize_labels = 14.
fontsize_labels_sm = 12.
fontsize_ann = 9.
fontsize_ann_sm = 8.
fontsize_title= 14.
fontsize_title_lg = 16.
fontsize_ticks = 11.
fontsize_ticks_sm = 9.
fontsize_corner_ann = 15.

fontsize_ann_lg = 11.
fontsize_ann_latex_sm = 12.
fontsize_ann_latex = 13.


cmap_mass = cm.OrRd
cmap_q = cm.magma_r
cmap_n = cm.viridis_r
cmapg = cm.Greys


cmap_im = copy.copy(cm.RdYlBu)
cmap_im.set_under('#b4396f')
cmap_im.set_over('#503a99')

cmap_im2 = copy.copy(cm.RdYlBu_r)
cmap_im2.set_under('#503a99')
cmap_im2.set_over('#b4396f')

cmap_fdm = cm.Blues



# ---------------------

def plot_compare_mencl(fileout=None, output_path=None, table_path=None, q_arr=[1., 0.4, 0.2]):
    """
    Plot the fractional 3D spherical enclosed mass profile versus radius,
    for a range of Sersic indices n (n=1..8) and intrinsic axis ratios q.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        q_arr: array_like, optional
            Range of intrinsic axis ratios to plot. Default: q_arr = [1., 0.4, 0.2]
        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """

    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'mencl_sersic_potential'
        for q in q_arr:
            fileout += '_q{:0.2f}'.format(q)
        fileout += '.pdf'


    nmin = 1
    nmax = 8
    nstep = 1
    nrange = nmax-nmin
    n_arr = np.linspace(nmin,nmax, num=np.int(np.round(((nrange)/nstep)))+1)
    n_arr = np.append(np.array([0.5]), n_arr)

    color_arr = []
    ls_arr = []
    labels = []
    nextra = -0.5
    for n in n_arr:
        if n == 8.:
            color_arr.append('#2d0037')
        else:
            color_arr.append(cmap_n((n+nextra)/(nrange+nextra)))
        ls_arr.append('-')
        #labels.append(r'$n={}$'.format(n))
        if n == 0.5:
            labels.append(r'$n={:0.1f}$'.format(n))
        else:
            labels.append(r'$n={:0.0f}$'.format(n))


    # Load files:
    ks_dicts = []
    for q in q_arr:
        try:
            invq = 1./q
            ks_dict = {}
            ks_dict['3D'] = {}
            ks_dict['3D_ellip'] = {}
            ks_dict['vcirc'] = {}
            n_cnt = 0
            for n in n_arr:
                try:
                    tab = table_io.read_profile_table(n=n, invq=invq, path=table_path)
                    if n == 1.:
                        ks_dict['r_arr'] = tab['r']
                        ks_dict['Reff'] = tab['Reff']
                    ks_dict['3D']['n={}'.format(n)] = tab['menc3D_sph']    / tab['total_mass']
                    ks_dict['3D_ellip']['n={}'.format(n)] = tab['menc3D_ellipsoid'] / tab['total_mass']
                    ks_dict['vcirc']['n={}'.format(n)] = tab['vcirc']
                    n_cnt += 1
                except:
                    ks_dict['3D']['n={}'.format(n)] = None
                    ks_dict['3D_ellip']['n={}'.format(n)] = None
                    ks_dict['vcirc']['n={}'.format(n)] = None


            if n_cnt == 0:
                raise ValueError

        except:
            ks_dict = None

        ks_dicts.append(ks_dict)


    # ++++++++++++++++
    # plot 3D:

    xlabel = r'$\log_{10}(r/R_e)$'

    types = []
    ylabels = []
    titles = []
    vline_loc = []
    vline_lss = []
    vline_labels = []

    for i, q in enumerate(q_arr):
        types.append('3D')
        ylabels.append(r'$M_{\mathrm{enc}, \, \mathrm{3D,\,sphere}}(<r)/M_{\mathrm{tot}}$')
        if q < 1.:
            titles.append(r'Fractional 3D enclosed mass, sphere, $q_0={:0.1f}$'.format(q))
        else:
            titles.append(r'Fractional 3D enclosed mass, sphere, $q_0={:0.0f}$'.format(q))
        vline_loc.append([0.,  np.log10(2.2/1.676)])
        vline_lss.append(['--', '-.'])
        if i == 0:
            vline_labels.append([r'$r=R_e$', r'$r=1.3 R_e$'])
        else:
            vline_labels.append([None, None])



    xlim = [-2.0, 2.0]
    ylims = [[0., 1.], [0., 1.], [0., 1.]]
    spec_pairs = [[1., 0.], [4., 0.]]

    lw = 1.25 # 1.

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 4.0 #4.25
    n_cols = len(types)
    fac = 1.15
    f.set_size_inches(fac*scale*n_cols,scale)

    pad_outer = 0.2

    gs = gridspec.GridSpec(1, n_cols, wspace=pad_outer)
    axes = []
    for i in range(n_cols):
        axes.append(plt.subplot(gs[0,i]))


    for i in range(n_cols):
        ax = axes[i]
        ylim = ylims[i]
        ks_dict = ks_dicts[i]
        q = q_arr[i]
        if ks_dict is not None:
            n_cnt = 0
            for j, n in enumerate(n_arr):
                menc_arr = ks_dict[types[i]]['n={}'.format(n)]
                if menc_arr is not None:
                    n_cnt += 1
                    rarr_plot = np.log10(ks_dict['r_arr']/ks_dict['Reff'])
                    if len(menc_arr) != len(ks_dict['r_arr']):
                        raise ValueError
                    ax.plot(rarr_plot, menc_arr, ls=ls_arr[j], color=color_arr[j], lw=lw, label=labels[j])

                    for mm, sp_p in enumerate(spec_pairs):
                        if sp_p[0] == n:
                            wh = np.where(rarr_plot == sp_p[1])[0]
                            if len(wh) > 0:
                                ax.axhline(y=menc_arr[wh[0]], ls='--', lw=0.8, color=color_arr[j], zorder=-20.)
                                ####
                                fracx = 0.015
                                if (q == 1.):
                                    delt = 0.015
                                elif (q == 0.4):
                                    delt = -0.06 - 0.03 * (len(spec_pairs)-mm-1)
                                elif (q == 0.2):
                                    delt = -0.047 - 0.043 * (len(spec_pairs)-mm-1)
                                xypos = (xlim[1]-fracx*(xlim[1]-xlim[0]), menc_arr[wh[0]]+delt)
                                ax.annotate(r'{:0.1f}'.format(menc_arr[wh[0]]*100)+'\%',
                                    xy=xypos, ha='right', color=color_arr[j], fontsize=fontsize_ann)

        ax.axhline(y=0.5, ls='-.', color='grey', zorder=-20.)
        delt = 0.015
        fracx = 0.015
        ax.annotate(r'50\%', xy=(xlim[1]-fracx*(xlim[1]-xlim[0]), 0.5+delt),
            ha='right', color='dimgrey', fontsize=fontsize_ann)

        if vline_loc[i] is not None:
            for vl, vls, vlb in zip(vline_loc[i], vline_lss[i], vline_labels[i]):
                ax.axvline(x=vl, ls=vls, color='grey', label=vlb, zorder=-20.)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel(xlabel, fontsize=fontsize_labels)
        ax.set_ylabel(ylabels[i], fontsize=fontsize_labels)
        ax.tick_params(labelsize=fontsize_ticks)

        if titles[i] is not None:   ax.set_title(titles[i], fontsize=fontsize_title)


        ax.xaxis.set_minor_locator(MultipleLocator(0.25))
        ax.xaxis.set_major_locator(MultipleLocator(1.))

        ax.yaxis.set_minor_locator(MultipleLocator(0.05))
        ax.yaxis.set_major_locator(MultipleLocator(0.2))


        if i == 0:
            handles, labels_leg = ax.get_legend_handles_labels()
            neworder = range(n_cnt)
            handles_arr = []
            labels_arr = []
            for i in neworder:
                handles_arr.append(handles[i])
                labels_arr.append(labels_leg[i])

            neworder2 = range(n_cnt, len(handles))
            handles_arr2 = []
            labels_arr2 = []
            for i in neworder2:
                handles_arr2.append(handles[i])
                labels_arr2.append(labels_leg[i])

            frameon = True
            framealpha = 1.
            edgecolor = 'none'
            borderpad = 0.25
            fontsize_leg_tmp = fontsize_leg
            labelspacing=0.15
            handletextpad=0.25

            legend1 = ax.legend(handles_arr, labels_arr,
                labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                loc='upper left',
                numpoints=1, scatterpoints=1,
                frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                fontsize=fontsize_leg_tmp)

            legend2 = ax.legend(handles_arr2, labels_arr2,
                labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                loc='lower right',
                numpoints=1, scatterpoints=1,
                frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                fontsize=fontsize_leg_tmp)
            ax.add_artist(legend1)
            ax.add_artist(legend2)


    plt.savefig(fileout, bbox_inches='tight', dpi=600)
    plt.close()


#####
def plot_rhalf_3D_sersic_potential(output_path=None, table_path=None, fileout=None):
    """
    Plot the ratio of the 3D half mass radius to
    the 2D projected major axis effective radius (Reff),
    for a range of Sersic indices n and range of intrinsic axis ratios q.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'rhalf_3D_sersic_potential'
        fileout += '.pdf'


    # --------------------------------------------------------------
    # Arrays:
    # PLOTTING COLORED BY q:
    #q_arr_plotq = np.array([0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.])
    q_arr_plotq = np.array([0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.])
    nmin = 0.5
    nmax = 8.
    nstep = 0.1
    nrange = 7. #nmax-nmin
    n_arr_plotq = np.linspace(nmin,nmax, num=np.int(np.round((nmax-nmin)/nstep))+1)
    color_arr_plotq = []
    ls_arr_plotq = []
    labels_plotq = []
    for q in q_arr_plotq:
        if q <= 1.:
            color_arr_plotq.append(cmap_q(q))
            ls_arr_plotq.append('-')
        else:
            color_arr_plotq.append(cmapg(1./q))
            ls_arr_plotq.append('--')
        if q != 1.:
            labels_plotq.append(r'$q_0={}$'.format(q))
        else:
            labels_plotq.append(r'$q_0={:0.0f}$'.format(q))

    # --------------------------------------------------------------
    # PLOTTING COLORED BY n:
    nrange = 8.-1.
    n_arr_plotn = np.array([0.5, 1., 2., 4., 8.])
    q_arr_plotn = np.array([0.01, 0.05, 0.1, 0.125, 0.1428, 0.1667, 0.2, 0.25, 0.3, 0.333,
                0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.])

    color_arr_plotn = []
    ls_arr_plotn = []
    labels_plotn = []
    nextra = -0.5
    for n in n_arr_plotn:
        if n == 8.:
            color_arr_plotn.append('#2d0037')
        else:
            color_arr_plotn.append(cmap_n((n+nextra)/(nrange+nextra)))
        ls_arr_plotn.append('-')
        if n < 1:
            labels_plotn.append(r'$n={}$'.format(n))
        else:
            labels_plotn.append(r'$n={:0.0f}$'.format(n))


    # --------------------------------------------------------------
    #  COMPOSITE STACK:
    n_arrs = [n_arr_plotq, n_arr_plotn]
    q_arrs = [q_arr_plotq, q_arr_plotn]

    color_arrs =    [color_arr_plotq, color_arr_plotn]
    ls_arrs =       [ls_arr_plotq, ls_arr_plotn]
    labels_arrs =   [labels_plotq, labels_plotn]

    plot_types = ['plotq', 'plotn']

    # --------------------------------------------------------------
    # Load files:

    ks_dicts_list = []

    for i, plot_type in enumerate(plot_types):
        q_arr = q_arrs[i]
        n_arr = n_arrs[i]
        ks_dicts = []

        arrs = {'q': q_arr,
                'n': n_arr}
        if plot_type == 'plotq':
            var_order = ['q', 'n']
        elif plot_type == 'plotn':
            var_order = ['n', 'q']


        for v1 in arrs[var_order[0]]:
            if var_order[0] == 'q':
                q = v1
            elif var_order[0] == 'n':
                n = v1
            ks_dict = {}
            rhalf3D_arr = np.ones(len(arrs[var_order[1]])) * -99.
            for j, v2 in enumerate(arrs[var_order[1]]):
                if var_order[1] == 'q':
                    q = v2
                elif var_order[1] == 'n':
                    n = v2
                try:
                    invq = 1./q
                    tab = table_io.read_profile_table(n=n, invq=invq, path=table_path)

                    rhalf3D_arr[j] = calcs.find_rhalf3D_sphere(r=tab['r'], menc3D_sph=tab['menc3D_sph'],
                                            total_mass=tab['total_mass'])

                except:
                    rhalf3D_arr[j] = np.NaN

            if plot_type == 'plotq':
                ks_dict['q'] = q
                ks_dict['n_arr'] = n_arr
            elif plot_type == 'plotn':
                ks_dict['n'] = n
                ks_dict['q_arr'] = q_arr
            ks_dict['rhalf3D'] = rhalf3D_arr
            ks_dicts.append(ks_dict)


        ###
        ks_dicts_list.append(ks_dicts)




    # ++++++++++++++++
    # plot:

    xlim_plotq = [0., 8.25]
    ylim_plotq = [0.98, 1.4]
    xlabel_plotq = r'$n$'

    xlim_plotn = [-0.05, 1.05]
    ylim_plotn = [0.98, 1.4]
    xlabel_plotn = r'$q_0$'

    xlims = [xlim_plotq, xlim_plotn]
    ylims = [ylim_plotq, ylim_plotn]
    xlabels = [xlabel_plotq, xlabel_plotn]
    ylabels = [r'$r_{1/2,\, \mathrm{mass,\,3D}}/R_e$', None]
    titles = [None, None]


    # TEMP!
    marker = 'o'
    marker = None
    ms = 2

    ###
    lw = 1.3 #1.35 #1.25 # 1.

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.75
    n_cols = len(xlims)
    n_rows = 1
    fac = 1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)

    wspace = 0.05
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))

    #####
    for i, plot_type in enumerate(plot_types):
        ax = axes[i]
        if (i == 0):  ax.set_zorder(1)
        ks_dicts = ks_dicts_list[i]
        q_arr = q_arrs[i]
        n_arr = n_arrs[i]

        ls_arr = ls_arrs[i]
        color_arr = color_arrs[i]
        labels = labels_arrs[i]

        xlim = xlims[i]
        ylim = ylims[i]
        xlabel = xlabels[i]
        ylabel = ylabels[i]
        title = titles[i]

        if plot_type == 'plotq':
            for i, q in enumerate(q_arr):
                ks_dict = ks_dicts[i]
                wh_fin = np.where(np.isfinite(ks_dict['rhalf3D']))[0]
                if len(wh_fin) > 0:
                    ax.plot(ks_dict['n_arr'][wh_fin], ks_dict['rhalf3D'][wh_fin], ls=ls_arr[i], color=color_arr[i],
                                lw=lw, label=labels[i], marker=marker, ms=ms)

            ax.axvline(x=1., ls=':', color='lightgrey', zorder=-20.)
            ax.axvline(x=4., ls=':', color='lightgrey', zorder=-20.)
        elif plot_type == 'plotn':
            for i, n in enumerate(n_arr):
                ks_dict = ks_dicts[i]
                wh_fin = np.where(np.isfinite(ks_dict['rhalf3D']))[0]
                if len(wh_fin) > 0:
                    ax.plot(ks_dict['q_arr'][wh_fin], ks_dict['rhalf3D'][wh_fin], ls=ls_arr[i], color=color_arr[i],
                                lw=lw, label=labels[i], marker=marker, ms=ms)

        ax.axhline(y=1., ls=":", color='lightgrey', zorder=-20.)
        #####
        if ylim is None: ylim = ax.get_ylim()

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        if xlabel is not None:
            ax.set_xlabel(xlabel, fontsize=fontsize_labels)
        else:
            #ax.tick_params(labelbottom='off')
            ax.set_xticklabels([])


        if ylabel is not None:
            ax.set_ylabel(ylabel, fontsize=fontsize_labels)
        else:
            #ax.tick_params(labelleft='off')
            ax.set_yticklabels([])

        ax.tick_params(labelsize=fontsize_ticks)

        if title is not None:   ax.set_title(title, fontsize=fontsize_title)

        if plot_type == 'plotq':
            ax.xaxis.set_minor_locator(MultipleLocator(0.2))
            ax.xaxis.set_major_locator(MultipleLocator(1.))
        elif plot_type == 'plotn':
            ax.xaxis.set_minor_locator(MultipleLocator(0.05))
            ax.xaxis.set_major_locator(MultipleLocator(0.2))


        if (ylim[1]-ylim[0]) > 3:
            ax.yaxis.set_minor_locator(MultipleLocator(0.2))
            ax.yaxis.set_major_locator(MultipleLocator(1.))
        else:
            ax.yaxis.set_minor_locator(MultipleLocator(0.01))
            ax.yaxis.set_major_locator(MultipleLocator(0.1))

        frameon = True
        framealpha = 1.
        edgecolor = 'none'
        borderpad = 0.25
        fontsize_leg_tmp = fontsize_leg
        labelspacing=0.15
        handletextpad=0.25
        if plot_type == 'plotq':
            #loc = (1.075, 0.57)
            loc = (1.075, 0.59)
            borderpad = 0.5
            edgecolor = 'grey'
        elif plot_type == 'plotn':
            loc = 'lower right'
        legend = ax.legend(labelspacing=labelspacing, borderpad=borderpad,
            handletextpad=handletextpad, loc=loc,
            frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
            numpoints=1, scatterpoints=1,
            fontsize=fontsize_leg_tmp)



    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()




def plot_composite_menc_vcirc_profile_invert(q_arr=[1., 0.4, 0.2], n_arr=[1., 4.],
             output_path=None, table_path=None, fileout=None):
    """
    Plot the enclosed mass and circular velocity profiles versus radius,
    for a number of direct calculations and inverted assumptions
    (applying the relation valid for spherically symmetric cases: v^2 = GM/r ).

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        q_arr: array_like, optional
            Range of intrinsic axis ratios to plot. Default: q_arr = [1., 0.4, 0.2]
        n_arr: array_like, optional
            Range of Sersic indices to plot. Default: n_arr = [1., 4.]
        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'mencl_vcirc_compsite_compare_sersic_potential'
        for q in q_arr:
            fileout += '_q{:0.2f}'.format(q)
        for n in n_arr:
            fileout += '_n{:1.0f}'.format(n)
        fileout += '.pdf'



    # Load files:
    ks_dicts = []
    for n in n_arr:
        for q in q_arr:
            try:
                # read fits tables, construct ks dict.....
                invq = 1./q
                tab = table_io.read_profile_table(n=n, invq=invq, path=table_path)

                ks_dict = {}
                ks_dict['r_arr'] = tab['r']
                ks_dict['Reff'] = tab['Reff']
                ks_dict['total_mass'] = tab['total_mass']
                ks_dict['menc2D_ellip']  =   calcs.M_encl_2D(tab['r'], total_mass=tab['total_mass'],
                                                    q=q, n=n, Reff=tab['Reff'],i=90.)
                ks_dict['menc3D_sph']  =     tab['menc3D_sph']
                ks_dict['menc3D_ellip']  =   tab['menc3D_ellipsoid']
                ks_dict['vcirc']  =          tab['vcirc']

                ks_dict['v_menc3D_sph'] =   calcs.vcirc_spherical_symmetry(r=tab['r'], menc=tab['menc3D_sph'])
                ks_dict['v_menc3D_ellip'] = calcs.vcirc_spherical_symmetry(r=tab['r'], menc=tab['menc3D_ellipsoid'])

                ks_dict['m_invert_vcirc']  = calcs.menc_spherical_symmetry(r=tab['r'], vcirc=tab['vcirc'])

                ks_dict['mass_plot'] = tab['total_mass']
            except:
                ks_dict = None
            ks_dicts.append(ks_dict)


    # ++++++++++++++++
    # plot:
    types1 = ['menc2D_ellip', 'menc3D_sph', 'menc3D_ellip', 'm_invert_vcirc']
    ls_arr1 = ['-','--','-.',':']
    lw_arr1 = [1.1, 1.35, 1.1, 1.35]
    labels1 = [r'2D, ellipse', r'3D, sphere', r'3D, ellipsoid', r'$v_{\mathrm{circ}}(r)^2 r/G$']
    color_arr1 = [cmap_q(0.18), cmap_q(1./3.), cmap_q(5./9.), cmap_q(1.)]


    types2 = ['v_menc3D_sph', 'v_menc3D_ellip', 'vcirc']
    ls_arr2 = ['-','-.',':']
    lw_arr2 = [1.35, 1.1, 1.35]
    labels2 = [r'$\sqrt{M_{\mathrm{3D,sph}}(r)G/r}$',
              r'$\sqrt{M_{\mathrm{3D,ellip}}(r)G/r}$',
              r'$v_{\mathrm{circ}}(r)$']
    #
    color_arr2 = [cmap_q(1./3.), cmap_q(5./9.), cmap_q(1.)]


    #
    titles1 = []
    vline_loc1 = []
    vline_lss1 = []
    vline_labels1 = []
    xlims1 = []
    ylims1 = []
    xlabels1 = []
    ylabels1 = []


    titles2 = []
    vline_loc2 = []
    vline_lss2 = []
    vline_labels2 = []
    xlims2 = []
    ylims2 = []
    xlabels2 = []
    ylabels2 = []

    for i, n in enumerate(n_arr):
        for j, q in enumerate(q_arr):
            if i == 0:
                if j == np.int(np.round((len(q_arr)-1)/2.)):
                    titles1.append(r'Fractional mass profile')
                    titles2.append(r'Circular velocity')
                else:
                    titles1.append(None)
                    titles2.append(None)
            else:
                titles1.append(None)
                titles2.append(None)

            if i == len(n_arr) - 1:
                xlabels1.append(r'$\log_{10}(r/R_e)$')
                xlabels2.append(r'$\log_{10}(r/R_e)$')
            else:
                xlabels1.append(None)
                xlabels2.append(None)

            if j == 0:
                ylabels1.append(r'$M_{\mathrm{enc}}(r)/M_{\mathrm{total}}$')
                ylabels2.append(r'$v_{\mathrm{circ}}(r)$ [km/s]')
            else:
                ylabels1.append(None)
                ylabels2.append(None)

            xlims1.append([-2.0, 2.0])
            xlims2.append([-2.0, 2.0])
            ylims1.append([-0.05, 1.22])
            ylims2.append([0., 410.])
            vline_loc1.append([0.,  np.log10(2.2/1.676)])
            vline_lss1.append(['--', '-.'])
            vline_loc2.append([0.,  np.log10(2.2/1.676)])
            vline_lss2.append(['--', '-.'])
            if ((i == 0) & (j == 0)):
                vline_labels1.append([r'$r=R_e$', r'$r=1.3 R_e$'])
                vline_labels2.append([r'$r=R_e$', r'$r=1.3 R_e$'])
            else:
                vline_labels1.append([None, None])
                vline_labels2.append([None, None])


    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.5 #3.75
    n_cols = len(q_arr)
    n_rows = len(n_arr)
    fac = 0.98
    f.set_size_inches(fac*scale*n_cols,2.*scale*n_rows)


    pad_outer = 0.175 #0.15
    wspace = 0.025
    hspace = wspace

    gs_outer = gridspec.GridSpec(2, 1, wspace=wspace, hspace=pad_outer)
    gs1 = gridspec.GridSpecFromSubplotSpec(n_rows,n_cols,subplot_spec=gs_outer[0,0],wspace=wspace, hspace=hspace)
    gs2 = gridspec.GridSpecFromSubplotSpec(n_rows,n_cols, subplot_spec=gs_outer[1,0], wspace=wspace, hspace=hspace)

    axes1 = []
    axes2 = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes1.append(plt.subplot(gs1[i,j]))
            axes2.append(plt.subplot(gs2[i,j]))


    for i in range(n_rows):
        for j in range(n_cols):

            k = i*n_cols + j

            n = n_arr[i]
            q = q_arr[j]

            ks_dict = ks_dicts[k]
            ax1 = axes1[k]
            ax2 = axes2[k]

            xlim1 = xlims1[k]
            ylim1= ylims1[k]
            ylabel1 = ylabels1[k]
            title1 = titles1[k]

            xlim2 = xlims2[k]
            ylim2 = ylims2[k]
            ylabel2 = ylabels2[k]
            title2 = titles2[k]

            if ks_dict is not None:
                for mm, typ in enumerate(types1):
                    menc_arr = ks_dict[types1[mm]]
                    rarr_plot = np.log10(ks_dict['r_arr']/ks_dict['Reff'])
                    ax1.plot(rarr_plot, menc_arr/ks_dict['mass_plot'], ls=ls_arr1[mm], color=color_arr1[mm],
                                lw=lw_arr1[mm], label=labels1[mm])
                #
                for mm, typ in enumerate(types2):
                    menc_arr = ks_dict[types2[mm]]
                    rarr_plot = np.log10(ks_dict['r_arr']/ks_dict['Reff'])
                    ax2.plot(rarr_plot, menc_arr, ls=ls_arr2[mm], color=color_arr2[mm],
                                lw=lw_arr2[mm], label=labels2[mm])

                if ylim1 is None:
                    ylim1 = ax1.get_ylim()
                #
                if ylim2 is None:
                    ylim2 = ax2.get_ylim()

                ax1.axhline(y=0.5*ks_dict['total_mass']/ks_dict['mass_plot'], ls='-.', color='darkgrey', zorder=-20.)
                ax1.axhline(y=ks_dict['total_mass']/ks_dict['mass_plot'], ls=':', color='darkgrey', zorder=-20.)
                if k == 0:
                    delt = 0.015
                    fracx = 0.015
                    yspan = ylim1[1]-ylim1[0]
                    ax1.annotate(r'50\%', xy=(xlim1[1]-fracx*(xlim1[1]-xlim1[0]), (0.5+delt)),
                                va='bottom', ha='right', color='grey', fontsize=fontsize_ann)
                    ax1.annotate(r'100\%', xy=(xlim1[1]-fracx*(xlim1[1]-xlim1[0]), (1.0+delt)),
                                va='bottom', ha='right', color='grey', fontsize=fontsize_ann)

                if vline_loc1[k] is not None:
                    for vl, vls, vlb in zip(vline_loc1[k], vline_lss1[k], vline_labels1[k]):
                        ax1.axvline(x=vl, ls=vls, color='grey', label=vlb, zorder=-20.)

                if vline_loc2[k] is not None:
                    for vl, vls, vlb in zip(vline_loc2[k], vline_lss2[k], vline_labels2[k]):
                        ax2.axvline(x=vl, ls=vls, color='grey', label=vlb, zorder=-20.)


            ######################
            # ANNOTATE:
            #######
            posannx = 0.765
            posanny = 0.95
            dely = 0.

            bbox_props = dict(boxstyle="square", fc="ghostwhite", ec="dimgrey", lw=1)
            ann_str = r'$n\ \:'+r'={:0.0f}$'.format(n)+'\n'+r'$q_0={:0.1f}$'.format(q)

            # Annotate ax1:
            ax1.annotate(ann_str, xy=(posannx, 1-posanny + dely),
                        xycoords='axes fraction', va='bottom', ha='left', fontsize=fontsize_ann_lg,
                        bbox=bbox_props)
            # Annotate ax2:
            ax2.annotate(ann_str, xy=(posannx, posanny),
                        xycoords='axes fraction', va='top', ha='left', fontsize=fontsize_ann_lg,
                        bbox=bbox_props)

            ######################
            ax1.set_xlim(xlim1)
            ax1.set_ylim(ylim1)
            ax2.set_xlim(xlim2)
            ax2.set_ylim(ylim2)

            ax1.tick_params(labelsize=fontsize_ticks)
            ax2.tick_params(labelsize=fontsize_ticks)



            ax1.xaxis.set_minor_locator(MultipleLocator(0.25))
            ax2.xaxis.set_minor_locator(MultipleLocator(0.25))

            if (j > 0) & (i == n_rows-1):
                ax1.xaxis.set_major_locator(FixedLocator([-2., -1., 0., 1., 2.]))
                ax1.xaxis.set_major_formatter(FixedFormatter(["", "-1", "0", "1", "2"]))

                ax2.xaxis.set_major_locator(FixedLocator([-2., -1., 0., 1., 2.]))
                ax2.xaxis.set_major_formatter(FixedFormatter(["", "-1", "0", "1", "2"]))
            else:
                ax1.xaxis.set_major_locator(MultipleLocator(1.))
                ax2.xaxis.set_major_locator(MultipleLocator(1.))


            ax1.yaxis.set_minor_locator(MultipleLocator(0.05))
            ax1.yaxis.set_major_locator(MultipleLocator(0.2))

            ax2.yaxis.set_minor_locator(MultipleLocator(20.))
            ax2.yaxis.set_major_locator(MultipleLocator(100.))



            if xlabels1[k] is not None:
                ax1.set_xlabel(xlabels1[k], fontsize=fontsize_labels)
            else:
                #ax1.tick_params(labelbottom='off')
                ax1.set_xticklabels([])
            if ylabels1[k] is not None:
                ax1.set_ylabel(ylabels1[k], fontsize=fontsize_labels)
            else:
                #ax1.tick_params(labelleft='off')
                ax1.set_yticklabels([])

            if xlabels2[k] is not None:
                ax2.set_xlabel(xlabels2[k], fontsize=fontsize_labels)
            else:
                #ax2.tick_params(labelbottom='off')
                ax2.set_xticklabels([])
            if ylabels2[k] is not None:
                ax2.set_ylabel(ylabels2[k], fontsize=fontsize_labels)
            else:
                #ax2.tick_params(labelleft='off')
                ax2.set_yticklabels([])


            if titles1[k] is not None:
                ax1.set_title(titles1[k], fontsize=fontsize_title_lg)
            if titles2[k] is not None:
                ax2.set_title(titles2[k], fontsize=fontsize_title_lg)



            if k == 0:
                handles1, labels1 = ax1.get_legend_handles_labels()
                neworder1 = range(len(types1))
                handles_arr1 = []
                labels_arr1 = []
                for ii in neworder1:
                    handles_arr1.append(handles1[ii])
                    labels_arr1.append(labels1[ii])

                neworder12 = range(len(types1), len(handles1))
                handles_arr12 = []
                labels_arr12 = []
                for ii in neworder12:
                    handles_arr12.append(handles1[ii])
                    labels_arr12.append(labels1[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25

                legend11 = ax1.legend(handles_arr1, labels_arr1,
                    labelspacing=labelspacing, borderpad=borderpad,
                    handletextpad=handletextpad,
                    loc='upper left',
                    frameon=frameon, numpoints=1,
                    scatterpoints=1,
                    framealpha=framealpha,
                    edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                legend12 = ax1.legend(handles_arr12, labels_arr12,
                    labelspacing=labelspacing, borderpad=borderpad,
                    handletextpad=handletextpad,
                    loc=(0.025, 0.15),
                    frameon=False, numpoints=1,
                    scatterpoints=1,
                    framealpha=framealpha,
                    edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                ax1.add_artist(legend11)
                ax1.add_artist(legend12)


                #####
                handles2, labels2 = ax2.get_legend_handles_labels()
                neworder2 = range(len(types2))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles2[ii])
                    labels_arr2.append(labels2[ii])

                neworder2 = range(len(types2), len(handles2))
                handles_arr22 = []
                labels_arr22 = []
                for ii in neworder2:
                    handles_arr22.append(handles2[ii])
                    labels_arr22.append(labels2[ii])

                legend21 = ax2.legend(handles_arr2, labels_arr2,
                    labelspacing=labelspacing, borderpad=borderpad,
                    handletextpad=handletextpad,
                    loc='upper left',
                    frameon=frameon, numpoints=1,
                    scatterpoints=1,
                    framealpha=framealpha,
                    edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                legend22 = ax2.legend(handles_arr22, labels_arr22,
                    labelspacing=labelspacing, borderpad=borderpad,
                    handletextpad=handletextpad,
                    loc='lower right',
                    frameon=False, numpoints=1,
                    scatterpoints=1,
                    framealpha=framealpha,
                    edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                ax2.add_artist(legend21)
                ax2.add_artist(legend22)


    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()



def plot_virial_coeff(fileout=None, output_path=None, table_path=None,
            q_arr=[0.2, 0.4, 0.6, 0.8, 1., 1.5, 2.]):
    """
    Plot the total and 3D virial coefficients at Reff, ktot(Reff) and k3D(Reff),
    as a function of Sersic index n for a range of intrinsic axis ratios q.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        q_arr: array_like, optional
            Range of intrinsic axis ratios to plot.
            Default: q_arr = [0.2, 0.4, 0.6, 0.8, 1., 1.5, 2.]  (mostly oblate, 2 prolate)
        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'virial_coeff_sersic_potential.pdf'

    mpl.rcParams['text.usetex'] = True

    ####################
    q_arr = np.array(q_arr)

    color_arr = []
    ls_arr = []
    labels = []
    for q in q_arr:
        if q <= 1.:
            color_arr.append(cmap_q(q))
            ls_arr.append('-')
        else:
            color_arr.append(cmapg(1./q))
            ls_arr.append('--')
        labels.append(r'$q_0={}$'.format(q))


    # Load files:
    try:
        # read fits tables, construct ks dict.....
        invq = 1./q
        ks_dict = {}
        ks_dict['tot'] = {}
        ks_dict['3D'] = {}

        nmin = 0.5
        nmax = 8.
        nstep = 0.1
        n_arr = np.linspace(nmin,nmax, num=np.int(np.round((nmax-nmin)/nstep))+1)

        for q in q_arr:
            invq = 1./q
            ktot_narr = np.ones(len(n_arr)) * -99.
            k3D_narr =  np.ones(len(n_arr)) * -99.
            for j, n in enumerate(n_arr):
                tab = table_io.read_profile_table(n=n, invq=invq, path=table_path)
                if (q == 0.2) & (n == 1.):
                    ks_dict['Reff'] = tab['Reff']
                    ks_dict['tot']['narr'] = n_arr
                    ks_dict['3D']['narr'] = n_arr

                ktot_narr[j] = calcs.virial_coeff_tot(tab['Reff'], total_mass=tab['total_mass'],
                                       q=q, Reff=tab['Reff'], n=n, i=90., vc=tab['vcirc_Reff'])
                k3D_narr[j]  = calcs.virial_coeff_3D(tab['Reff'], total_mass=tab['total_mass'],
                                       q=q, Reff=tab['Reff'], n=n, i=90., vc=tab['vcirc_Reff'], m3D=tab['menc3D_sph_Reff'])


            ks_dict['tot']['q={}'.format(q)] = ktot_narr
            ks_dict['3D']['q={}'.format(q)]  = k3D_narr

    except:
        ks_dict = None


    types = ['tot', '3D']
    xlabel = r'$n$'
    ylabels = [r'$k_{\mathrm{tot}}(r=R_e)$',
               r'$k_{\mathrm{3D}}(r=R_e)$']
    xlim = [0., 8.25]
    ylims = [[1.75, 5.5], [0.85, 1.15]]

    titles = [r'Total virial coefficient',
              r'Enclosed 3D virial coefficient' ]

    ann_arr = [ r'$\displaystyle k_{\mathrm{tot}}(R_e) = \frac{M_{\mathrm{tot}} G }{v_c(R_e)^2 R_e}$',
                r'$\displaystyle k_{\mathrm{3D}}(R_e) = \frac{M_{\mathrm{encl,3D}}(<R_e) G }{v_c(R_e)^2 R_e}$' ]
    ann_arr_pos = ['upperright', 'lowerright']

    lw = 1.3 #1.25 #1.

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 4.0 #4.25
    n_cols = len(types)
    f.set_size_inches(1.15*scale*n_cols,scale)


    pad_outer = 0.2

    gs = gridspec.GridSpec(1, n_cols, wspace=pad_outer)
    axes = []
    for i in range(n_cols):
        axes.append(plt.subplot(gs[0,i]))

    for i in range(n_cols):
        ax = axes[i]
        ylim = ylims[i]
        for j, q in enumerate(q_arr):
            k_arr = ks_dict[types[i]]['q={}'.format(q)]
            n_arr = ks_dict[types[i]]['narr']
            if len(k_arr) != len(n_arr):
                raise ValueError

            ax.plot(n_arr, k_arr, ls=ls_arr[j], color=color_arr[j], lw=lw, label=labels[j])

            try:
                for sp_p in spec_pairs:
                    if sp_p[0] == q:
                        wh = np.where(n_arr == sp_p[1])[0]
                        if len(wh) > 0:
                            ax.scatter([sp_p[1]], [k_arr[wh[0]]], marker='o', s=35.,
                                    color=color_arr[j], edgecolor='white', lw=1, zorder=20.)
                            delt = - 1.
                            ax.annotate(r'$k_{\mathrm{'+types[i]+r'}}=$'+r'${:0.2f}$'.format(k_arr[wh[0]]),
                                xy=(sp_p[1], k_arr[wh[0]]+delt), color=color_arr[j], fontsize=fontsize_ann)
            except:
                pass

        #
        ax.axvline(x=1., ls=':', color='lightgrey', zorder=-20.)
        ax.axvline(x=4., ls=':', color='lightgrey', zorder=-20.)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel(xlabel, fontsize=fontsize_labels)
        ax.set_ylabel(ylabels[i], fontsize=fontsize_labels)
        ax.tick_params(labelsize=fontsize_ticks)

        if titles[i] is not None:   ax.set_title(titles[i], fontsize=fontsize_title)

        ax.xaxis.set_minor_locator(MultipleLocator(0.25))
        ax.xaxis.set_major_locator(MultipleLocator(1.))

        xydelt = 0.04
        if ann_arr_pos[i] == 'lowerright':
            xy = (1.-xydelt, xydelt)
            va='bottom'
            ha='right'
        elif ann_arr_pos[i] == 'upperright':
            xy = (1.-xydelt, 1.-xydelt)
            va='top'
            ha='right'
        ax.annotate(ann_arr[i], xy=xy,
                va=va, ha=ha, fontsize=fontsize_ann,
                xycoords='axes fraction')

        if (ylim[1]-ylim[0]) > 3:
            ax.yaxis.set_minor_locator(MultipleLocator(0.2))
            ax.yaxis.set_major_locator(MultipleLocator(1.))
        else:
            ax.yaxis.set_minor_locator(MultipleLocator(0.02))
            ax.yaxis.set_major_locator(MultipleLocator(0.1))

        if i == 1:
            frameon = False
            borderpad = 0.25
            fontsize_leg_tmp = fontsize_leg
            labelspacing=0.15
            handletextpad=0.25
            legend = ax.legend(labelspacing=labelspacing, borderpad=borderpad,
                handletextpad=handletextpad, loc='upper right', frameon=frameon,
                numpoints=1, scatterpoints=1,fontsize=fontsize_leg_tmp)


    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

    mpl.rcParams['text.usetex'] = False

    return None
    #####


def plot_alpha_vs_r(fileout=None, output_path=None, table_path=None,
            n_arr=[0.5, 1., 2., 4., 8.]):
    """
    Plot alpha=-dlnrho_g/dlnr derived for deprojected Sersic distribution,
    over a range of Sersic index n.
    Compare to self-gravitating exponential disk case (eg Burkert+10).

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        n_arr: array_like, optional
            Range of Sersic indices to plot. Default: n_arr = [0.5, 1., 2., 4,, 8.]
        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'alpha_vs_r_sersic_potential.pdf'


    ####################
    n_arr = np.array(n_arr)

    color_arr = []
    #ls_arr = []
    labels = []
    nextra = -0.5
    nrange = 7. #n_arr.max()-n_arr.min()
    for n in n_arr:
        if n == 8.:
            color_arr.append('#2d0037')
        elif n < 0.5:
            color_arr.append('orange')
        else:
            color_arr.append(cmap_n((n+nextra)/(nrange+nextra)))
        #ls_arr.append('-')
        if n < 1.:
            labels.append(r'$n={:0.1f}$'.format(n))
        else:
            labels.append(r'$n={:0.0f}$'.format(n))

    q_arr = [1.]
    # Load files:
    try:
        # read fits tables, construct ks dict.....
        ks_dict = {}
        ks_dict['alpha'] = {}

        invq = 1.
        q = 1.
        for j, n in enumerate(n_arr):
            tab = table_io.read_profile_table(n=n, invq=invq, path=table_path)
            if (q == 1.) & (n == 1.):
                ks_dict['Reff'] = tab['Reff']
                ks_dict['alpha']['narr'] = n_arr
                ks_dict['r'] = tab['r']

            ks_dict['alpha']['n={}'.format(n)] = -tab['dlnrho_dlnr']

    except:
        ks_dict = None



    types = ['alpha', 'alpha_by_sg']
    xlabel = r'$r/R_e$'
    ylabels = [r'$\alpha(r)$', r'$\alpha/\alpha_{\mathrm{self-grav}}(r)$']
    # xlim = [0., 20.]
    # ylims = [[-1., 20.]]
    # xlim = [0., 5.]
    # ylims = [[-1., 20.]]
    xlim = [0., 5.] #4.5] #3.5]
    #xlim = [0.,20.]
    ylims = [[0., 10.], [0., 2.]]
    #ylims = [[-2., 10.], [-1., 2.]]
    #ylims = [[-10., 10.], [-2., 2.]]

    titles = [None, None] # [r'$alpha(r)$', r'$\alpha/\alpha_{\mathrm{sg}}(r)$' ]

    ann_arr = [ r'$\alpha(r) = -\frac{\mathrm{d}\ln \rho_g}{\mathrm{d}\ln{}r}$', None]
    ann_arr_pos = ['lowerright', 'lowerright']

    lw = 1.3 #1.25 #1.
    #ls_arr = ['-', '--']
    ls_arr = ['-']

    # ---------------------------------------------------------
    # Kretschmer+21 points:
    k21_dict = {'rtore': np.array([0.5,1.,2.,4.]),
                'a': np.array([-1.54, -0.86, 0.98, 4.08]),
                'b': np.array([2.87,2.98,2.9, 2.69]),
                'rtore_cont': np.arange(xlim[0], xlim[1]+0.05, 0.05)}
    for n in n_arr:
        if (n >= 0.5):
            k21_dict['n={}'.format(n)] = k21_dict['a']/n + k21_dict['b']
        else:
            k21_dict['n={}'.format(n)] = k21_dict['rtore'] * np.NaN

    x = k21_dict['rtore_cont'] - 1.
    k21_dict['gas_rtore']   = -0.146*(x**2) + 1.204*x + 1.475
    k21_dict['stars_rtore'] = -0.075*(x**2) + 0.591*x + 2.544
    k21_dict['color'] = 'darkgrey'

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 4. #4.25
    n_cols = len(types)
    f.set_size_inches(1.15*scale*n_cols,scale)


    pad_outer = 0.2

    gs = gridspec.GridSpec(1, n_cols, wspace=pad_outer)
    axes = []
    for i in range(n_cols):
        axes.append(plt.subplot(gs[0,i]))



    r_arr = ks_dict['r']/ks_dict['Reff']



    for i in range(n_cols):
        ax = axes[i]
        ylim = ylims[i]

        if types[i] == 'alpha':
            ax.plot(r_arr, 3.36*r_arr, ls='--', color='black', lw=lw, label='Self-grav')

            # ax.plot(k21_dict['rtore_cont'], k21_dict['gas_rtore'], ls='--',
            #                 color=k21_dict['color'], lw=lw, label='K+21, gas (Tab 1)',zorder=-5.)
            # ax.plot(k21_dict['rtore_cont'], k21_dict['stars_rtore'], ls='-.',
            #                 color=k21_dict['color'], lw=lw, label='K+21, stars (Tab 1)',zorder=-5.)
            # ax.scatter([1., 5.], [0.45*3.36, 0.3*3.36*5.], color='magenta',
            #             marker='o', linestyle='None', zorder=10., label=r'K+21, $\alpha_{\rho}$ (gas '+'\n+/or stars?\nFig 4)')

        elif types[i] == 'alpha_by_sg':
            # ax.plot(k21_dict['rtore_cont'], k21_dict['gas_rtore']/(3.36*k21_dict['rtore_cont']),
            #                 ls='--', color=k21_dict['color'], lw=lw, label='None',zorder=-5.)
            # ax.plot(k21_dict['rtore_cont'], k21_dict['stars_rtore']/(3.36*k21_dict['rtore_cont']),
            #                 ls='-.', color=k21_dict['color'], lw=lw, label='None',zorder=-5.)
            # ax.scatter([1., 5.], [0.45, 0.3], color='magenta',marker='o', linestyle='None', zorder=10.)

            pass


        ls = ls_arr[0]

        for k, n in enumerate(n_arr):
            if types[i] == 'alpha':
                alpha_arr = ks_dict['alpha']['n={}'.format(n)]
                #alpha_arr = ks_dict['alpha']['q={}'.format(q)]['n={}'.format(n)]
            elif types[i] == 'alpha_by_sg':
                alpha_arr = ks_dict['alpha']['n={}'.format(n)] / (3.36*r_arr)
                #alpha_arr = ks_dict['alpha']['q={}'.format(q)]['n={}'.format(n)] / (3.36*r_arr)

            if len(alpha_arr) != len(r_arr):
                raise ValueError

            ax.plot(r_arr, alpha_arr, ls=ls, color=color_arr[k], lw=lw, label=labels[k])

            # if types[i] == 'alpha':
            #     ax.scatter(k21_dict['rtore'], k21_dict['n={}'.format(n)], color=color_arr[k],
            #                 marker='o', linestyle='None')
            # elif types[i] == 'alpha_by_sg':
            #     ax.scatter(k21_dict['rtore'], k21_dict['n={}'.format(n)]/(3.36*k21_dict['rtore']), color=color_arr[k],
            #                 marker='o', linestyle='None')

            # if (n == 1.):
            #     ax.plot(r_arr, alpha_arr*np.NaN, ls=ls, color='black', lw=1., label=r'$q={}$'.format(q))

        #
        if types[i] == 'alpha_by_sg':
            #ax.axhline(y=1., ls=':', color='lightgrey', zorder=-20.)
            ax.axhline(y=1., ls='--', color='black', zorder=-20.)
        ax.axvline(x=1., ls=':', color='lightgrey', zorder=-20.)
        # ax.axvline(x=4., ls=':', color='lightgrey', zorder=-20.)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel(xlabel, fontsize=fontsize_labels)
        ax.set_ylabel(ylabels[i], fontsize=fontsize_labels)
        ax.tick_params(labelsize=fontsize_ticks)

        if titles[i] is not None:   ax.set_title(titles[i], fontsize=fontsize_title)

        # ax.xaxis.set_minor_locator(MultipleLocator(0.25))
        # ax.xaxis.set_major_locator(MultipleLocator(1.))
        # ax.xaxis.set_minor_locator(MultipleLocator(0.1))
        # ax.xaxis.set_major_locator(MultipleLocator(0.5))
        ax.xaxis.set_minor_locator(MultipleLocator(0.2))
        ax.xaxis.set_major_locator(MultipleLocator(1.0))

        xydelt = 0.04
        if ann_arr_pos[i] == 'lowerright':
            xy = (1.-xydelt, xydelt)
            va='bottom'
            ha='right'
        elif ann_arr_pos[i] == 'upperright':
            xy = (1.-xydelt, 1.-xydelt)
            va='top'
            ha='right'
        ax.annotate(ann_arr[i], xy=xy,
                va=va, ha=ha, fontsize=fontsize_ann_latex,
                xycoords='axes fraction')

        if (ylim[1]-ylim[0]) > 9:
            ax.yaxis.set_minor_locator(MultipleLocator(0.5))
            ax.yaxis.set_major_locator(MultipleLocator(2.))
        elif (ylim[1]-ylim[0]) > 3:
            ax.yaxis.set_minor_locator(MultipleLocator(0.2))
            ax.yaxis.set_major_locator(MultipleLocator(1.))
        elif (ylim[1]-ylim[0]) > 1:
            ax.yaxis.set_minor_locator(MultipleLocator(0.1))
            ax.yaxis.set_major_locator(MultipleLocator(0.5))
        else:
            ax.yaxis.set_minor_locator(MultipleLocator(0.02))
            ax.yaxis.set_major_locator(MultipleLocator(0.1))

        if i == 0:
            frameon = True
            framealpha = 1.
            borderpad = 0.75 #0.5 #0.25
            fontsize_leg_tmp = fontsize_leg
            labelspacing= 0.2 # 0.15
            handletextpad= 0.5  #0.25
            fancybox = False
            edgecolor='None'
            facecolor = 'white' #'magenta' # 'white'
            legend = ax.legend(labelspacing=labelspacing, borderpad=borderpad,
                handletextpad=handletextpad, loc='upper left', frameon=frameon,
                numpoints=1, scatterpoints=1,fontsize=fontsize_leg_tmp,
                fancybox=fancybox,edgecolor=edgecolor, facecolor=facecolor,
                framealpha=framealpha)


    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


    return None
    #####


#
def plot_AD_sersic_potential_alpha_vs_r(fileout=None, output_path=None, table_path=None,
            sigma0_arr = [30., 60., 90.],
            q_arr=[1., 0.2],
            n_arr=[0.5, 1., 2., 4.],
            show_sigmar_toy=False,
            show_sigmar_toy_nosig0=False):
    """
    Plot asymmetric drift using alpha=-dlnrho_g/dlnr derived for deprojected
    Sersic distributions, over a range of Sersic index n and intrinsic axis ratios q.
    Compare to self-gravitating exponential disk case (eg Burkert+10).

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        sigma0_arr: array_like, optional
            Intrinsic constant velocity dispersions to plot (km/s).
            Default: [30., 60., 90.]
        q_arr: array_like, optional
            Range of intrinsic axis ratios to plot. Default: q_arr = [1., 0.2]
        n_arr: array_like, optional
            Range of Sersic indices to plot. Default: n_arr = [0.5, 1., 2., 4.]
        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'AD_sersic_potential_alpha_vs_r'
        if show_sigmar_toy:
            fileout += '_sigmar_toy'
        if show_sigmar_toy_nosig0:
            fileout += '_sigmar_toy_nosig0'
        fileout += '.pdf'

    ####################
    n_arr = np.array(n_arr)
    q_arr = np.array(q_arr)

    color_arr = []
    #ls_arr = []
    labels = []
    nextra = -0.5
    nrange = 7. #n_arr.max()-n_arr.min()
    for n in n_arr:
        if n == 8.:
            color_arr.append('#2d0037')
        else:
            color_arr.append(cmap_n((n+nextra)/(nrange+nextra)))
        #ls_arr.append('-')
        if n < 1.:
            labels.append(r'$n={:0.1f}$'.format(n))
        else:
            labels.append(r'$n={:0.0f}$'.format(n))


    labels = []
    color_arr = []
    color_arr_basic = ['tab:purple', 'tab:cyan', 'tab:orange']

    for i, sig0 in enumerate(sigma0_arr):
        color_arr.append(color_arr_basic[i])
        labels.append(r'$\sigma_0='+'{:0.0f}'.format(sig0)+r'\ \mathrm{km/s}$')

    xlabel = r'$r/R_e$'
    ylabel = r'$v(r)$'
    xlim = [0., 5.]
    ylim = [0.,320.]

    # Load files:
    delr = 0.001
    rarr = np.arange(xlim[0], xlim[1]+delr, delr)
    Reff = 1.
    total_mass = np.power(10.,10.5)
    #try:
    if True:
        # read fits tables, construct ks dict.....
        ks_dict = {}

        for q in q_arr:
            invq = 1./q
            ks_dict_q = {}
            for j, n in enumerate(n_arr):
                ks_dict_q['n={}'.format(n)] = {}
                tab = table_io.read_profile_table(n=n, invq=invq, path=table_path)
                if (q == q_arr.min()) & (n == n_arr.min()):
                    ks_dict['Reff'] = Reff
                    ks_dict['narr'] = n_arr
                    ks_dict['qarr'] = q_arr
                    ks_dict['r'] = rarr
                    ks_dict['total_mass'] = total_mass

                ks_dict_q['n={}'.format(n)]['alpha'] = calcs.interpolate_sersic_profile_alpha_nearest(r=rarr,
                            Reff=Reff, n=n, invq=invq, path=table_path)
                ks_dict_q['n={}'.format(n)]['vcirc'] = calcs.interpolate_sersic_profile_VC_nearest(r=rarr,
                            total_mass=total_mass, Reff=Reff, n=n, invq=invq, path=table_path)
                #tab['vcirc']
                #raise ValueError

            ks_dict['q={}'.format(q)] = ks_dict_q


    #except:
    else:
        ks_dict = None


    titles = []
    ann_arr = []
    ann_arr_pos = []
    # for sig0 in sigma0_arr:
    #     titles.append(r'$\sigma_0='+'{:0.0f}$'.format(sig0))
    for n in n_arr:
        if n < 1.:
            nann = '{:0.1f}'.format(n)
        else:
            nann = '{:0.0f}'.format(n)
        titles.append(r'$n='+"{}$".format(nann))

    for i, q in enumerate(q_arr):
        if q != 1.:
            qstr = "{:0.1f}".format(q)
        else:
            qstr = "{:0.0f}".format(q)
        ann_arr.append(r'$q_0='+'{}$'.format(qstr))
        ann_arr_pos.append('upperright')

    lw = 1.3 #1.25 #1.


    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.25 #3.75 #4.25
    n_cols = len(n_arr)
    n_rows = len(q_arr)
    f.set_size_inches(1.05*scale*n_cols,scale*n_rows)

    pad_outer = 0.05

    gs = gridspec.GridSpec(n_rows, n_cols, wspace=pad_outer,hspace=pad_outer)
    axes = []
    for j in range(n_rows):
        for i in range(n_cols):
            axes.append(plt.subplot(gs[j,i]))

    r_arr = ks_dict['r']/ks_dict['Reff']

    for j, q in enumerate(q_arr):
        for i, n in enumerate(n_arr):
            mm = j*n_cols+i
            ax = axes[mm]

            for k, sig0 in enumerate(sigma0_arr):

                vcirc = ks_dict['q={}'.format(q)]['n={}'.format(n)]['vcirc'].copy()
                alpha = ks_dict['q={}'.format(q)]['n={}'.format(n)]['alpha'].copy()
                if (mm == 1):
                    lbl_sig0 = labels[k]
                else:
                    lbl_sig0 = None
                if (mm == 0):
                    lbl_circ = r'$v_{\mathrm{circ}}$'
                    lbl_alpha = r'$v_{\mathrm{rot}}$, $\alpha(n)$'
                    lbl_SG = r'$v_{\mathrm{rot}}$, Self-grav'
                    lbl_alpha_sigmar = r'$v_{\mathrm{rot}}$, $\alpha(n)+\alpha_{\sigma(r)}$'
                    lbl_alpha_sigmar_nosig0 = r'$v_{\mathrm{rot}}$, $\alpha(n)+\alpha_{\sigma(r)}$, $\sigma_0=0$'
                else:
                    lbl_circ = None
                    lbl_alpha = None
                    lbl_SG = None
                    lbl_alpha_sigmar = None
                    lbl_alpha_sigmar_nosig0 = None


                if k == 0:
                    ax.plot(r_arr, vcirc, ls='-', color='black', lw=lw, label=lbl_circ, zorder=10.)
                    if lbl_alpha is not None:
                        ax.plot(r_arr, r_arr*np.NaN, ls='--', color='black', lw=lw, label=lbl_alpha)
                        if show_sigmar_toy:
                            ax.plot(r_arr, r_arr*np.NaN, ls='-.', color='black', lw=lw, label=lbl_alpha_sigmar)
                        if show_sigmar_toy_nosig0:
                            ax.plot(r_arr, r_arr*np.NaN, ls=(0, (5, 2, 1, 2, 1, 2, 1, 2)), color='black', lw=lw, label=lbl_alpha_sigmar_nosig0)
                        ax.plot(r_arr, r_arr*np.NaN, ls=':', color='black', lw=lw, label=lbl_SG)

                if lbl_sig0 is not None:
                    ax.plot(r_arr, r_arr*np.NaN, ls='-', color=color_arr[k], lw=lw, label=lbl_sig0)

                ax.plot(r_arr, np.sqrt(vcirc**2-alpha*(sig0**2)), ls='--', color=color_arr[k], lw=lw)
                if show_sigmar_toy:
                    sigr =  _sigr_toy(r_arr, 2.*sig0, sig0, 0.5*Reff)
                    alphasigr = _alpha_sigr_toy(r_arr, 2.*sig0, sig0, 0.5*Reff)
                    ax.plot(r_arr, np.sqrt(vcirc**2-(alpha+alphasigr)*(sigr**2)), ls='-.', color=color_arr[k], lw=lw)
                if show_sigmar_toy_nosig0:
                    sigr_nosig0 = _sigr_toy(r_arr, np.sqrt(5.)*sig0, 0., 0.5*Reff)
                    alphasigr_nosig0 = _alpha_sigr_toy(r_arr, np.sqrt(5.)*sig0, 0., 0.5*Reff)
                    print(sigr[0], sigr_nosig0[0])
                    ax.plot(r_arr, np.sqrt(vcirc**2-(alpha+alphasigr_nosig0)*(sigr_nosig0**2)),
                            ls=(0, (5, 2, 1, 2, 1, 2, 1, 2)), color=color_arr[k], lw=lw)
                ax.plot(r_arr, np.sqrt(vcirc**2-3.36*r_arr*(sig0**2)), ls=':', color=color_arr[k], lw=lw)

            ax.axvline(x=1.3, ls=':', color='lightgrey', zorder=-20.)

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            ax.tick_params(labelsize=fontsize_ticks)


            if (titles[i] is not None) & (j==0):
                ax.set_title(titles[i], fontsize=fontsize_title)

            ax.xaxis.set_minor_locator(MultipleLocator(0.2))
            ax.xaxis.set_major_locator(MultipleLocator(1.))

            if True:
                xydelt = 0.04
                arpos = ann_arr_pos[j]
                if (mm <= 1):
                    arpos = 'upperleft'
                if arpos == 'lowerright':
                    xy = (1.-xydelt, xydelt)
                    va='bottom'
                    ha='right'
                elif arpos == 'upperright':
                    xy = (1.-xydelt, 1.-xydelt)
                    va='top'
                    ha='right'
                elif arpos == 'lowerleft':
                    xy = (xydelt, xydelt)
                    va='bottom'
                    ha='left'
                elif arpos == 'upperleft':
                    xy = (xydelt, 1.-xydelt)
                    va='top'
                    ha='left'
                ax.annotate(ann_arr[j], xy=xy,
                        va=va, ha=ha, fontsize=fontsize_ann_latex_sm, #fontsize_ann_latex,
                        xycoords='axes fraction')
            if (ylim[1]-ylim[0]) > 300:
                ax.yaxis.set_minor_locator(MultipleLocator(20.))
                ax.yaxis.set_major_locator(MultipleLocator(100.))
            elif (ylim[1]-ylim[0]) > 50:
                ax.yaxis.set_minor_locator(MultipleLocator(10.))
                ax.yaxis.set_major_locator(MultipleLocator(50.))
            elif (ylim[1]-ylim[0]) > 3:
                ax.yaxis.set_minor_locator(MultipleLocator(0.2))
                ax.yaxis.set_major_locator(MultipleLocator(1.))
            elif (ylim[1]-ylim[0]) > 1:
                ax.yaxis.set_minor_locator(MultipleLocator(0.1))
                ax.yaxis.set_major_locator(MultipleLocator(0.5))
            else:
                ax.yaxis.set_minor_locator(MultipleLocator(0.02))
                ax.yaxis.set_major_locator(MultipleLocator(0.1))

            if (j == n_rows-1):
                ax.set_xlabel(xlabel, fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if (i == 0):
                ax.set_ylabel(ylabel, fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            if (mm <= 1):
                frameon = False #True
                borderpad = 0.5 #0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad= 0.5  #0.25
                fancybox = False
                edgecolor='None'
                loc='upper right' #'upper left'
                legend = ax.legend(labelspacing=labelspacing, borderpad=borderpad,
                    handletextpad=handletextpad, loc=loc, frameon=frameon,
                    numpoints=1, scatterpoints=1,fontsize=fontsize_leg_tmp,
                    fancybox=fancybox,edgecolor=edgecolor)


    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


    return None
    #####


def plot_AD_composite_alpha_vs_r(fileout=None, output_path=None, table_path=None):
    """
    Plot asymmetric drift using alpha=-dlnrho_g/dlnr derived for deprojected
    Sersic distributions, over a range of Sersic index n and intrinsic axis ratios q.
    Compare to self-gravitating exponential disk case (eg Burkert+10).

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'AD_composite_alpha_vs_r.pdf'


    ####################
    ks_dict = {}
    gal1 = {'bt':      0.07,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 0.5,
            're_disk': 6.,
            'sigma0':  60.,
            'lMbar':   10.74,
            'lMhalo':  8.5,
            'halo_conc': 4.}
    gal2 = {'bt':      0.07,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 0.5,
            're_disk': 6.,
            'sigma0':  65.,
            'lMbar':   10.46,
            'lMhalo':  11.5,
            'halo_conc': 4.}
    gal3 = {'bt':      0.07,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 0.5,
            're_disk': 6.,
            'sigma0':  30.,
            'lMbar':   10.74,
            'lMhalo':  8.5,
            'halo_conc': 4.}
    gal4 = {'bt':      0.07,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 0.5,
            're_disk': 6.,
            'sigma0':  30.,
            'lMbar':   10.46,
            'lMhalo':  11.5,
            'halo_conc': 4.}

    gal5 = {'bt':      0.5,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  45.,
            'lMbar':   10.5,
            'lMhalo':  12.5,
            'halo_conc': 4.}
    gal6 = {'bt':      0.5,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  45.,
            'lMbar':   11.,
            'lMhalo':  7.,
            'halo_conc': 4.}
    gal7 = {'bt':      0.5,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  20.,
            'lMbar':   11.,
            'lMhalo':  7.,
            'halo_conc': 4.}
    gal8 = {'bt':      0.5,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  20.,
            'lMbar':   10.8,
            'lMhalo':  12.,
            'halo_conc': 4.}
    gal9 = {'bt':      0.5,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  60.,
            'lMbar':   10.8,
            'lMhalo':  12.,
            'halo_conc': 4.}


    gal10 = {'bt':      0.0,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  20.,
            'lMbar':   10.8,
            'lMhalo':  12.,
            'halo_conc': 4.}

    gal11 = {'bt':      0.0,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  60.,
            'lMbar':   10.8,
            'lMhalo':  12.,
            'halo_conc': 4.}

    ks_dict['1'] = gal1
    ks_dict['2'] = gal2
    ks_dict['3'] = gal3
    ks_dict['4'] = gal4
    ks_dict['5'] = gal5
    ks_dict['6'] = gal6
    ks_dict['7'] = gal7
    ks_dict['8'] = gal8
    ks_dict['9'] = gal9
    ks_dict['10'] = gal10
    ks_dict['11'] = gal11



    xlabel = r'$r$ [kpc]'
    ylabel = r'$v(r)$ [km/s]'
    xlim = [0., 30.]
    ylim = [0.,320.]

    # Load files:
    delr = 0.1
    rarr = np.arange(xlim[0], xlim[1]+delr, delr)

    for key in ks_dict.keys():
        invq_disk = 1./ks_dict[key]['q_disk']
        n_disk = ks_dict[key]['ns_disk']
        Reff_disk = ks_dict[key]['re_disk']
        bt = ks_dict[key]['bt']
        Mbaryon = np.power(10., ks_dict[key]['lMbar'])
        Mhalo = np.power(10., ks_dict[key]['lMhalo'])
        n_bulge = 4.
        invq_bulge = 1.
        Reff_bulge = 1.
        halo_conc = ks_dict[key]['halo_conc']
        z = ks_dict[key]['z']
        alpha_gas = calcs.interpolate_sersic_profile_alpha_nearest(r=rarr,
                    Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)

        vcirc_disk = calcs.interpolate_sersic_profile_VC(r=rarr, total_mass=(1.-bt)*Mbaryon,
                                Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
        vcirc_bulge = calcs.interpolate_sersic_profile_VC(r=rarr, total_mass=(bt)*Mbaryon,
                                Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
        vcirc_halo = calcs.NFW_halo_vcirc(r=rarr, Mvirial=Mhalo, conc=halo_conc, z=z)
        vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
        vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
        fdm_vsq = fdm_vsq = vcirc_halo**2/vcirc_tot**2

        ks_dict[key]['vcirc'] = vcirc_tot
        ks_dict[key]['alpha'] = alpha_gas
        ks_dict[key]['r'] =     rarr


        ks_dict[key]['vcirc_disk'] = vcirc_disk
        ks_dict[key]['vcirc_bulge'] = vcirc_bulge
        ks_dict[key]['vcirc_halo'] = vcirc_halo
        ks_dict[key]['vcirc_baryons'] = vcirc_baryons
        ks_dict[key]['fdm_vsq'] = fdm_vsq

    ann_arr = []
    ann_arr_pos = []
    gal9 = {'bt':      0.5,
            'q_disk':  0.25,
            'z':       2.,
            'ns_disk': 1.,
            're_disk': 5.,
            'sigma0':  60.,
            'lMbar':   10.8,
            'lMhalo':  12.,
            'halo_conc': 4.}
    ann_keys = ['lMbar', 'ns_disk', 're_disk', #'q_disk',
                'bt', 'sigma0', 'lMhalo']  #, 'halo_conc'

    gals = ks_dict.keys()
    for i, gal in enumerate([*gals]):
        ann_str = ''
        #for j, gkey in enumerate(ks_dict[gal].keys()):
        for j, gkey in enumerate(ann_keys):
            if gkey == 'lMbar':
                if len(ann_str) > 0:
                    ann_str += '\n'
                ann_str += r'$\log_{10}(M_{\mathrm{bar}}/M_{\odot})='
                ann_str += "{:0.2f}".format(ks_dict[gal][gkey])
                ann_str += r'$'
            elif gkey == 'ns_disk':
                if len(ann_str) > 0:
                    ann_str += '\n'
                ann_str += r'$n_{\mathrm{disk}}='
                if (ks_dict[gal][gkey]< 1.):
                    ann_str += "{:0.1f}".format(ks_dict[gal][gkey])
                else:
                    ann_str += "{:0.0f}".format(ks_dict[gal][gkey])
                ann_str += r'$'
            elif gkey == 're_disk':
                if len(ann_str) > 0:
                    ann_str += '\n'
                ann_str += r'$R_{e,\mathrm{disk}}='
                ann_str += "{:0.0f}".format(ks_dict[gal][gkey])
                ann_str += r'$ kpc'
            elif gkey == 'bt':
                if len(ann_str) > 0:
                    ann_str += '\n'
                ann_str += r'$B/T='
                ann_str += "{:0.2f}".format(ks_dict[gal][gkey])
                ann_str += r'$'
            elif gkey == 'sigma0':
                if len(ann_str) > 0:
                    ann_str += '\n'
                ann_str += r'$\sigma_0='
                ann_str += "{:0.0f}".format(ks_dict[gal][gkey])
                ann_str += r'$'
            elif gkey == 'lMhalo':
                if len(ann_str) > 0:
                    ann_str += '\n'
                ann_str += r'$\log_{10}(M_{\mathrm{halo}}/M_{\odot})='
                ann_str += "{:0.2f}".format(ks_dict[gal][gkey])
                ann_str += r'$'
            else:
                raise ValueError("unspecified gkey={}".format(gkey))


        ## ADD FDM APPROX
        whnear = np.abs(rarr-ks_dict[gal]['re_disk']).argmin()
        ann_str += '\n'
        ann_str += r'$f_{\mathrm{DM}}(\sim R_{e})='
        ann_str += "{:0.2f}".format(ks_dict[gal]['fdm_vsq'][whnear])
        ann_str += r'$'

        ann_arr.append(ann_str)
        ann_arr_pos.append('upperright')

    lw = 1.3 #1.25 #1.


    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.25 #3.75 #4.25
    n_rows = np.int(np.floor(np.sqrt(1.*len(gals))))
    n_cols = np.int(np.ceil(len(gals)/(1.*n_rows)))
    f.set_size_inches(1.05*scale*n_cols,scale*n_rows)


    #pad_outer = 0.25 #0.2
    pad_outer = 0.05

    gs = gridspec.GridSpec(n_rows, n_cols, wspace=pad_outer,hspace=pad_outer)
    axes = []
    for j in range(n_rows):
        for i in range(n_cols):
            axes.append(plt.subplot(gs[j,i]))


    for j in range(n_rows):
        for i in range(n_cols):
            mm = j*n_cols+i
            ax = axes[mm]
            if mm >= len(gals):
                ax.set_axis_off()
            else:
                gal = [*gals][mm]

                r_arr = ks_dict[gal]['r']
                vcirc = ks_dict[gal]['vcirc'].copy()
                alpha = ks_dict[gal]['alpha'].copy()
                sig0 =  ks_dict[gal]['sigma0']

                if (mm == 0):
                    lbl_circ = r'$v_{\mathrm{circ}}$'
                    lbl_alpha = r'$v_{\mathrm{rot}}$, $\alpha(n)$'
                    lbl_SG = r'$v_{\mathrm{rot}}$, Self-grav'
                else:
                    lbl_circ = None
                    lbl_alpha = None
                    lbl_SG = None

                ax.plot(r_arr, vcirc, ls='-', color='black', lw=lw, label=lbl_circ, zorder=10.)


                ax.plot(r_arr, ks_dict[gal]['vcirc_disk'], ls='-', color='tab:blue', lw=1., label='Disk')
                ax.plot(r_arr, ks_dict[gal]['vcirc_bulge'], ls='-', color='tab:red', lw=1., label='Bulge')
                ax.plot(r_arr, ks_dict[gal]['vcirc_baryons'], ls='-', color='green', lw=1., label='Baryons')
                ax.plot(r_arr, ks_dict[gal]['vcirc_halo'], ls='-', color='purple', lw=1., label='Halo')



                ax.plot(r_arr, np.sqrt(vcirc**2-alpha*(sig0**2)), ls='--', color='red', lw=lw, label=lbl_alpha)
                ax.plot(r_arr, np.sqrt(vcirc**2-3.36*(r_arr/ks_dict[gal]['re_disk'])*(sig0**2)), ls=':', color='blue', lw=lw, label=lbl_SG)


                ax.axvline(x=1.*ks_dict[gal]['re_disk'], ls=':', color='lightgrey', zorder=-20.)

                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.tick_params(labelsize=fontsize_ticks)

                ax.xaxis.set_minor_locator(MultipleLocator(1.))
                ax.xaxis.set_major_locator(MultipleLocator(5.))

                #if (i == 0):
                if True:
                    xydelt = 0.04
                    arpos = ann_arr_pos[mm]
                    if (mm <= 0):
                        arpos = 'upperleft'
                    if arpos == 'lowerright':
                        xy = (1.-xydelt, xydelt)
                        va='bottom'
                        ha='right'
                    elif arpos == 'upperright':
                        xy = (1.-xydelt, 1.-xydelt)
                        va='top'
                        ha='right'
                    elif arpos == 'lowerleft':
                        xy = (xydelt, xydelt)
                        va='bottom'
                        ha='left'
                    elif arpos == 'upperleft':
                        xy = (xydelt, 1.-xydelt)
                        va='top'
                        ha='left'
                    ax.annotate(ann_arr[mm], xy=xy,
                            va=va, ha=ha, fontsize=fontsize_ann, #fontsize_ann_latex_sm, #fontsize_ann_latex,
                            xycoords='axes fraction')
                if (ylim[1]-ylim[0]) > 300:
                    ax.yaxis.set_minor_locator(MultipleLocator(20.))
                    ax.yaxis.set_major_locator(MultipleLocator(100.))
                elif (ylim[1]-ylim[0]) > 50:
                    ax.yaxis.set_minor_locator(MultipleLocator(10.))
                    ax.yaxis.set_major_locator(MultipleLocator(50.))
                elif (ylim[1]-ylim[0]) > 3:
                    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
                    ax.yaxis.set_major_locator(MultipleLocator(1.))
                elif (ylim[1]-ylim[0]) > 1:
                    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
                    ax.yaxis.set_major_locator(MultipleLocator(0.5))
                else:
                    ax.yaxis.set_minor_locator(MultipleLocator(0.02))
                    ax.yaxis.set_major_locator(MultipleLocator(0.1))

                if (j == n_rows-1):
                    ax.set_xlabel(xlabel, fontsize=fontsize_labels)
                else:
                    ax.set_xticklabels([])

                if (i == 0):
                    ax.set_ylabel(ylabel, fontsize=fontsize_labels)
                else:
                    ax.set_yticklabels([])

                if (mm <= 0):
                    frameon = False #True
                    borderpad = 0.5 #0.25
                    fontsize_leg_tmp = fontsize_leg
                    labelspacing=0.15
                    handletextpad= 0.5  #0.25
                    fancybox = False
                    edgecolor='None'
                    loc='upper right' #'upper left'
                    legend = ax.legend(labelspacing=labelspacing, borderpad=borderpad,
                        handletextpad=handletextpad, loc=loc, frameon=frameon,
                        numpoints=1, scatterpoints=1,fontsize=fontsize_leg_tmp,
                        fancybox=fancybox,edgecolor=edgecolor)


    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


    return None
    #####

def plot_example_galaxy_mencl_vcirc(bt_arr=[0., 0.25, 0.5, 0.75, 1.],
             output_path=None, table_path=None, fileout=None,
             z=2., Mbaryon=5.e10,
             Reff_disk=5., n_disk=1., invq_disk=5.,
             Reff_bulge=1., n_bulge=4., invq_bulge=1.,
             Mhalo=1.e12, halo_conc=4.,
             rmin = 0., rmax=15., rstep=0.01,
             log_rmin=-0.6, log_rmax=2.2, nlogr = 101,
             logradius=False,
             ylim_lmenc=[8., 12.],
             ylim_lmenc_lograd=[6.,12.5],
             ylim_vcirc=[0., 360.]):
    """
    Plot example enclosed mass and circular velocity profiles for
    different mass components, over a variety of B/T ratios.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        bt_arr: array_like, optional
            Array of B/T ratios to plot, in separate panels.
            Default: [0., 0.25, 0.5, 0.75]
        z: float, optional
            Redshift (to determine NFW halo properties. Default: z=2.
        Mbaryon: float, optional
            Total baryon mass [Msun]. Default: 5.e10 Msun.
        Reff_disk: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of disk component [kpc].
            Default: 5kpc
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        invq_disk: float, optional
            Flattening of disk component. Default: invq_disk = 5.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)
        Mhalo: float, optional
            NFW halo mass within R200 (=M200) [Msun]. Default: 1.e12 Msun
        halo_conc: float, optional
            Concentration of NFW halo. Default: 4.

        logradius: bool, optional
            Option whether to plot log radius or linear. Default: False (plot linear).
        rmin: float, optional
            Minimum radius, if doing linear radius. Ignored if logradius=True. [kpc]
        rmax: float, optional
            Maximum radius, if doing linear radius. Ignored if logradius=True. [kpc]
        rstep: float, optional
            Radius stepsize, if doing linear radius.Ignored if logradius=True. [kpc]
        log_rmin: float, optional
            Log of minimum radius, if doing log radius. Ignored if logradius=False. [log(kpc)]
        log_rmax: float, optional
            Log of maximum radius, if doing log radius. Ignored if logradius=False. [log(kpc)]
        nlogr: int, optional
            Number of log radius steps, if logradius=True. Ignored if logradius=False.

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """

    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_example_galaxy_mencl_vcirc'
        for bt in bt_arr:
            fileout += '_bt{:0.2f}'.format(bt)
        if logradius:  fileout += '_logradius'
        fileout += '.pdf'



    if logradius:
        r_arr = np.logspace(log_rmin, log_rmax, num=nlogr)
        rarr_plot = np.log10(r_arr)
    else:
        r_arr = np.arange(rmin, rmax+rstep, rstep)
        rarr_plot = r_arr

    q_disk = 1./invq_disk


    # ++++++++++++++++
    # plot:

    color_fdm = 'silver' # 'grey'
    color_vsq = 'dimgrey'
    types = ['menc3D', 'vcirc']
    ls_arr = ['--', '-.',
                (0, (3, 1, 1, 1, 1, 1)),
                ':', '-',
                (0, (10, 4)), (0, (10, 4, 1, 4, 1, 4, 1, 4))]
    lw_arr = [1.25, 1.25,
                1.35,
            1.35, 1.5,
            1., 1.]
    labels = ['Disk', 'Bulge',
                'Baryons (D+B)',
                'Halo', 'Total',
                r'$M_{\mathrm{enc,DM}}/M_{\mathrm{enc,tot}}$', r'$v_{\mathrm{circ,DM}}^2/v_{\mathrm{circ,tot}}^2$']

    color_arr = ['blue', 'red',
                'green',
                'purple', 'black',
                color_fdm, color_vsq]


    titles = []
    vline_loc = []
    vline_lss = []
    vline_labels = []
    xlims = []
    ylims = []
    xlabels = []
    ylabels = []

    ylims2 = []
    ylabels2 = []

    for i, typ in enumerate(types):
        for j, bt in enumerate(bt_arr):
            if i == 0:
                titles.append(r'$B/T={:0.2f}$'.format(bt))
            else:
                titles.append(None)

            if i == len(types) - 1:
                if logradius:
                    xlabels.append(r'$\log_{10}(r/\mathrm{[kpc]})$')
                else:
                    xlabels.append(r'$r\ \mathrm{[kpc]}$')
            else:
                xlabels.append(None)

            if j == 0:
                if typ == 'menc3D':
                    ylabels.append(r'$\log_{10}(M_{\mathrm{encl,3D,sph}}(r)/M_{\odot})$')
                elif typ == 'vcirc':
                    ylabels.append(r'$v_{\mathrm{circ}}(r)$ [km/s]')
            else:
                ylabels.append(None)

            if j == len(bt_arr) -1:
                ylabels2.append(r'$\mathrm{frac}$')
            else:
                ylabels2.append(None)

            if logradius:
                xlims.append([log_rmin, log_rmax])
            else:
                xlims.append([rmin, rmax+0.025*(rmax-rmin)])

            if typ == 'menc3D':
                if logradius:
                    ylims.append(ylim_lmenc_lograd)
                else:
                    ylims.append(ylim_lmenc)
            elif typ == 'vcirc':
                ylims.append(ylim_vcirc)

            ####
            ylims2.append([0.,1.])


            if logradius:
                vline_loc.append([np.log10(Reff_disk),  np.log10(2.2/1.676 * Reff_disk), np.log10(calcs.halo_rvir(Mvirial=Mhalo, z=z))])
                vline_lss.append(['--', '-.', ':'])
                if ((i == 0) & (j == 1)):
                    vline_labels.append([r'$r=R_{e,\mathrm{disk}}$', r'$r=1.3 R_{e,\mathrm{disk}}$', r'$r_{\mathrm{vir}}$'])
                else:
                    vline_labels.append([None, None, None])
            else:
                vline_loc.append([Reff_disk,  (2.2/1.676 * Reff_disk)])
                vline_lss.append(['--', '-.'])
                if ((i == 0) & (j == 1)):
                    vline_labels.append([r'$r=R_{e,\mathrm{disk}}$', r'$r=1.3 R_{e,\mathrm{disk}}$'])
                else:
                    vline_labels.append([None, None])



    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 2.75
    n_cols = len(bt_arr)
    n_rows = len(types)
    fac = 1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)


    wspace = 0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            typ = types[i]
            bt = bt_arr[j]

            ax = axes[k]
            xlim = xlims[k]
            ylim = ylims[k]
            ylabel = ylabels[k]
            title = titles[k]

            ###############
            ## Get mass, velocity components:

            #####
            menc_disk = calcs.interpolate_sersic_profile_menc(r=r_arr, total_mass=(1.-bt)*Mbaryon,
                                    Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
            menc_bulge = calcs.interpolate_sersic_profile_menc(r=r_arr, total_mass=(bt)*Mbaryon,
                                    Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
            menc_halo = calcs.NFW_halo_enclosed_mass(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z)
            menc_baryons = menc_disk + menc_bulge
            menc_tot = menc_baryons + menc_halo
            fdm_menc = menc_halo/menc_tot

            #####
            vcirc_disk = calcs.interpolate_sersic_profile_VC(r=r_arr, total_mass=(1.-bt)*Mbaryon,
                                    Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
            vcirc_bulge = calcs.interpolate_sersic_profile_VC(r=r_arr, total_mass=(bt)*Mbaryon,
                                    Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
            vcirc_halo = calcs.NFW_halo_vcirc(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z)
            vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
            vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
            fdm_vsq = vcirc_halo**2/vcirc_tot**2

            if typ == 'menc3D':
                yarrs = [np.log10(menc_disk), np.log10(menc_bulge),
                         np.log10(menc_baryons),
                         np.log10(menc_halo), np.log10(menc_tot)]
                asymp_vals = [np.log10((1.-bt)*Mbaryon), np.log10(bt*Mbaryon), np.log10(Mbaryon), np.log10(Mhalo), np.NaN]
                fdm = fdm_menc

            elif typ == 'vcirc':
                yarrs = [vcirc_disk, vcirc_bulge,
                         vcirc_baryons,
                         vcirc_halo, vcirc_tot]
                fdm = fdm_vsq





            for mm in range(len(yarrs)):
                ax.plot(rarr_plot, yarrs[mm], ls=ls_arr[mm], color=color_arr[mm],
                        lw=lw_arr[mm], label=labels[mm])

            # Plot fDM:
            if typ in ['menc3D', 'vcirc']:
                ax2 = ax.twinx()
                ax2.set_zorder(-1)
                ax.patch.set_visible(False)


                mm += 1
                ax2.plot(rarr_plot, fdm_menc, ls=ls_arr[mm], color=color_arr[mm],
                        lw=lw_arr[mm], label=labels[mm], zorder=-10.)
                mm += 1
                ax2.plot(rarr_plot, fdm_vsq, ls=ls_arr[mm], color=color_arr[mm],
                        lw=lw_arr[mm], label=labels[mm], zorder=-12.)
            else:
                ax2 = None

            if ylim is None:
                ylim = ax.get_ylim()


            if vline_loc[k] is not None:
                for vl, vls, vlb in zip(vline_loc[k], vline_lss[k], vline_labels[k]):
                    ax.axvline(x=vl, ls=vls, color='grey', label=vlb, zorder=-20.)

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)


            ########
            if ax2 is not None:
                ax2.set_ylim(ylims2[k])
                ax2.yaxis.set_minor_locator(MultipleLocator(0.05))
                ax2.tick_params(axis='y', direction='in', color=color_vsq, which='both')
                if (j == n_cols-1):
                    if ylabels2[k] is not None:
                        ax2.set_ylabel(ylabels2[k], fontsize=fontsize_labels_sm, color=color_vsq)
                    if (i < n_rows-1):
                        ax2.yaxis.set_major_locator(FixedLocator([0., 0.25, 0.5, 0.75, 1.]))
                        ax2.yaxis.set_major_formatter(FixedFormatter(["", "0.25", "0.50", "0.75", "1.00"]))
                    else:
                        ax2.yaxis.set_major_locator(MultipleLocator(0.25))
                    ax2.tick_params(axis='y', direction='in', color=color_vsq,
                            labelsize=fontsize_ticks_sm, colors=color_vsq)
                else:
                    ax2.yaxis.set_major_locator(MultipleLocator(0.25))
                    #ax2.tick_params(labelright='off')
                    ax2.set_yticklabels([])
            ########
            if logradius:
                ax.xaxis.set_minor_locator(MultipleLocator(0.1))
                if (j > 0) & (i == n_rows-1):
                    ax.xaxis.set_major_locator(FixedLocator([-2., -1., 0., 1., 2.]))
                    ax.xaxis.set_major_formatter(FixedFormatter(["", "-1", "0", "1", "2"]))
                else:
                    ax.xaxis.set_major_locator(MultipleLocator(1.))
            else:
                ax.xaxis.set_minor_locator(MultipleLocator(1.))
                if (j > 0) & (i == n_rows-1):
                    ax.xaxis.set_major_locator(FixedLocator([0., 5., 10., 15.]))
                    ax.xaxis.set_major_formatter(FixedFormatter(["", "5", "10", "15"]))
                else:
                    ax.xaxis.set_major_locator(MultipleLocator(5.))

            if typ == 'menc3D':
                ax.yaxis.set_minor_locator(MultipleLocator(0.2))
                ax.yaxis.set_major_locator(MultipleLocator(1.))
                pass
            elif typ == 'vcirc':
                ax.yaxis.set_minor_locator(MultipleLocator(10.))
                ax.yaxis.set_major_locator(MultipleLocator(50.))

            ax.tick_params(labelsize=fontsize_ticks)

            if xlabels[k] is not None:
                ax.set_xlabel(xlabels[k], fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if ylabels[k] is not None:
                ax.set_ylabel(ylabels[k], fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])


            if titles[k] is not None:
                ax.set_title(titles[k], fontsize=fontsize_title)

            if (k == 0) | ((i == n_rows -1) & (j == 0)) | ((i == 0) & (j == 1)):
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(len(yarrs))
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])



                ###############
                handlesax2, labelsax2 = ax2.get_legend_handles_labels()
                neworder2 = range(len(handlesax2))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handlesax2[ii])
                    labels_arr2.append(labelsax2[ii])

                ###############
                neworder3 = range(len(yarrs), len(handles))
                handles_arr3 = []
                labels_arr3 = []
                for ii in neworder3:
                    handles_arr3.append(handles[ii])
                    labels_arr3.append(labels_leg[ii])

                ###############
                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25
                loc3 = 'lower right'
                if logradius:
                    loc2 = 'upper left'
                else:
                    loc2 = 'upper left'

                if (k == 0):
                    legend1 = ax.legend(handles_arr, labels_arr,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc='lower right',
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend1)
                elif ((i == n_rows -1) & (j == 0)):
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc= loc2,
                        numpoints=1, scatterpoints=1,
                        handlelength = 3.5,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)
                elif ((i == 0) & (j == 1)):
                    legend3 = ax.legend(handles_arr3, labels_arr3,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc= loc3,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend3)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


#
def plot_fdm_calibration_3panel(Mstar_arr=None,
            Mbaryon_arr=[1.e10, 10**10.5, 1.e11],
            q_disk_arr = [0.01, 0.05, 0.1, 0.2, 0.25, 0.4, 0.6, 0.8, 1.],
            Mhalo_arr=[3.e11, 1.e12, 3.e12], halo_conc_arr=[4.,4.,4.],
            Reff_disk_arr = [3.,5.,7.],
            output_path=None, table_path=None, fileout=None,
            z=2.,
            n_disk=1., Reff_bulge=1., n_bulge=4., invq_bulge=1.,
            del_fDM=False):
    """
    Plot the calibration ratio between fDM(vcirc,Reff) / fDM(Menc,Reff)

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
        Path to directory containing the Sersic profile tables.

        z: float, optional
            Redshift (to determine NFW halo properties). Default: z=2.
        Mbaryon_arr: array_like, optional
            Array of total baryon mass to plot [Msun].
            Default: [1.e10, 10**10.5, 1.e11] Msun.
        q_disk_arr: array_like, optional
            Array of flattening for disk.
            Default: [0.01, 0.05, 0.1, 0.2, 0.25, 0.4, 0.6, 0.8, 1.]
        Mhalo_arr: array_like, optional
            Array of NFW halo masses within R200 (=M200) [Msun].
            Default: [3.e11, 1.e12, 3.e12] Msun.
        halo_conc_arr: array_like, optional
            Array of halo concentrations. Default: [4.,4.,4.]
        Reff_disk_arr: array_like, optional
            Sersic projected 2D half-light (assumed half-mass) radius of disk component [kpc].
            Default: [3.,5.,7.] kpc.
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge:    Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: Flattening of bulge componen. Default: invq_bulge = 1. (spherical)

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_fdm_calibration'
        if del_fDM:     fileout += '_del_fDM'
        fileout += '.pdf'

    # ++++++++++++++++
    # SETUP:
    if Mstar_arr is not None:
        # Override the other settings with "typical" values:
        Mbaryon_arr = []
        Mhalo_arr = []
        halo_conc_arr = []
        Reff_disk_arr = []

        for Mstar in Mstar_arr:
            lmstar = np.log10(Mstar)

            Reff_disk = _mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')
            fgas =      _fgas_scaling_relation_MS(z=z, lmstar=lmstar)

            Mhalo = _smhm_relation(z=z, lmstar=lmstar)
            halo_conc = _halo_conc_relation(z=z, lmhalo=np.log10(Mhalo))

            Mbaryon_arr.append(Mstar/(1.-fgas))
            Mhalo_arr.append(Mhalo)
            halo_conc_arr.append(halo_conc)
            Reff_disk_arr.append(Reff_disk)



    # ++++++++++++++++
    # plot:
    btstep = 0.05
    bt_arr=np.arange(0.,1.+btstep, btstep)


    q_disk_arr = np.array(q_disk_arr)
    invq_disk_arr = 1./q_disk_arr

    color_arr = []
    ls_arr = []
    labels = []
    lw_arr = []
    for q in q_disk_arr:
        if q <= 1.:
            color_arr.append(cmap_q(q))
            ls_arr.append('-')
        else:
            color_arr.append(cmapg(1./q))
            ls_arr.append('--')
        lw_arr.append(1.25)
        labels.append(r'$q_{0,\mathrm{disk}}'+r'={}$'.format(q))


    lss_bonus = ['-', '--', '-.']


    titles = []
    xlims = []
    ylims = []
    xlabels = []
    ylabels = []


    for j, Mbaryon in enumerate(Mbaryon_arr):
        titles.append(r'$\log_{10}(M_{\mathrm{baryon}}/M_{\odot})'+r'={:0.1f}$'.format(np.log10(Mbaryon)))
        xlabels.append(r'$B/T$')
        if j == 0:
            if del_fDM:
                ylabels.append(r'$[ (f_{\mathrm{DM}}^{v}-f_{\mathrm{DM}}^{m})/f_{\mathrm{DM}}^{m}](R_{e,\mathrm{disk}})$')
            else:
                ylabels.append(r'$f_{\mathrm{DM}}^{v}(R_{e,\mathrm{disk}})/f_{\mathrm{DM}}^{m}(R_{e,\mathrm{disk}})$')
        else:
            ylabels.append(None)

        xlims.append([0., 1.])
        if del_fDM:
            ylims.append([-0.15, 0.05])
        else:
            ylims.append([0.85, 1.05])


    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.55
    n_cols = len(Mbaryon_arr)
    n_rows = 1
    fac = 1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)


    wspace = 0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')


    ######################

    plot_cnt_q = 0
    for mm, invq_disk in enumerate(invq_disk_arr):
        if invq_disk in invq_disk_arr:
            ## Get mass, velocity components:
            # FASTER:
            ######################
            tab_disk =  table_io.read_profile_table(n=n_disk, invq=invq_disk, path=table_path)
            tab_disk_menc =    tab_disk['menc3D_sph']
            tab_disk_vcirc =   tab_disk['vcirc']
            tab_disk_rad =     tab_disk['r']
            tab_disk_Reff =    tab_disk['Reff']
            tab_disk_mass =    tab_disk['total_mass']

            # Clean up values inside rmin:  Add the value at r=0: menc=0
            if tab_disk['r'][0] > 0.:
                tab_disk_rad = np.append(0., tab_disk_rad)
                tab_disk_menc = np.append(0., tab_disk_menc)
                tab_disk_vcirc = np.append(0., tab_disk_vcirc)

            m_interp_disk = scp_interp.interp1d(tab_disk_rad, tab_disk_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
            v_interp_disk = scp_interp.interp1d(tab_disk_rad, tab_disk_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')

            ######################

            for i in range(n_rows):
                for j in range(n_cols):
                    k = i*n_cols + j

                    Mbaryon =   Mbaryon_arr[j]
                    Reff_disk = Reff_disk_arr[j]
                    Mhalo =     Mhalo_arr[j]
                    halo_conc = halo_conc_arr[j]

                    ax =        axes[k]
                    xlim =      xlims[k]
                    ylim =      ylims[k]
                    ylabel =    ylabels[k]
                    title =     titles[k]

                    ######################
                    fdm_menc = np.ones(len(bt_arr))* -99.
                    fdm_vsq = np.ones(len(bt_arr))* -99.

                    for ll, bt in enumerate(bt_arr):
                        menc_disk = (m_interp_disk(Reff_disk / Reff_disk * tab_disk_Reff) * (((1.-bt)*Mbaryon) / tab_disk_mass) )
                        vcirc_disk = (v_interp_disk(Reff_disk / Reff_disk * tab_disk_Reff) * np.sqrt(((1.-bt)*Mbaryon) / tab_disk_mass) * np.sqrt(tab_disk_Reff / Reff_disk))

                        menc_bulge = (m_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * ((bt*Mbaryon) / tab_bulge_mass) )
                        vcirc_bulge = (v_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))

                        menc_halo = calcs.NFW_halo_enclosed_mass(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                        menc_baryons = menc_disk + menc_bulge
                        menc_tot = menc_baryons + menc_halo
                        fdm_menc[ll] = menc_halo/menc_tot

                        vcirc_halo = calcs.NFW_halo_vcirc(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                        vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
                        vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
                        fdm_vsq[ll] = vcirc_halo**2/vcirc_tot**2

                    ######################

                    if del_fDM:
                        ax.plot(bt_arr, (fdm_vsq-fdm_menc)/fdm_menc, ls=ls_arr[mm], color=color_arr[mm], lw=lw_arr[mm], label=labels[mm])
                    else:
                        ax.plot(bt_arr, fdm_vsq/fdm_menc, ls=ls_arr[mm], color=color_arr[mm], lw=lw_arr[mm], label=labels[mm])
                        if k > 0:
                            if (mm == (len(invq_disk_arr) -1) ):
                                lbl_tmp = r'$\log_{10}(M_{\mathrm{bar}}/M_{\odot})='+r'{:0.2f}$'.format(np.log10(Mbaryon))
                            else:
                                lbl_tmp = None
                            axes[0].plot(bt_arr, fdm_vsq/fdm_menc, ls=lss_bonus[k], color=color_arr[mm], lw=lw_arr[mm], label=lbl_tmp)

            plot_cnt_q += 1

        else:
            # Missing invq_disk file
            pass

    ####
    # Go back and do plot formatting:
    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            Mbaryon =   Mbaryon_arr[j]
            Reff_disk = Reff_disk_arr[j]
            Mhalo =     Mhalo_arr[j]
            halo_conc = halo_conc_arr[j]

            ax =        axes[k]
            xlim =      xlims[k]
            ylim =      ylims[k]
            ylabel =    ylabels[k]
            title =     titles[k]

            if ylim is None:        ylim = ax.get_ylim()

            # Annotate:
            if k  == 0:
                padx = pady = 0.05
                xypos = (padx, 1.-pady)
                va = 'top'
                ha = 'left'
                ann_str_cnst = r'$R_{e,\mathrm{disk}}='+r'{:0.1f}'.format(Reff_disk)+r'\,\mathrm{kpc}$'
                ann_str_cnst += '\n'
                ann_str_cnst += r'$n_{\mathrm{disk}}='+r'{:0.1f}$'.format(n_disk)
                ax.annotate(ann_str_cnst, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                        color='darkblue', fontsize=fontsize_ann)  #


                pady = 0.04375
                xdelt = 0.35
                ann_str_cnst = r'$R_{e,\mathrm{bulge}}='+r'{:0.1f}'.format(Reff_bulge)+r'\,\mathrm{kpc}$'
                ann_str_cnst += '\n'
                ann_str_cnst += r'$n_{\mathrm{bulge}}='+r'{:0.1f}$'.format(n_bulge)
                ann_str_cnst += '\n'
                ann_str_cnst += r'$q_{0,\mathrm{bulge}}='+r'{:0.1f}$'.format(1./invq_bulge)
                xypos = (padx + xdelt, 1.-pady)
                ax.annotate(ann_str_cnst, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                        color='firebrick', fontsize=fontsize_ann)


            else:
                padx = pady = 0.05
                xypos = (padx, 1.-pady)
                va = 'top'
                ha = 'left'
                ann_str_cnst = r'$R_{e,\mathrm{disk}}='+r'{:0.1f}'.format(Reff_disk)+r'\,\mathrm{kpc}$'
                ax.annotate(ann_str_cnst, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                        color='darkblue', fontsize=fontsize_ann)

            ############
            padx = 0.045
            pady = 0.025
            xypos = (padx, pady)
            va = 'bottom'
            ha = 'left'
            ann_str = r'$\log_{10}(M_{\mathrm{bar}}/M_{\odot})'+r'={:0.2f}$'.format(np.log10(Mbaryon))
            ann_str += '\n'
            ann_str += r'$\log_{10}(M_{\mathrm{halo}}/M_{\odot})'+r'={:0.2f}$'.format(np.log10(Mhalo))
            ann_str += '\n'
            ann_str += r'$\mathrm{conc}_{\mathrm{halo}}'+r'={:0.1f}$'.format(halo_conc)
            ax.annotate(ann_str, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                    color='black', fontsize=fontsize_ann)


            if del_fDM:
                ax.axhline(y=0., ls=(0, (5,3)), color='darkgrey', zorder=-20.)
            else:
                ax.axhline(y=1., ls=(0, (5,3)), color='darkgrey', zorder=-20.)


            ax.set_xlim(xlim)
            ax.set_ylim(ylim)



            ########
            ax.xaxis.set_minor_locator(MultipleLocator(0.05))

            if (j > 0) & (i == n_rows-1):
                bt_loc = [0., 0.2, 0.4, 0.6, 0.8, 1.]
                bt_loc_str = ["{:0.1f}".format(bt) for bt in bt_loc]
                bt_loc_str[0] = ""
                ax.xaxis.set_major_locator(FixedLocator(bt_loc))
                ax.xaxis.set_major_formatter(FixedFormatter(bt_loc_str))
            else:
                ax.xaxis.set_major_locator(MultipleLocator(0.2))

            #
            ax.yaxis.set_minor_locator(MultipleLocator(0.01))
            ax.yaxis.set_major_locator(MultipleLocator(0.05))
            ax.tick_params(labelsize=fontsize_ticks)

            if xlabels[k] is not None:
                ax.set_xlabel(xlabels[k], fontsize=fontsize_labels)
            else:
                #ax.tick_params(labelbottom='off')
                ax.set_xticklabels([])

            if ylabels[k] is not None:
                ax.set_ylabel(ylabels[k], fontsize=fontsize_labels)
            else:
                #ax.tick_params(labelleft='off')
                ax.set_yticklabels([])


            if titles[k] is not None:
                ax.set_title(titles[k], fontsize=fontsize_title)


            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_q)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_q, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25

                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc='lower right',
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    loc2 = (1.05, 0.5)
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc=loc2,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

                    ax.set_zorder(1)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

#
def plot_fdm_calibration(Mstar_arr=None,
            Mbaryon_arr=[10**10.5],
            q_disk_arr = [0.01, 0.05, 0.1, 0.2, 0.25, 0.4, 0.6, 0.8, 1.],
            Mhalo_arr=[1.e12], halo_conc_arr=[4.],
            Reff_disk_arr = [5.],
            output_path=None, table_path=None, fileout=None,
            z=2.,
            n_disk=1., Reff_bulge=1., n_bulge=4., invq_bulge=1.,
            del_fDM=False):
    """
    Plot the calibration ratio between fDM(vcirc,Reff) / fDM(Menc,Reff)

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
        Path to directory containing the Sersic profile tables.

        z: float, optional
            Redshift (to determine NFW halo properties). Default: z=2.
        Mbaryon_arr: array_like, optional
            Array of total baryon mass to plot [Msun].
            Default: [10**10.5] Msun.
        q_disk_arr: array_like, optional
            Array of flattening for disk.
            Default: [0.01, 0.05, 0.1, 0.2, 0.25, 0.4, 0.6, 0.8, 1.]
        Mhalo_arr: array_like, optional
            Array of NFW halo masses within R200 (=M200) [Msun].
            Default: [1.e12] Msun.
        halo_conc_arr: array_like, optional
            Array of halo concentrations. Default: [4.]
        Reff_disk: array_like, optional
            Sersic projected 2D half-light (assumed half-mass) radius of disk component [kpc].
            Default: [5.] kpc
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge:    Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: Flattening of bulge componen. Default: invq_bulge = 1. (spherical)

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_fdm_calibration'
        if del_fDM:     fileout += '_del_fDM'
        fileout += '.pdf'

    # ++++++++++++++++
    # SETUP:
    if Mstar_arr is not None:
        # Override the other settings with "typical" values:
        Mbaryon_arr = []
        Mhalo_arr = []
        halo_conc_arr = []
        Reff_disk_arr = []

        for Mstar in Mstar_arr:
            lmstar = np.log10(Mstar)

            Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')
            fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

            Mhalo = utils._smhm_relation(z=z, lmstar=lmstar)
            halo_conc = utils._halo_conc_relation(z=z, lmhalo=np.log10(Mhalo))

            Mbaryon_arr.append(Mstar/(1.-fgas))
            Mhalo_arr.append(Mhalo)
            halo_conc_arr.append(halo_conc)
            Reff_disk_arr.append(Reff_disk)



    # ++++++++++++++++
    # plot:
    btstep = 0.05
    bt_arr=np.arange(0.,1.+btstep, btstep)


    q_disk_arr = np.array(q_disk_arr)
    invq_disk_arr = 1./q_disk_arr

    color_arr = []
    ls_arr = []
    labels = []
    lw_arr = []
    for q in q_disk_arr:
        if q <= 1.:
            color_arr.append(cmap_q(q))
            ls_arr.append('-')
        else:
            color_arr.append(cmapg(1./q))
            ls_arr.append('--')
        lw_arr.append(1.25)
        labels.append(r'$q_{0,\mathrm{disk}}'+r'={}$'.format(q))


    lss_bonus = ['-', '--', '-.']


    titles = []
    xlims = []
    ylims = []
    xlabels = []
    ylabels = []


    for j, Mbaryon in enumerate(Mbaryon_arr):
        titles.append(r'$\log_{10}(M_{\mathrm{baryon}}/M_{\odot})'+r'={:0.1f}$'.format(np.log10(Mbaryon)))
        xlabels.append(r'$B/T$')
        if j == 0:
            if del_fDM:
                ylabels.append(r'$[ (f_{\mathrm{DM}}^{v}-f_{\mathrm{DM}}^{m})/f_{\mathrm{DM}}^{m}](R_{e,\mathrm{disk}})$')
            else:
                ylabels.append(r'$f_{\mathrm{DM}}^{v}(R_{e,\mathrm{disk}})/f_{\mathrm{DM}}^{m}(R_{e,\mathrm{disk}})$')
        else:
            ylabels.append(None)

        xlims.append([0., 1.])
        if del_fDM:
            ylims.append([-0.15, 0.05])
        else:
            ylims.append([0.85, 1.05])


    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 4. #3.55
    n_cols = len(Mbaryon_arr)
    n_rows = 1
    fac = 1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)


    wspace = 0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')


    ######################

    plot_cnt_q = 0
    for mm, invq_disk in enumerate(invq_disk_arr):
        if invq_disk in invq_disk_arr:
            ## Get mass, velocity components:
            # FASTER:
            ######################
            tab_disk =  table_io.read_profile_table(n=n_disk, invq=invq_disk, path=table_path)
            tab_disk_menc =    tab_disk['menc3D_sph']
            tab_disk_vcirc =   tab_disk['vcirc']
            tab_disk_rad =     tab_disk['r']
            tab_disk_Reff =    tab_disk['Reff']
            tab_disk_mass =    tab_disk['total_mass']

            # Clean up values inside rmin:  Add the value at r=0: menc=0
            if tab_disk['r'][0] > 0.:
                tab_disk_rad = np.append(0., tab_disk_rad)
                tab_disk_menc = np.append(0., tab_disk_menc)
                tab_disk_vcirc = np.append(0., tab_disk_vcirc)

            m_interp_disk = scp_interp.interp1d(tab_disk_rad, tab_disk_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
            v_interp_disk = scp_interp.interp1d(tab_disk_rad, tab_disk_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')

            ######################

            for i in range(n_rows):
                for j in range(n_cols):
                    k = i*n_cols + j

                    Mbaryon =   Mbaryon_arr[j]
                    Reff_disk = Reff_disk_arr[j]
                    Mhalo =     Mhalo_arr[j]
                    halo_conc = halo_conc_arr[j]

                    ax =        axes[k]
                    xlim =      xlims[k]
                    ylim =      ylims[k]
                    ylabel =    ylabels[k]
                    title =     titles[k]

                    ######################
                    fdm_menc = np.ones(len(bt_arr))* -99.
                    fdm_vsq = np.ones(len(bt_arr))* -99.

                    for ll, bt in enumerate(bt_arr):
                        menc_disk = (m_interp_disk(Reff_disk / Reff_disk * tab_disk_Reff) * (((1.-bt)*Mbaryon) / tab_disk_mass) )
                        vcirc_disk = (v_interp_disk(Reff_disk / Reff_disk * tab_disk_Reff) * np.sqrt(((1.-bt)*Mbaryon) / tab_disk_mass) * np.sqrt(tab_disk_Reff / Reff_disk))

                        menc_bulge = (m_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * ((bt*Mbaryon) / tab_bulge_mass) )
                        vcirc_bulge = (v_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))

                        menc_halo = calcs.NFW_halo_enclosed_mass(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                        menc_baryons = menc_disk + menc_bulge
                        menc_tot = menc_baryons + menc_halo
                        fdm_menc[ll] = menc_halo/menc_tot

                        vcirc_halo = calcs.NFW_halo_vcirc(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                        vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
                        vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
                        fdm_vsq[ll] = vcirc_halo**2/vcirc_tot**2

                    ######################

                    if del_fDM:
                        ax.plot(bt_arr, (fdm_vsq-fdm_menc)/fdm_menc, ls=ls_arr[mm], color=color_arr[mm], lw=lw_arr[mm], label=labels[mm])
                    else:
                        ax.plot(bt_arr, fdm_vsq/fdm_menc, ls=ls_arr[mm], color=color_arr[mm], lw=lw_arr[mm], label=labels[mm])
                        if k > 0:
                            if (mm == (len(invq_disk_arr) -1) ):
                                lbl_tmp = r'$\log_{10}(M_{\mathrm{bar}}/M_{\odot})='+r'{:0.2f}$'.format(np.log10(Mbaryon))
                            else:
                                lbl_tmp = None
                            axes[0].plot(bt_arr, fdm_vsq/fdm_menc, ls=lss_bonus[k], color=color_arr[mm], lw=lw_arr[mm], label=lbl_tmp)

            plot_cnt_q += 1

        else:
            # Missing invq_disk file
            pass

    ####
    # Go back and do plot formatting:
    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            Mbaryon =   Mbaryon_arr[j]
            Reff_disk = Reff_disk_arr[j]
            Mhalo =     Mhalo_arr[j]
            halo_conc = halo_conc_arr[j]

            ax =        axes[k]
            xlim =      xlims[k]
            ylim =      ylims[k]
            ylabel =    ylabels[k]
            title =     titles[k]

            if ylim is None:        ylim = ax.get_ylim()

            # Annotate:
            if k  == 0:
                padx = pady = 0.05
                xypos = (padx, 1.-pady)
                va = 'top'
                ha = 'left'
                ann_str_cnst = r'$R_{e,\mathrm{disk}}='+r'{:0.1f}'.format(Reff_disk)+r'\,\mathrm{kpc}$'
                ann_str_cnst += '\n'
                ann_str_cnst += r'$n_{\mathrm{disk}}='+r'{:0.1f}$'.format(n_disk)
                ax.annotate(ann_str_cnst, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                        color='darkblue', fontsize=fontsize_ann)  #


                pady = 0.04375
                xdelt = 0.35
                ann_str_cnst = r'$R_{e,\mathrm{bulge}}='+r'{:0.1f}'.format(Reff_bulge)+r'\,\mathrm{kpc}$'
                ann_str_cnst += '\n'
                ann_str_cnst += r'$n_{\mathrm{bulge}}='+r'{:0.1f}$'.format(n_bulge)
                ann_str_cnst += '\n'
                ann_str_cnst += r'$q_{0,\mathrm{bulge}}='+r'{:0.1f}$'.format(1./invq_bulge)
                xypos = (padx + xdelt, 1.-pady)
                ax.annotate(ann_str_cnst, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                        color='firebrick', fontsize=fontsize_ann)


            else:
                padx = pady = 0.05
                xypos = (padx, 1.-pady)
                va = 'top'
                ha = 'left'
                ann_str_cnst = r'$R_{e,\mathrm{disk}}='+r'{:0.1f}'.format(Reff_disk)+r'\,\mathrm{kpc}$'
                ax.annotate(ann_str_cnst, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                        color='darkblue', fontsize=fontsize_ann)

            ############
            padx = 0.045
            pady = 0.025
            xypos = (padx, pady)
            va = 'bottom'
            ha = 'left'
            ann_str = r'$\log_{10}(M_{\mathrm{bar}}/M_{\odot})'+r'={:0.2f}$'.format(np.log10(Mbaryon))
            ann_str += '\n'
            ann_str += r'$\log_{10}(M_{\mathrm{halo}}/M_{\odot})'+r'={:0.2f}$'.format(np.log10(Mhalo))
            ann_str += '\n'
            ann_str += r'$\mathrm{conc}_{\mathrm{halo}}'+r'={:0.1f}$'.format(halo_conc)
            ax.annotate(ann_str, xy=xypos, xycoords='axes fraction', ha=ha, va=va,
                    color='black', fontsize=fontsize_ann)


            if del_fDM:
                ax.axhline(y=0., ls=(0, (5,3)), color='darkgrey', zorder=-20.)
            else:
                ax.axhline(y=1., ls=(0, (5,3)), color='darkgrey', zorder=-20.)


            ax.set_xlim(xlim)
            ax.set_ylim(ylim)



            ########
            ax.xaxis.set_minor_locator(MultipleLocator(0.05))

            if (j > 0) & (i == n_rows-1):
                bt_loc = [0., 0.2, 0.4, 0.6, 0.8, 1.]
                bt_loc_str = ["{:0.1f}".format(bt) for bt in bt_loc]
                bt_loc_str[0] = ""
                ax.xaxis.set_major_locator(FixedLocator(bt_loc))
                ax.xaxis.set_major_formatter(FixedFormatter(bt_loc_str))
            else:
                ax.xaxis.set_major_locator(MultipleLocator(0.2))

            #
            ax.yaxis.set_minor_locator(MultipleLocator(0.01))
            ax.yaxis.set_major_locator(MultipleLocator(0.05))
            ax.tick_params(labelsize=fontsize_ticks)

            if xlabels[k] is not None:
                ax.set_xlabel(xlabels[k], fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if ylabels[k] is not None:
                ax.set_ylabel(ylabels[k], fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])


            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_q)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_q, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25

                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc='lower right',
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    loc2 = (1.05, 0.5)
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc=loc2,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

                    ax.set_zorder(1)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


def plot_toy_impl_fDM_calibration_z_evol(lmstar_arr=None,
            output_path=None, table_path=None, fileout=None,
            n_disk=1., Reff_bulge=1., n_bulge=4., invq_bulge=1.,
            del_fDM=False,
            save_dict_stack=True,
            overwrite_dict_stack=False,
            include_toy_curves=True):
    """
    Plot "typical" change of difference between fDM calibrations
    fDM(vcirc,Reff) / fDM(Menc,Reff) with redshift for SF, roughly MS galaxies,
    for different stellar masses.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
        Path to directory containing the Sersic profile tables.

        z: float, optional
            Redshift (to determine NFW halo properties). Default: z=2.
        lmstar_arr: array_like, optional
            Array of the log of the total stellar mass [logMsun].
            Default: [9.0, 9.5, 10., 10.5, 11.] logMsun.
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge
            component [kpc].  Default: 1kpc
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)

        include_toy_curves: bool, optional
            Include curves showing assumed interpolated / extrapolated parameters
            curves used to construct the toy MS model. Default: True

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_toy_fdm_calibration_z_evol'
        if del_fDM:     fileout += '_del_fDM'
        fileout += '.pdf'


    mpl.rcParams['text.usetex'] = True

    if lmstar_arr is None:
        lm_step = 0.25
        lmstar_arr = np.arange(9.0, 11.+lm_step, lm_step)

    # Ensure it's an np array, not a list:
    lmstar_arr = np.array(lmstar_arr)


    # ++++++++++++++++
    # plot:

    zstep = 0.1
    z_arr = np.arange(0., 3.+zstep, zstep)

    color_arr = []
    ls_arr = []
    labels = []
    lw_arr = []
    for lmstar in lmstar_arr:
        color_arr.append(cmap_mass( (lmstar-lmstar_arr.min())/(lmstar_arr.max()-lmstar_arr.min()) ) )
        if ((lmstar % 1.) == 0):
            lw_arr.append(2.) #1.75)
            ls_arr.append('-')
        else:
            lw_arr.append(1.)
            ls_arr.append('-')

        if ((lmstar % 1.) == 0):
            labels.append(r'${:2.0f}$'.format(lmstar))
        elif ((lmstar*2. % 1.) == 0):
            labels.append(r'${:2.1f}$'.format(lmstar))
        else:
            labels.append(r'${:2.2f}$'.format(lmstar))


    xlabel = r'$z$'
    if del_fDM:
        ylabel = r'$[ (f_{\mathrm{DM}}^{v}-f_{\mathrm{DM}}^{m})/f_{\mathrm{DM}}^{m}](R_{e,\mathrm{disk}})$'
    else:
        ylabel = r'$f_{\mathrm{DM}}^{v}(R_{e,\mathrm{disk}})/f_{\mathrm{DM}}^{m}(R_{e,\mathrm{disk}})$'
    ylabels = [r'$f_{\mathrm{DM}}^{v}(R_{e,\mathrm{disk}})$',
               r'$f_{\mathrm{DM}}^{m}(R_{e,\mathrm{disk}})$',
               ylabel]
    xlim = [0., 3.]
    ylim = [0.9, 1.01]
    ylims = [[0.,1.],[0.,1.], [0.9, 1.01]]

    types = ['fdm_vsq', 'fdm_menc', 'fDM_comp']


    ann_arr = [ r'$\displaystyle f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}}) = \frac{v_{\mathrm{circ,DM}}^2(R_{e,\mathrm{disk}})}{v_{\mathrm{circ,tot}}^2(R_{e,\mathrm{disk}})}$',
                r'$\displaystyle f_{\mathrm{DM}}^m(R_{e,\mathrm{disk}}) = \frac{M_{\mathrm{DM,sph}}(<r=R_{e,\mathrm{disk}})}{M_{\mathrm{tot,sph}}(<r=R_{e,\mathrm{disk}})}$',
                None]
    ann_arr_pos = ['upperleft', 'upperright', None]

    if include_toy_curves:
        keys_toy = ['Reff_disk', 'invq_disk', 'fgas', 'bt', 'lMhalo', 'halo_conc']
        ylabels_toy = []
        ylims_toy = []
        ylocators_toy = []
        for keyt in keys_toy:
            if keyt == 'Reff_disk':
                ylabels_toy.append(r'$R_{e,\mathrm{disk}}$ [kpc]')
                ylims_toy.append([0., 12.]) #20.])
                ylocators_toy.append([1.,5.])
            elif keyt == 'invq_disk':
                ylabels_toy.append(r'$1/q_{0,\mathrm{disk}}$')
                ylims_toy.append([0., 12.]) # 20.])
                ylocators_toy.append([1.,5.])
            elif keyt == 'fgas':
                ylabels_toy.append(r'$f_{\mathrm{gas}}$')
                ylims_toy.append([0., 1.])
                ylocators_toy.append([0.05, 0.5]) #[0.05,0.2])
            elif keyt == 'lMbar':
                ylabels_toy.append(r'$\log_{10}(M_{\mathrm{bar}}/M_{\odot})$')
                ylims_toy.append([8.8, 11.6]) #[9., 13.])
                ylocators_toy.append([0.2,1.])
            elif keyt == 'bt':
                ylabels_toy.append(r'$B/T$')
                ylims_toy.append([0., 1.])
                ylocators_toy.append([0.05, 0.5]) #[0.05,0.2])
            elif keyt == 'lMhalo':
                ylabels_toy.append(r'$\log_{10}(M_{\mathrm{halo}}/M_{\odot})$')
                ylims_toy.append([10.8, 13.2]) #9., 15.])
                ylocators_toy.append([0.2,1.])
            elif keyt == 'halo_conc':
                ylabels_toy.append(r'$c_{\mathrm{halo}}$')
                ylims_toy.append([2., 12.]) #0., 20.])
                ylocators_toy.append([1.,5.])
            else:
                raise ValueError

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 2.8 #3.25  #3.75 #4.25
    n_cols = len(types)
    if include_toy_curves:
        n_rows = 2
        if len(keys_toy) == 7:
            fac = 1.5 #1.725 #1.15*1.5
        elif len(keys_toy) == 6:
            fac = 1.45
    else:
        n_rows = 1
        fac = 1.15 #1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)


    if include_toy_curves:
        wspace = 0.25 #0.025
        hspace = wspace
        if len(keys_toy) == 7:
            height_ratios=[0.4, 1.]
        elif len(keys_toy) == 6:
            height_ratios=[0.45, 1.]
        else:
            height_ratios=[len(types)/len(keys_toy), 1.]

        gs_outer = gridspec.GridSpec(2, 1, wspace=wspace, hspace=hspace, height_ratios=height_ratios)

        wspace = 0.35 #0.25 #0.025
        hspace = wspace
        gs0 = gridspec.GridSpecFromSubplotSpec(1, len(keys_toy),subplot_spec=gs_outer[0,0],
                wspace=wspace, hspace=hspace )
        axes_toy = []
        for i in range(1):
            for j in range(len(keys_toy)):
                axes_toy.append(plt.subplot(gs0[i,j]))

        wspace = 0.25 #0.025
        hspace = wspace
        gs = gridspec.GridSpecFromSubplotSpec(1, n_cols,subplot_spec=gs_outer[1,0],
                wspace=wspace, hspace=hspace )
        axes = []
        for i in range(1):
            for j in range(n_cols):
                axes.append(plt.subplot(gs[i,j]))
    else:
        wspace = 0.25 #0.025
        hspace = wspace
        gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
        axes = []
        for i in range(n_rows):
            for j in range(n_cols):
                axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')


    ######################

    dict_stack = None
    f_save = output_path+'toy_impl_fDM_calibration_z.pickle'
    if save_dict_stack:
        if (os.path.isfile(f_save)):
            with open(f_save, 'rb') as f:
                dict_stack = copy.deepcopy(pickle.load(f))


            if overwrite_dict_stack:
                raise ValueError("Really shouldn't do this!")
                os.remove(f_save)
                dict_stack = None


    if dict_stack is None:
        dict_stack = []
        for mm, lmstar in enumerate(lmstar_arr):
            print("lmstar={}".format(lmstar))
            val_dict = {'z_arr': z_arr,
                        'lmstar': np.ones(len(z_arr)) * lmstar,
                        'bt': np.ones(len(z_arr)) * -99.,
                        'Reff_disk': np.ones(len(z_arr)) * -99.,
                        'invq_disk': np.ones(len(z_arr)) * -99.,
                        'invq_near': np.ones(len(z_arr)) * -99.,
                        'fgas': np.ones(len(z_arr)) * -99.,
                        'lMbar': np.ones(len(z_arr)) * -99.,
                        'lMhalo': np.ones(len(z_arr)) * -99.,
                        'Rvir': np.ones(len(z_arr)) * -99.,
                        'halo_conc': np.ones(len(z_arr)) * -99.,

                        'menc_disk': np.ones(len(z_arr)) * -99.,
                        'menc_bulge': np.ones(len(z_arr)) * -99.,
                        'menc_halo': np.ones(len(z_arr)) * -99.,
                        'menc_bar': np.ones(len(z_arr)) * -99.,
                        'menc_tot': np.ones(len(z_arr)) * -99.,
                        'fdm_menc': np.ones(len(z_arr)) * -99.,
                        'vcirc_disk': np.ones(len(z_arr)) * -99.,
                        'vcirc_bulge': np.ones(len(z_arr)) * -99.,
                        'vcirc_halo': np.ones(len(z_arr)) * -99.,
                        'vcirc_bar': np.ones(len(z_arr)) * -99.,
                        'vcirc_tot': np.ones(len(z_arr)) * -99.,
                        'fdm_vsq': np.ones(len(z_arr)) * -99.,
                        'fDM_comp': np.ones(len(z_arr)) * -99.
                        }
            for ll, z in enumerate(z_arr):
                print("  z={}".format(z))
                Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')

                invq_disk = utils._invq_disk_lmstar_estimate(z=z, lmstar=lmstar)

                fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

                Mstar =     np.power(10., lmstar)
                Mbaryon =   Mstar / (1.-fgas)
                lMbar = np.log10(Mbaryon)

                bt =        utils._bt_lmstar_relation(z=z, lmstar=lmstar, galtype='sf')

                Mhalo =     utils._smhm_relation(z=z, lmstar=lmstar)
                Rvir = calcs.halo_rvir(Mvirial=Mhalo, z=z)
                lMhalo = np.log10(Mhalo)
                halo_conc = utils._halo_conc_relation(z=z, lmhalo=lMhalo)

                val_dict['bt'][ll] = bt
                val_dict['Reff_disk'][ll] = Reff_disk
                val_dict['invq_disk'][ll] = invq_disk
                val_dict['fgas'][ll] = fgas
                val_dict['lMbar'][ll] = lMbar
                val_dict['lMhalo'][ll] = lMhalo
                val_dict['Rvir'][ll] = Rvir
                val_dict['halo_conc'][ll] = halo_conc


                ######
                nearest_n, nearest_invq = n_disk, invq_disk
                try:
                    menc_disk = calcs.interpolate_sersic_profile_menc(r=Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                    vcirc_disk = calcs.interpolate_sersic_profile_VC(r=Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)

                except:
                    menc_disk = calcs.M_encl_3D(Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, q=1./invq_disk, i=90.)
                    vcirc_disk = calcs.v_circ(Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, q=1./invq_disk, i=90.)

                menc_bulge = (m_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * ((bt*Mbaryon) / tab_bulge_mass) )
                vcirc_bulge = (v_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))

                menc_halo = calcs.NFW_halo_enclosed_mass(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                menc_baryons = menc_disk + menc_bulge
                menc_tot = menc_baryons + menc_halo
                fdm_menc = menc_halo/menc_tot

                vcirc_halo = calcs.NFW_halo_vcirc(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
                vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
                fdm_vsq = vcirc_halo**2/vcirc_tot**2

                #fDM_compare_arr
                if del_fDM:
                    val_dict['fDM_comp'][ll] = (fdm_vsq-fdm_menc)/fdm_menc
                else:
                    val_dict['fDM_comp'][ll] = fdm_vsq/fdm_menc

                ####

                val_dict['menc_disk'][ll] = menc_disk
                val_dict['menc_bulge'][ll] = menc_bulge
                val_dict['menc_halo'][ll] = menc_halo
                val_dict['menc_bar'][ll] = menc_baryons
                val_dict['menc_tot'][ll] = menc_tot
                val_dict['fdm_menc'][ll] = fdm_menc

                val_dict['vcirc_disk'][ll] = vcirc_disk
                val_dict['vcirc_bulge'][ll] = vcirc_bulge
                val_dict['vcirc_halo'][ll] = vcirc_halo
                val_dict['vcirc_bar'][ll] = vcirc_baryons
                val_dict['vcirc_tot'][ll] = vcirc_tot
                val_dict['fdm_vsq'][ll] = fdm_vsq

                val_dict['invq_near'][ll] = nearest_invq

            ##
            dict_stack.append(val_dict)



    dict_toy = None
    f_save_toy = output_path+'toy_impl_fDM_calibration_z_MW_M31.pickle'
    if save_dict_stack:
        if (os.path.isfile(f_save_toy)):
            with open(f_save_toy, 'rb') as f:
                dict_toy = copy.deepcopy(pickle.load(f))

            if overwrite_dict_stack:
                raise ValueError("Really shouldn't do this!")
                os.remove(f_save_toy)
                dict_toy = None
    if dict_toy is None:
        dict_toy = {}
        #z_arr_toy = z_arr
        ztoystep = 0.05
        z_arr_toy = np.arange(z_arr.min(), z_arr.max()+ztoystep, ztoystep)
        names = ['MW', 'M31']
        ln0_arr = [-2.9, -3.4]
        n_evol='const'
        cmf_source='papovich15'
        for name, ln0 in zip(names, ln0_arr):
            print("Toy model: {}".format(name))
            val_dict = {'z_arr': z_arr_toy,
                        'lmstar': np.ones(len(z_arr_toy)) * -99,
                        'bt': np.ones(len(z_arr_toy)) * -99.,
                        'Reff_disk': np.ones(len(z_arr_toy)) * -99.,
                        'invq_disk': np.ones(len(z_arr_toy)) * -99.,
                        'invq_near': np.ones(len(z_arr_toy)) * -99.,
                        'fgas': np.ones(len(z_arr_toy)) * -99.,
                        'lMbar': np.ones(len(z_arr_toy)) * -99.,
                        'lMhalo': np.ones(len(z_arr_toy)) * -99.,
                        'Rvir': np.ones(len(z_arr_toy)) * -99.,
                        'halo_conc': np.ones(len(z_arr_toy)) * -99.,

                        'menc_disk': np.ones(len(z_arr_toy)) * -99.,
                        'menc_bulge': np.ones(len(z_arr_toy)) * -99.,
                        'menc_halo': np.ones(len(z_arr_toy)) * -99.,
                        'menc_bar': np.ones(len(z_arr_toy)) * -99.,
                        'menc_tot': np.ones(len(z_arr_toy)) * -99.,
                        'fdm_menc': np.ones(len(z_arr_toy)) * -99.,
                        'vcirc_disk': np.ones(len(z_arr_toy)) * -99.,
                        'vcirc_bulge': np.ones(len(z_arr_toy)) * -99.,
                        'vcirc_halo': np.ones(len(z_arr_toy)) * -99.,
                        'vcirc_bar': np.ones(len(z_arr_toy)) * -99.,
                        'vcirc_tot': np.ones(len(z_arr_toy)) * -99.,
                        'fdm_vsq': np.ones(len(z_arr_toy)) * -99.,
                        'fDM_comp': np.ones(len(z_arr_toy)) * -99.,
                        'n_evol': n_evol,
                        'cmf_source': cmf_source,
                        'name': name,
                        }
            val_dict['lmstar'] = _mass_progenitor_num_density(ln0, z_arr_toy,
                        n_evol=n_evol, cmf_source=cmf_source)
            for ll, z in enumerate(z_arr_toy):
                print("  z={}".format(z))

                lmstar = val_dict['lmstar'][ll]
                Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')

                invq_disk = utils._invq_disk_lmstar_estimate(z=z, lmstar=lmstar)

                fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

                Mstar =     np.power(10., lmstar)
                Mbaryon =   Mstar / (1.-fgas)
                lMbar = np.log10(Mbaryon)

                bt =        utils._bt_lmstar_relation(z=z, lmstar=lmstar, galtype='sf')

                Mhalo =     utils._smhm_relation(z=z, lmstar=lmstar)
                Rvir = calcs.halo_rvir(Mvirial=Mhalo, z=z)
                lMhalo = np.log10(Mhalo)
                halo_conc = utils._halo_conc_relation(z=z, lmhalo=lMhalo)

                val_dict['bt'][ll] = bt
                val_dict['Reff_disk'][ll] = Reff_disk
                val_dict['invq_disk'][ll] = invq_disk
                val_dict['fgas'][ll] = fgas
                val_dict['lMbar'][ll] = lMbar
                val_dict['lMhalo'][ll] = lMhalo
                val_dict['Rvir'][ll] = Rvir
                val_dict['halo_conc'][ll] = halo_conc


                ######
                nearest_n, nearest_invq = n_disk, invq_disk
                try:
                    menc_disk = calcs.interpolate_sersic_profile_menc(r=Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                    vcirc_disk = calcs.interpolate_sersic_profile_VC(r=Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)

                except:
                    menc_disk = calcs.M_encl_3D(Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, q=1./invq_disk, i=90.)
                    vcirc_disk = calcs.v_circ(Reff_disk, total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, q=1./invq_disk, i=90.)

                menc_bulge = (m_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * ((bt*Mbaryon) / tab_bulge_mass) )
                vcirc_bulge = (v_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))

                menc_halo = calcs.NFW_halo_enclosed_mass(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                menc_baryons = menc_disk + menc_bulge
                menc_tot = menc_baryons + menc_halo
                fdm_menc = menc_halo/menc_tot

                vcirc_halo = calcs.NFW_halo_vcirc(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
                vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
                fdm_vsq = vcirc_halo**2/vcirc_tot**2

                #fDM_compare_arr
                if del_fDM:
                    val_dict['fDM_comp'][ll] = (fdm_vsq-fdm_menc)/fdm_menc
                else:
                    val_dict['fDM_comp'][ll] = fdm_vsq/fdm_menc

                ####

                val_dict['menc_disk'][ll] = menc_disk
                val_dict['menc_bulge'][ll] = menc_bulge
                val_dict['menc_halo'][ll] = menc_halo
                val_dict['menc_bar'][ll] = menc_baryons
                val_dict['menc_tot'][ll] = menc_tot
                val_dict['fdm_menc'][ll] = fdm_menc

                val_dict['vcirc_disk'][ll] = vcirc_disk
                val_dict['vcirc_bulge'][ll] = vcirc_bulge
                val_dict['vcirc_halo'][ll] = vcirc_halo
                val_dict['vcirc_bar'][ll] = vcirc_baryons
                val_dict['vcirc_tot'][ll] = vcirc_tot
                val_dict['fdm_vsq'][ll] = fdm_vsq

                val_dict['invq_near'][ll] = nearest_invq

            ##
            dict_toy[name] = val_dict

    if save_dict_stack:
        if not (os.path.isfile(f_save)):
            with open(f_save, 'wb') as f:
                pickle.dump(dict_stack, f)

        if not (os.path.isfile(f_save_toy)):
            with open(f_save_toy, 'wb') as f:
                pickle.dump(dict_toy, f)


    ######################
    # FOR TOY PLOTS
    if include_toy_curves:
        for i in range(1):
            for j in range(len(keys_toy)):
                k = i*n_cols + j

                ax = axes_toy[k]
                keyy = keys_toy[j]
                ylim = ylims_toy[j]
                ylabel = ylabels_toy[j]

                plot_cnt_lmstar = 0
                for mm, lmstar in enumerate(lmstar_arr):
                    #if ((lmstar*2. % 1.) == 0):
                    if True:
                        ax.plot(dict_stack[mm]['z_arr'], dict_stack[mm][keyy], ls=ls_arr[mm],
                                   color=color_arr[mm], lw=lw_arr[mm], label=labels[mm],
                                   zorder=-1.)

                        plot_cnt_lmstar += 1

                for name, color, m, s,zord in zip(['MW', 'M31'], ['black', 'grey'],
                                            ['*', 's'], [15, 7.5], [-0.5, -0.6]):
                    whshow = np.where(((dict_toy[name]['z_arr'])%0.25 == 0))[0]
                    ax.scatter(dict_toy[name]['z_arr'][whshow], dict_toy[name][keyy][whshow],
                               color=color, facecolor='none',
                               lw=0.5, marker=m, s=s, label=name,zorder=zord)

                ######################
                if ylim is None:        ylim = ax.get_ylim()

                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ########
                ax.xaxis.set_minor_locator(MultipleLocator(0.2))
                ax.xaxis.set_major_locator(MultipleLocator(1.))

                ax.yaxis.set_minor_locator(MultipleLocator(ylocators_toy[j][0]))
                ax.yaxis.set_major_locator(MultipleLocator(ylocators_toy[j][1]))

                if xlabel is not None:
                    ax.set_xlabel(xlabel, fontsize=fontsize_labels_sm-2)
                else:
                    ax.set_xticklabels([])

                if ylabel is not None:
                    ax.set_ylabel(ylabel, fontsize=fontsize_labels_sm-2, labelpad=2)
                else:
                    ax.set_yticklabels([])

                ax.tick_params(labelsize=fontsize_ticks_sm-2)

    ######################
    # FOR JUST THE fDM PLOTS!
    n_rows = 1

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            ax = axes[k]
            keyy = types[j]
            ylim = ylims[j]
            ylabel = ylabels[j]

            plot_cnt_lmstar = 0
            for mm, lmstar in enumerate(lmstar_arr):
                if True:
                    ax.plot(dict_stack[mm]['z_arr'], dict_stack[mm][keyy], ls=ls_arr[mm],
                               color=color_arr[mm], lw=lw_arr[mm], label=labels[mm],
                               zorder=-1.)

                    plot_cnt_lmstar += 1

            #####################
            for name, color, m, s,zord in zip(['MW', 'M31'], ['black', 'grey'],
                                        ['*', 's'], [30, 15], [-0.5, -0.6]):
                whshow = np.where(((dict_toy[name]['z_arr'])%0.25 == 0))[0]
                ax.scatter(dict_toy[name]['z_arr'][whshow], dict_toy[name][keyy][whshow],
                           color=color, facecolor='none', marker=m, s=s,
                           lw=0.7, label=name,zorder=zord)

            ######################
            if ylim is None:        ylim = ax.get_ylim()

            if keyy == 'fDM_comp':
                if del_fDM:
                    ax.axhline(y=0., ls=(0, (5,3)), color='darkgrey', zorder=-20.)
                else:
                    ax.axhline(y=1., ls=(0, (5,3)), color='darkgrey', zorder=-20.)

            if ann_arr[j] is not None:
                xydelt = 0.04
                if ann_arr_pos[j] == 'lowerright':
                    xy = (1.-xydelt, xydelt)
                    va='bottom'
                    ha='right'
                elif ann_arr_pos[j] == 'upperright':
                    xy = (1.-xydelt, 1.-xydelt)
                    va='top'
                    ha='right'
                elif ann_arr_pos[j] == 'upperleft':
                    xy = (xydelt, 1.-xydelt)
                    va='top'
                    ha='left'
                ax.annotate(ann_arr[j], xy=xy,
                        va=va, ha=ha, fontsize=fontsize_ann-0.5, #fontsize_ann_latex
                        xycoords='axes fraction')

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            ########
            ax.xaxis.set_minor_locator(MultipleLocator(0.2))
            ax.xaxis.set_major_locator(MultipleLocator(1.))

            if keyy == 'fDM_comp':
                ax.yaxis.set_minor_locator(MultipleLocator(0.01))
                ax.yaxis.set_major_locator(MultipleLocator(0.05))
            else:
                ax.yaxis.set_minor_locator(MultipleLocator(0.05))
                ax.yaxis.set_major_locator(MultipleLocator(0.2))

            if xlabel is not None:
                ax.set_xlabel(xlabel, fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if ylabel is not None:
                ax.set_ylabel(ylabel, fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            ax.tick_params(labelsize=fontsize_ticks)

            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_lmstar)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_lmstar, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25
                loc = 'upper right' #'lower right'
                leg_title = r'$\log_{10}(M_{\star}/M_{\odot})=$'
                fontsize_leg_title = fontsize_leg
                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc=loc,
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp,
                    title=leg_title, title_fontsize=fontsize_leg_title)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc='lower left',
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


    mpl.rcParams['text.usetex'] = False

    return None


def plot_toy_AD_apply_z(lmstar = None, z_arr=None,
            output_path=None, table_path=None, fileout=None,
            n_disk=1., Reff_bulge=1., n_bulge=4., invq_bulge=1.,
            save_dict_stack=True,
            overwrite_dict_stack=False,
            show_sigmar_toy=False):
    """
    Plot example applying asymmetric drift of different kinds to vcirc curves
    to yield predicted vrot curves.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lmstar: float, optional
            Log of the total stellar mass [logMsun]. Default: 10.5 logMsun
        z_arr: array_like, optional
            Redshifts to show example. Default: [0.5, 1., 1.5, 2., 2.5]
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_toy_AD_apply_z'
        if show_sigmar_toy:
            fileout += "_sigmar_toy"
        fileout += '.pdf'

    mpl.rcParams['text.usetex'] = False

    if lmstar is None:
        lmstar = 10.5

    if z_arr is None:
        z_step = 0.5
        z_arr = np.arange(0.5, 2.5+z_step, z_step)

    # Ensure it's an np array, not a list:
    z_arr = np.array(z_arr)

    rstep = 0.1 # kpc
    r_arr = np.arange(0., 20.+rstep, rstep)

    # ++++++++++++++++
    titles = []
    for z in z_arr:
        if (z %1 == 0):
            titles.append(r'$z={:0.0f}$'.format(z))
        else:
            titles.append(r'$z={:0.1f}$'.format(z))

    xlabel = r'$r$ [kpc]'
    ylabel = r'$v(r)$ [km/s]'
    xlim = [0., 20.]
    ylim = [0., 300.]

    types = ['alphan', 'SG']
    ls_arr = ['--', ':']
    color_arr = ['black', 'black']
    lw_arr = [1.3, 1.3]
    labels = [r'$v_{\mathrm{rot}},\ \alpha(n)$', r'$v_{\mathrm{rot}},\ \alpha_{\mathrm{SG}}$']

    if show_sigmar_toy:
        ann_arr = [ None, r'$\log_{10}(M_*/M_{\odot})'+r'={:0.1f}$'.format(lmstar), None, None, None]
        ann_arr_pos = [None, 'upperright', None, None, None]
    else:
        ann_arr = [ r'$\log_{10}(M_*/M_{\odot})'+r'={:0.1f}$'.format(lmstar), None, None, None, None]
        ann_arr_pos = ['upperright', None, None, None, None]

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 2.75 #3.25 #3.75 #4.25
    n_cols = len(z_arr)
    n_rows = 1
    fac = 1.05 #1.15 #1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)


    wspace = 0.075 #0.1 #0.25 #0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')

    ######################
    dict_stack = None
    f_save = output_path+'toy_impl_AD_apply_z.pickle'
    if save_dict_stack:
        if (os.path.isfile(f_save)):
            with open(f_save, 'rb') as f:
                dict_stack = copy.deepcopy(pickle.load(f))

            if overwrite_dict_stack:
                raise ValueError("Really shouldn't do this!")
                os.remove(f_save)
                dict_stack = None

    if dict_stack is None:
        dict_stack = []
        for mm, z in enumerate(z_arr):
            print("z={}".format(z))
            val_dict = {'z':            z,
                        'r_arr':        r_arr,
                        'lmstar':       lmstar,
                        'bt':           -99.,
                        'Reff_disk':    -99.,
                        'invq_disk':    -99.,
                        'invq_near':    -99.,
                        'fgas':         -99.,
                        'lMbar':        -99.,
                        'lMhalo':       -99.,
                        'Rvir':         -99.,
                        'halo_conc':    -99.,
                        'sigma0':       -99.,

                        'vcirc_disk':   np.ones(len(r_arr)) * -99.,
                        'vcirc_bulge':  np.ones(len(r_arr)) * -99.,
                        'vcirc_halo':   np.ones(len(r_arr)) * -99.,
                        'vcirc_bar':    np.ones(len(r_arr)) * -99.,
                        'vcirc_tot':    np.ones(len(r_arr)) * -99.,

                        'alphan':       np.ones(len(r_arr)) * -99.,
                        'alpha_SG':     np.ones(len(r_arr)) * -99.,

                        'vrot_alphan':  np.ones(len(r_arr)) * -99.,
                        'vrot_SG':      np.ones(len(r_arr)) * -99.
                        }
            Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')

            invq_disk = utils._invq_disk_lmstar_estimate(z=z, lmstar=lmstar)

            fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

            Mstar =     np.power(10., lmstar)
            Mbaryon =   Mstar / (1.-fgas)
            Mgas = Mbaryon * fgas
            lMbar = np.log10(Mbaryon)

            bt =        utils._bt_lmstar_relation(z=z, lmstar=lmstar, galtype='sf')

            Mhalo =     utils._smhm_relation(z=z, lmstar=lmstar)
            Rvir = calcs.halo_rvir(Mvirial=Mhalo, z=z)
            lMhalo = np.log10(Mhalo)
            halo_conc = utils._halo_conc_relation(z=z, lmhalo=lMhalo)
            sigma0 =    utils._int_disp_z_evol_U19(z=z)

            val_dict['bt'] = bt
            val_dict['Reff_disk'] = Reff_disk
            val_dict['invq_disk'] = invq_disk
            val_dict['fgas'] = fgas
            val_dict['lMbar'] = lMbar
            val_dict['lMhalo'] = lMhalo
            val_dict['Rvir'] = Rvir
            val_dict['halo_conc'] = halo_conc
            val_dict['sigma0'] = sigma0

            ######
            # JUST USE LOOKUP
            nearest_n, nearest_invq = calcs.nearest_n_invq(n=n_disk, invq=invq_disk)
            vcirc_disk = calcs.interpolate_sersic_profile_VC_nearest(r=r_arr,
                            total_mass=((1.-bt)*Mbaryon),
                            Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)

            vcirc_bulge = (v_interp_bulge(r_arr / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))

            vcirc_halo = calcs.NFW_halo_vcirc(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z)
            vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
            vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)

            alphan = calcs.interpolate_sersic_profile_alpha_bulge_disk_nearest(r=r_arr,
                    BT=bt,  total_mass=Mgas,
                    Reff_disk=Reff_disk, n_disk=n_disk, invq_disk=invq_disk,
                    Reff_bulge=Reff_bulge,  n_bulge=n_bulge, invq_bulge=invq_bulge,
                    path=table_path)

            alpha_SG = 3.36 * (r_arr / Reff_disk)

            vrot_alphan = np.sqrt(vcirc_tot**2 - alphan*(sigma0**2))
            vrot_SG = np.sqrt(vcirc_tot**2 - alpha_SG*(sigma0**2))

            ####

            val_dict['invq_near'] = nearest_invq

            val_dict['vcirc_disk'] = vcirc_disk
            val_dict['vcirc_bulge'] = vcirc_bulge
            val_dict['vcirc_halo'] = vcirc_halo
            val_dict['vcirc_bar'] = vcirc_baryons
            val_dict['vcirc_tot'] = vcirc_tot

            val_dict['alphan'] = alphan
            val_dict['alpha_SG'] = alpha_SG

            val_dict['vrot_alphan'] = vrot_alphan
            val_dict['vrot_SG'] = vrot_SG


            ##
            dict_stack.append(val_dict)


    if save_dict_stack:
        if not (os.path.isfile(f_save)):
            with open(f_save, 'wb') as f:
                pickle.dump(dict_stack, f)

    ######################
    # FOR JUST THE fDM PLOTS!
    n_rows = 1

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            ax = axes[k]

            lw_comp = 0.5 # 1.
            lws = [lw_comp, lw_comp, lw_comp, lw_comp, lw_comp, 1.3]
            colors = ['tab:blue', 'tab:red', 'tab:green', 'tab:purple', 'orange', 'black']
            lss = ['-', '-', '-', '-', '-', '-']
            comps = ['disk', 'bulge', 'bar', 'halo', 'sigma0', 'tot']
            labels_components = [r'$v_{\mathrm{circ,disk}}$', r'$v_{\mathrm{circ,bulge}}$',
                                 r'$v_{\mathrm{circ,bar}}$', r'$v_{\mathrm{circ,halo}}$',
                                 r'$\sigma_0$', r'$v_{\mathrm{circ,tot}}$']

            plot_cnt_lmstar = 0
            for comp, ls, col, lw, lbl in zip(comps, lss, colors, lws, labels_components):
                if comp == 'sigma0':
                    keyy = comp
                    # Convert const to array
                    yarr = dict_stack[j][keyy] + 0. * dict_stack[j]['r_arr']
                else:
                    keyy = 'vcirc_{}'.format(comp)
                    yarr = dict_stack[j][keyy]
                ax.plot(dict_stack[j]['r_arr'], yarr,
                           ls=ls, color=col, lw=lw, label=lbl, zorder=-1.)
                plot_cnt_lmstar += 1

            plot_cnt_lmstar -= 1

            for mm, type in enumerate(types):
                    ax.plot(dict_stack[j]['r_arr'], dict_stack[j]['vrot_{}'.format(type)],
                       ls=ls_arr[mm],
                       color=color_arr[mm], lw=lw_arr[mm], label=labels[mm],
                       zorder=-1.)

            if show_sigmar_toy:
                Reff = dict_stack[j]['Reff_disk']
                sig0 = dict_stack[j]['sigma0']
                sigr =  _sigr_toy(dict_stack[j]['r_arr'], 2.*sig0, sig0, 0.5*Reff)
                alphasigr = _alpha_sigr_toy(dict_stack[j]['r_arr'], 2.*sig0, sig0, 0.5*Reff)
                alpha = dict_stack[j]['alphan']
                ax.plot(dict_stack[j]['r_arr'],
                    np.sqrt(dict_stack[j]['vcirc_tot']**2 -(alpha+alphasigr)*(sigr**2)),
                   ls='-.',  color='darkgrey', lw=1.,
                   label=r'$v_{\mathrm{rot}}$, $\alpha(n)+\alpha_{\sigma(r)}$',
                   zorder=-1.)


            ######################
            if ylim is None:        ylim = ax.get_ylim()

            ax.axvline(x=dict_stack[j]['Reff_disk'], ls=':', color='darkgrey', zorder=-20.)

            if ann_arr[j] is not None:
                xydelt = 0.04
                if ann_arr_pos[j] == 'lowerright':
                    xy = (1.-xydelt, xydelt)
                    va='bottom'
                    ha='right'
                elif ann_arr_pos[j] == 'upperright':
                    xy = (1.-xydelt, 1.-xydelt)
                    va='top'
                    ha='right'
                elif ann_arr_pos[j] == 'upperleft':
                    xy = (xydelt, 1.-xydelt)
                    va='top'
                    ha='left'
                ax.annotate(ann_arr[j], xy=xy,
                        va=va, ha=ha, fontsize=fontsize_ann_latex-2,
                        xycoords='axes fraction')

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            ########
            ax.xaxis.set_minor_locator(MultipleLocator(1.))
            ax.xaxis.set_major_locator(MultipleLocator(5.))

            ax.yaxis.set_minor_locator(MultipleLocator(20.))
            ax.yaxis.set_major_locator(MultipleLocator(100.))

            if xlabel is not None:
                ax.set_xlabel(xlabel, fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if (j == 0) & (ylabel is not None):
                ax.set_ylabel(ylabel, fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            ax.tick_params(labelsize=fontsize_ticks)

            if titles[j] is not None:
                ax.set_title(titles[j], fontsize=fontsize_title)

            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_lmstar)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_lmstar, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg + 1#fontsize_leg
                labelspacing=0.01 #0.15
                handletextpad=0.25
                loc = (0.02, 0.005)
                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc=loc,
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                legend1.set_zorder(-0.05)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    labelspacing=0.15
                    loc2= (0.55, 0.635)#'lower right' # 'lower left'
                    if show_sigmar_toy:
                        loc2 = 'upper right'
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc=loc2,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

    mpl.rcParams['text.usetex'] = False

    return None

def plot_toy_AD_corr_z(lmstar = None, z_arr=None,
            output_path=None, table_path=None, fileout=None,
            n_disk=1., Reff_bulge=1., n_bulge=4., invq_bulge=1.,
            save_dict_stack=True,
            overwrite_dict_stack=False):
    """
    Plot example correcting for asymmetric drift of different kinds.
    Take a vrot curve and predict the appropriate vcirc curves
    for the different AD corrections.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lmstar: float, optional
            Log of the total stellar mass [logMsun]. Default: 10.5 logMsun
        z_arr: array_like, optional
            Redshifts to show example. Default: [0.5, 1., 1.5, 2., 2.5]
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_toy_AD_corr_z'
        fileout += '.pdf'

    mpl.rcParams['text.usetex'] = False

    if lmstar is None:
        lmstar = 10.5

    if z_arr is None:
        z_step = 0.5
        zlims = [1., 3.] #[0.5, 2.5]
        z_arr = np.arange(zlims[0], zlims[1]+z_step, z_step)

    # Ensure it's an np array, not a list:
    z_arr = np.array(z_arr)

    rstep = 0.1 # kpc
    r_arr = np.arange(0., 20.+rstep, rstep)

    # ++++++++++++++++
    titles = []
    for z in z_arr:
        if (z %1 == 0):
            titles.append(r'$z={:0.0f}$'.format(z))
        else:
            titles.append(r'$z={:0.1f}$'.format(z))

    xlabel = r'$r$ [kpc]'
    ylabel = r'$v(r)$ [km/s]'
    xlim = [0., 20.]
    ylim = [0., 340.] #300.]

    types = ['alphan', 'SG']
    ls_arr = ['--', ':']
    color_arr = ['cyan', 'grey']
    lw_arr = [1.3, 1.3]
    labels = [r'$v_{\mathrm{rot}},\ \alpha(n)$', r'$v_{\mathrm{rot}},\ \alpha_{\mathrm{SG}}$']

    ann_arr = [ r'$\log_{10}(M_*/M_{\odot})'+r'={:0.1f}$'.format(lmstar), None, None, None, None]
    ann_arr_pos = ['upperright', None, None, None, None]

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.25 #3.75 #4.25
    n_cols = len(z_arr)
    n_rows = 1
    fac = 1.05 #1.15 #1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)


    wspace = 0.075 #0.1 #0.25 #0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')

    ######################
    dict_stack = None
    f_save = output_path+'toy_impl_AD_corr_z.pickle'
    if save_dict_stack:
        if (os.path.isfile(f_save)):
            with open(f_save, 'rb') as f:
                dict_stack = copy.deepcopy(pickle.load(f))

            if overwrite_dict_stack:
                raise ValueError("Really shouldn't do this!")
                os.remove(f_save)
                dict_stack = None

    if dict_stack is None:
        dict_stack = []
        for mm, z in enumerate(z_arr):
            print("z={}".format(z))
            val_dict = {'z':            z,
                        'r_arr':        r_arr,
                        'lmstar':       lmstar,
                        'bt':           -99.,
                        'Reff_disk':    -99.,
                        'invq_disk':    -99.,
                        'invq_near':    -99.,
                        'fgas':         -99.,
                        'lMbar':        -99.,
                        'lMhalo':       -99.,
                        'Rvir':         -99.,
                        'halo_conc':    -99.,
                        'sigma0':       -99.,

                        'vcirc_disk':   np.ones(len(r_arr)) * -99.,
                        'vcirc_bulge':  np.ones(len(r_arr)) * -99.,
                        'vcirc_halo':   np.ones(len(r_arr)) * -99.,
                        'vcirc_bar':    np.ones(len(r_arr)) * -99.,
                        'vcirc_tot':    np.ones(len(r_arr)) * -99.,

                        'alphan':       np.ones(len(r_arr)) * -99.,
                        'alpha_SG':     np.ones(len(r_arr)) * -99.,

                        'vrot_alphan':  np.ones(len(r_arr)) * -99.,
                        'vrot_SG':      np.ones(len(r_arr)) * -99.,

                        'vrot_obs':     np.ones(len(r_arr)) * -99.,
                        'vcirc_corr_alphan': np.ones(len(r_arr)) * -99.,
                        'vcirc_corr_SG':     np.ones(len(r_arr)) * -99.
                        }
            Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')

            invq_disk = utils._invq_disk_lmstar_estimate(z=z, lmstar=lmstar)

            fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

            Mstar =     np.power(10., lmstar)
            Mbaryon =   Mstar / (1.-fgas)
            Mgas = Mbaryon * fgas
            lMbar = np.log10(Mbaryon)

            bt =        utils._bt_lmstar_relation(z=z, lmstar=lmstar, galtype='sf')

            Mhalo =     utils._smhm_relation(z=z, lmstar=lmstar)
            Rvir = calcs.halo_rvir(Mvirial=Mhalo, z=z)
            lMhalo = np.log10(Mhalo)
            halo_conc = utils._halo_conc_relation(z=z, lmhalo=lMhalo)
            sigma0 =    utils._int_disp_z_evol_U19(z=z)

            val_dict['bt'] = bt
            val_dict['Reff_disk'] = Reff_disk
            val_dict['invq_disk'] = invq_disk
            val_dict['fgas'] = fgas
            val_dict['lMbar'] = lMbar
            val_dict['lMhalo'] = lMhalo
            val_dict['Rvir'] = Rvir
            val_dict['halo_conc'] = halo_conc
            val_dict['sigma0'] = sigma0

            ######
            # JUST USE LOOKUP
            nearest_n, nearest_invq = calcs.nearest_n_invq(n=n_disk, invq=invq_disk)
            vcirc_disk = calcs.interpolate_sersic_profile_VC_nearest(r=r_arr,
                            total_mass=((1.-bt)*Mbaryon),
                            Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)

            vcirc_bulge = (v_interp_bulge(r_arr / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))


            vcirc_halo = calcs.NFW_halo_vcirc(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z)
            vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
            vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)


            alphan = calcs.interpolate_sersic_profile_alpha_bulge_disk_nearest(r=r_arr,
                    BT=bt,  total_mass=Mgas,
                    Reff_disk=Reff_disk, n_disk=n_disk, invq_disk=invq_disk,
                    Reff_bulge=Reff_bulge,  n_bulge=n_bulge, invq_bulge=invq_bulge,
                    path=table_path)

            alpha_SG = 3.36 * (r_arr / Reff_disk)

            vrot_alphan = np.sqrt(vcirc_tot**2 - alphan*(sigma0**2))
            vrot_SG = np.sqrt(vcirc_tot**2 - alpha_SG*(sigma0**2))

            ####

            val_dict['invq_near'] = nearest_invq

            val_dict['vcirc_disk'] = vcirc_disk
            val_dict['vcirc_bulge'] = vcirc_bulge
            val_dict['vcirc_halo'] = vcirc_halo
            val_dict['vcirc_bar'] = vcirc_baryons
            val_dict['vcirc_tot'] = vcirc_tot

            val_dict['alphan'] = alphan
            val_dict['alpha_SG'] = alpha_SG

            val_dict['vrot_alphan'] = vrot_alphan
            val_dict['vrot_SG'] = vrot_SG

            val_dict['vrot_obs'] = vrot_alphan
            val_dict['vcirc_corr_alphan'] = np.sqrt(val_dict['vrot_obs']**2 + alphan*(sigma0**2))
            val_dict['vcirc_corr_SG'] = np.sqrt(val_dict['vrot_obs']**2 + alpha_SG*(sigma0**2))

            ##
            dict_stack.append(val_dict)

    if save_dict_stack:
        if not (os.path.isfile(f_save)):
            with open(f_save, 'wb') as f:
                pickle.dump(dict_stack, f)

    ######################
    # FOR JUST THE fDM PLOTS!
    n_rows = 1

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            ax = axes[k]

            lw_comp = 0.5 # 1.
            lws = [lw_comp, lw_comp, lw_comp, lw_comp, lw_comp, 1.3]
            colors = ['tab:blue', 'tab:red', 'tab:green', 'tab:purple', 'orange', 'black']
            lss = ['-', '-', '-', '-', '-', '-']
            comps = ['disk', 'bulge', 'bar', 'halo', 'sigma0', 'tot']
            labels_components = [r'$v_{\mathrm{circ,disk}}$', r'$v_{\mathrm{circ,bulge}}$',
                                 r'$v_{\mathrm{circ,bar}}$', r'$v_{\mathrm{circ,halo}}$',
                                 r'$\sigma_0$', r'$v_{\mathrm{circ,tot}}$']

            plot_cnt_lmstar = 0
            for comp, ls, col, lw, lbl in zip(comps, lss, colors, lws, labels_components):
                if comp == 'sigma0':
                    keyy = comp
                    # Convert const to array
                    yarr = dict_stack[j][keyy] + 0. * dict_stack[j]['r_arr']
                else:
                    keyy = 'vcirc_{}'.format(comp)
                    yarr = dict_stack[j][keyy]
                ax.plot(dict_stack[j]['r_arr'], yarr,
                           ls=ls, color=col, lw=lw, label=lbl, zorder=-1.)
                plot_cnt_lmstar += 1

            ax.plot(dict_stack[j]['r_arr'], dict_stack[j]['vrot_obs'],
               ls='-',color='magenta', lw=1.3, label=r'$v_{\mathrm{rot}}$', zorder=-1.)

            for mm, type in enumerate(types):
                    ax.plot(dict_stack[j]['r_arr'], dict_stack[j]['vcirc_corr_{}'.format(type)],
                       ls=ls_arr[mm],
                       color=color_arr[mm], lw=lw_arr[mm], label=labels[mm],
                       zorder=-1.)

            ######################
            if ylim is None:        ylim = ax.get_ylim()

            ax.axvline(x=dict_stack[j]['Reff_disk'], ls=':', color='darkgrey', zorder=-20.)

            if ann_arr[j] is not None:
                xydelt = 0.04
                if ann_arr_pos[j] == 'lowerright':
                    xy = (1.-xydelt, xydelt)
                    va='bottom'
                    ha='right'
                elif ann_arr_pos[j] == 'upperright':
                    xy = (1.-xydelt, 1.-xydelt)
                    va='top'
                    ha='right'
                elif ann_arr_pos[j] == 'upperleft':
                    xy = (xydelt, 1.-xydelt)
                    va='top'
                    ha='left'
                ax.annotate(ann_arr[j], xy=xy,
                        va=va, ha=ha, fontsize=fontsize_ann_latex-2,
                        xycoords='axes fraction')


            ax.set_xlim(xlim)
            ax.set_ylim(ylim)


            ########
            ax.xaxis.set_minor_locator(MultipleLocator(1.))
            ax.xaxis.set_major_locator(MultipleLocator(5.))

            ax.yaxis.set_minor_locator(MultipleLocator(20.))
            ax.yaxis.set_major_locator(MultipleLocator(100.))

            if xlabel is not None:
                ax.set_xlabel(xlabel, fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if (j == 0) & (ylabel is not None):
                ax.set_ylabel(ylabel, fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            ax.tick_params(labelsize=fontsize_ticks)

            if titles[j] is not None:
                ax.set_title(titles[j], fontsize=fontsize_title)

            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_lmstar)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_lmstar, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25
                loc = 'lower left'
                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc=loc,
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    loc2='lower right' # 'lower left'
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc=loc2,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

    mpl.rcParams['text.usetex'] = False

    return None


def plot_menc_frac_bulge_disk(fileout=None, output_path=None, table_path=None,
            z = 2., lmstar = 11.4365, n_disk = 1.,
            n_bulge = 4., invq_bulge=1., Reff_bulge=1.,
            q_arr=[0.1, 0.2, 0.4, 1., 1.5, 2.],
            bt_arr = [0., 0.25, 0.5, 0.75, 1.],
            save_dict_stack=False,
            overwrite_dict_stack=False):
    """
    Plot enclosed mass fractions predicted for different flattening q and B/T ratios.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lmstar: float, optional
            Log of the total stellar mass [logMsun]. Default: 10.5 logMsun
        z_arr: array_like, optional
            Redshifts to show example. Default: [0.5, 1., 1.5, 2., 2.5]
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)
        q_arr: array_like, optional
            Disk axis ratio array. Default: q_arr=[0.1, 0.2, 0.4, 1., 1.5, 2.].
        bt_arr: array_like, optional
            Bulge-to-total ratio array. Default: bt_arr = [0., 0.25, 0.5, 0.75, 1.].

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_menc_frac_bulge_disk'
        fileout += '_lmstar_{:0.1f}'.format(lmstar)
        fileout += '.pdf'


    mpl.rcParams['text.usetex'] = True

    # Ensure it's an np array, not a list:
    q_arr = np.array(q_arr)
    bt_arr = np.array(bt_arr)

    rstep = 0.1 # kpc
    r_range = [0., 3.] #[0., 5.] #[0., 10.] #[0., 20.]
    r_arr = np.arange(r_range[0], r_range[1]+rstep, rstep)


    # ++++++++++++++++
    titles = []
    for bt in bt_arr:
        if (bt % 1 == 0):
            titles.append(r'$B/T={:0.0f}$'.format(bt))
        else:
            titles.append(r'$B/T={}$'.format(bt))

    xlabel = r'$r/R_{e,\mathrm{disk}}$'
    ylabel = r'$M_{\mathrm{enc}}(<r)/M_{\mathrm{tot}}$'
    xlim = [r_arr.min(), r_arr.max()]
    ylim = [0., 1.]


    color_arr = []
    ls_arr = []
    labels = []
    for q in q_arr:
        if q <= 1.:
            color_arr.append(cmap_q(q))
            ls_arr.append('-')
        else:
            color_arr.append(cmapg(1./q))
            ls_arr.append('--')
        labels.append(r'$q_0={}$'.format(q))

    lw = 1.3

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 2.75 #3.25 #3.75 #4.25
    n_cols = len(bt_arr)
    n_rows = 1
    fac = 1.05 #1.15 #1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)

    wspace = 0.075 #0.1 #0.25 #0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')

    ######################

    dict_stack = None
    f_save = output_path+'menc_frac_bulge_disk.pickle'
    if save_dict_stack:
        if (os.path.isfile(f_save)):
            with open(f_save, 'rb') as f:
                dict_stack = copy.deepcopy(pickle.load(f))

            if overwrite_dict_stack:
                os.remove(f_save)
                dict_stack = None

    if dict_stack is None:
        dict_stack = []
        for jj, bt in enumerate(bt_arr):
            val_bt_dict = {}
            print("B/T={}".format(bt))
            for mm, q in enumerate(q_arr):
                print("   q0={}".format(q))
                val_dict = {'q':            q,
                            'z':            z,
                            'r_arr':        np.ones(len(r_arr)) * -99.,
                            'lmstar':       lmstar,
                            'bt':           bt,
                            'Reff_disk':    -99.,
                            'invq_disk':    -99.,
                            'invq_near':    -99.,
                            'fgas':         -99.,
                            'lMbar':        -99.,

                            'menc_disk':    np.ones(len(r_arr)) * -99.,
                            'menc_bulge':   np.ones(len(r_arr)) * -99.,
                            'menc_bar':     np.ones(len(r_arr)) * -99.,
                            'Mbar_tot':     -99.
                            }
                Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')

                invq_disk = 1./q

                fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

                Mstar =     np.power(10., lmstar)
                Mbaryon =   Mstar / (1.-fgas)
                Mgas = Mbaryon * fgas
                lMbar = np.log10(Mbaryon)

                val_dict['bt'] = bt
                val_dict['Reff_disk'] = Reff_disk
                val_dict['invq_disk'] = invq_disk
                val_dict['fgas'] = fgas
                val_dict['lMbar'] = lMbar
                val_dict['Mbar_tot'] = np.power(10., lMbar)

                val_dict['r_arr'] = r_arr.copy() * Reff_disk


                # JUST USE LOOKUP
                nearest_n, nearest_invq = calcs.nearest_n_invq(n=n_disk, invq=invq_disk)
                menc_disk = calcs.interpolate_sersic_profile_menc_nearest(r=val_dict['r_arr'],
                                total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                menc_bulge = (m_interp_bulge(val_dict['r_arr'] / Reff_bulge * tab_bulge_Reff) * ((bt*Mbaryon) / tab_bulge_mass) )

                menc_bar = menc_disk + menc_bulge

                ####
                val_dict['invq_near'] = nearest_invq

                val_dict['menc_disk'] = menc_disk
                val_dict['menc_bulge'] = menc_bulge
                val_dict['menc_bar'] = menc_bar

                val_bt_dict['q={}'.format(q)] = val_dict
                ##
            dict_stack.append(val_bt_dict)

    print("Re,disk={}".format(Reff_disk))

    if save_dict_stack:
        if not (os.path.isfile(f_save)):
            with open(f_save, 'wb') as f:
                pickle.dump(dict_stack, f)

    ######################
    # FOR JUST THE fDM PLOTS!
    n_rows = 1

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            ax = axes[k]

            bt = bt_arr[j]

            plot_cnt_lmstar = 0
            for mm, q in enumerate(q_arr):
                plot_cnt_lmstar += 1
                ax.plot(dict_stack[j]['q={}'.format(q)]['r_arr']/dict_stack[j]['q={}'.format(q)]['Reff_disk'],
                        dict_stack[j]['q={}'.format(q)]['menc_bar']/dict_stack[j]['q={}'.format(q)]['Mbar_tot'],
                           ls=ls_arr[mm], color=color_arr[mm], lw=lw, label=labels[mm], zorder=-1.)

            ######################
            if ylim is None:        ylim = ax.get_ylim()

            ax.axhline(y=0.5, ls=':', color='darkgrey', zorder=-20.)
            ax.axvline(x=1., ls=':', color='darkgrey', zorder=-20.)

            ax.axvline(x=Reff_bulge/dict_stack[j]['q={}'.format(q)]['Reff_disk'], ls='-.', color='darkgrey', zorder=-20.)
            ax.axvline(x=Reff_bulge/dict_stack[j]['q={}'.format(q)]['Reff_disk']*1.3, ls='--', color='darkgrey', zorder=-20.)

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            ########
            ax.xaxis.set_minor_locator(MultipleLocator(0.2))
            ax.xaxis.set_major_locator(MultipleLocator(1.))

            ax.yaxis.set_minor_locator(MultipleLocator(0.05))
            ax.yaxis.set_major_locator(MultipleLocator(0.2))

            if xlabel is not None:
                ax.set_xlabel(xlabel, fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if (j == 0) & (ylabel is not None):
                ax.set_ylabel(ylabel, fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            ax.tick_params(labelsize=fontsize_ticks)

            if titles[j] is not None:
                ax.set_title(titles[j], fontsize=fontsize_title)

            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_lmstar)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_lmstar, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg + 1#fontsize_leg
                labelspacing=0.01 #0.15
                handletextpad=0.25
                loc = 'lower right'
                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc=loc,
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                legend1.set_zorder(-0.05)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    labelspacing=0.15
                    loc2= (0.55, 0.635)#'lower right' # 'lower left'
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc=loc2,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

    mpl.rcParams['text.usetex'] = False

    return None


def plot_k3D_bulge_disk_halo(fileout=None, output_path=None, table_path=None,
            z = 2., lmstar = 11.4365, n_disk = 1.,
            n_bulge = 4., invq_bulge=1., Reff_bulge=1.,
            q_arr=[0.1, 0.2, 0.4, 1., 1.5, 2.],
            bt_arr = [0., 0.25, 0.5, 0.75, 1.],
            save_dict_stack=False,
            overwrite_dict_stack=False):
    """
    Plot 3D enclosed virial coefficient k3D for a composite disk+bulge system
    predicted for different flattening q and B/T ratios.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lmstar: float, optional
            Log of the total stellar mass [logMsun]. Default: 10.5 logMsun
        z_arr: array_like, optional
            Redshifts to show example. Default: [0.5, 1., 1.5, 2., 2.5]
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)
        q_arr: array_like, optional
            Disk axis ratio array. Default: q_arr=[0.1, 0.2, 0.4, 1., 1.5, 2.].
        bt_arr: array_like, optional
            Bulge-to-total ratio array. Default: bt_arr = [0., 0.25, 0.5, 0.75, 1.].

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_k3D_bulge_disk_halo'
        fileout += '_lmstar_{:0.1f}'.format(lmstar)
        fileout += '.pdf'


    mpl.rcParams['text.usetex'] = True

    # Ensure it's an np array, not a list:
    q_arr = np.array(q_arr)
    bt_arr = np.array(bt_arr)

    rstep = 0.1 # kpc
    r_range = [0., 3.] #[0., 5.] #[0., 10.] #[0., 20.]
    r_arr = np.arange(r_range[0], r_range[1]+rstep, rstep)

    # ++++++++++++++++
    titles = []
    for bt in bt_arr:
        if (bt % 1 == 0):
            titles.append(r'$B/T={:0.0f}$'.format(bt))
        else:
            titles.append(r'$B/T={}$'.format(bt))

    xlabel = r'$r/R_{e,\mathrm{disk}}$'
    ylabel = r'$k_{\mathrm{3D}}$'
    xlim = [r_arr.min(), r_arr.max()]
    ylim = [0.8, 1.3] #[0., 2.] #[0., 1.]


    color_arr = []
    ls_arr = []
    labels = []
    for q in q_arr:
        if q <= 1.:
            color_arr.append(cmap_q(q))
            ls_arr.append('-')
        else:
            color_arr.append(cmapg(1./q))
            ls_arr.append('--')
        labels.append(r'$q_0={}$'.format(q))

    lw = 1.3

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 2.75 #3.25 #3.75 #4.25
    n_cols = len(bt_arr)
    n_rows = 1
    fac = 1.05 #1.15 #1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)


    wspace = 0.075 #0.1 #0.25 #0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')


    ######################

    dict_stack = None
    f_save = output_path+'k3D_bulge_disk_halo.pickle'
    if save_dict_stack:
        if (os.path.isfile(f_save)):
            with open(f_save, 'rb') as f:
                dict_stack = copy.deepcopy(pickle.load(f))

            if overwrite_dict_stack:
                os.remove(f_save)
                dict_stack = None


    if dict_stack is None:
        dict_stack = []
        for jj, bt in enumerate(bt_arr):
            val_bt_dict = {}
            print("B/T={}".format(bt))
            for mm, q in enumerate(q_arr):
                print("   q0={}".format(q))
                val_dict = {'q':            q,
                            'z':            z,
                            'r_arr':        np.ones(len(r_arr)) * -99.,
                            'lmstar':       lmstar,
                            'bt':           bt,
                            'Reff_disk':    -99.,
                            'invq_disk':    -99.,
                            'invq_near':    -99.,
                            'fgas':         -99.,
                            'lMbar':        -99.,
                            'lMhalo':       -99.,
                            'Rvir':         -99.,
                            'halo_conc':    -99.,

                            'vcirc_disk':   np.ones(len(r_arr)) * -99.,
                            'vcirc_bulge':  np.ones(len(r_arr)) * -99.,
                            'vcirc_halo':   np.ones(len(r_arr)) * -99.,
                            'vcirc_bar':    np.ones(len(r_arr)) * -99.,
                            'vcirc_tot':    np.ones(len(r_arr)) * -99.,

                            'menc_disk':    np.ones(len(r_arr)) * -99.,
                            'menc_bulge':   np.ones(len(r_arr)) * -99.,
                            'menc_bar':     np.ones(len(r_arr)) * -99.,
                            'menc_halo':    np.ones(len(r_arr)) * -99.,
                            'menc_tot':     np.ones(len(r_arr)) * -99.,
                            'Mbar_tot':     -99.,
                            'k3d':          np.ones(len(r_arr)) * -99.
                            }
                Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')

                invq_disk = 1./q

                fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

                Mstar =     np.power(10., lmstar)
                Mbaryon =   Mstar / (1.-fgas)
                Mgas = Mbaryon * fgas
                lMbar = np.log10(Mbaryon)

                Mhalo =     utils._smhm_relation(z=z, lmstar=lmstar)
                Rvir = calcs.halo_rvir(Mvirial=Mhalo, z=z)
                lMhalo = np.log10(Mhalo)
                halo_conc = utils._halo_conc_relation(z=z, lmhalo=lMhalo)

                val_dict['bt'] = bt
                val_dict['Reff_disk'] = Reff_disk
                val_dict['invq_disk'] = invq_disk
                val_dict['fgas'] = fgas
                val_dict['lMbar'] = lMbar
                val_dict['Mbar_tot'] = np.power(10., lMbar)

                val_dict['lMhalo'] = lMhalo
                val_dict['Rvir'] = Rvir
                val_dict['halo_conc'] = halo_conc

                val_dict['r_arr'] = r_arr.copy() * Reff_disk

                # JUST USE LOOKUP
                nearest_n, nearest_invq = calcs.nearest_n_invq(n=n_disk, invq=invq_disk)
                menc_disk = calcs.interpolate_sersic_profile_menc_nearest(r=val_dict['r_arr'],
                                total_mass=((1.-bt)*Mbaryon),
                                Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                menc_bulge = (m_interp_bulge(val_dict['r_arr'] / Reff_bulge * tab_bulge_Reff) * ((bt*Mbaryon) / tab_bulge_mass) )
                menc_halo = calcs.NFW_halo_enclosed_mass(r=val_dict['r_arr'], Mvirial=Mhalo, conc=halo_conc, z=z)

                menc_bar = menc_disk + menc_bulge

                menc_tot = menc_bar + menc_halo

                vcirc_disk = calcs.interpolate_sersic_profile_VC(r=val_dict['r_arr'], total_mass=(1.-bt)*Mbaryon,
                                        Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                vcirc_bulge = (v_interp_bulge(val_dict['r_arr'] / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))
                vcirc_halo = calcs.NFW_halo_vcirc(r=val_dict['r_arr'], Mvirial=Mhalo, conc=halo_conc, z=z)
                vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
                vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)

                ####

                val_dict['invq_near'] = nearest_invq

                val_dict['menc_disk'] = menc_disk
                val_dict['menc_bulge'] = menc_bulge
                val_dict['menc_bar'] = menc_bar
                val_dict['menc_halo'] = menc_halo
                val_dict['menc_tot'] = menc_tot

                val_dict['vcirc_disk'] = vcirc_disk
                val_dict['vcirc_bulge'] = vcirc_bulge
                val_dict['vcirc_halo'] = vcirc_halo
                val_dict['vcirc_baryons'] = vcirc_baryons
                val_dict['vcirc_tot'] = vcirc_tot

                k3d = (menc_tot * Msun.cgs.value) * G.cgs.value / \
                                          (( val_dict['r_arr'] *1.e3*pc.cgs.value ) * \
                                           (vcirc_tot*1.e5)**2)
                val_dict['k3d'] = k3d

                val_bt_dict['q={}'.format(q)] = val_dict
                ##
            dict_stack.append(val_bt_dict)

    print("Re,disk={}".format(Reff_disk))

    if save_dict_stack:
        if not (os.path.isfile(f_save)):
            with open(f_save, 'wb') as f:
                pickle.dump(dict_stack, f)

    ######################
    # FOR JUST THE fDM PLOTS!
    n_rows = 1

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            ax = axes[k]

            bt = bt_arr[j]

            plot_cnt_lmstar = 0
            for mm, q in enumerate(q_arr):
                plot_cnt_lmstar += 1
                ax.plot(dict_stack[j]['q={}'.format(q)]['r_arr']/dict_stack[j]['q={}'.format(q)]['Reff_disk'],
                        dict_stack[j]['q={}'.format(q)]['k3d'],
                           ls=ls_arr[mm], color=color_arr[mm], lw=lw, label=labels[mm], zorder=-1.)

            ######################
            if ylim is None:        ylim = ax.get_ylim()

            ax.axvline(x=1., ls=':', color='darkgrey', zorder=-20.)
            ax.axvline(x=Reff_bulge/dict_stack[j]['q={}'.format(q)]['Reff_disk'], ls='-.', color='darkgrey', zorder=-20.)

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            ########
            ax.xaxis.set_minor_locator(MultipleLocator(0.2))
            ax.xaxis.set_major_locator(MultipleLocator(1.))

            ax.yaxis.set_minor_locator(MultipleLocator(0.05))
            ax.yaxis.set_major_locator(MultipleLocator(0.2))

            if xlabel is not None:
                ax.set_xlabel(xlabel, fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if (j == 0) & (ylabel is not None):
                ax.set_ylabel(ylabel, fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            ax.tick_params(labelsize=fontsize_ticks)

            if titles[j] is not None:
                ax.set_title(titles[j], fontsize=fontsize_title)

            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_lmstar)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_lmstar, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg + 1#fontsize_leg
                labelspacing=0.01 #0.15
                handletextpad=0.25
                loc = 'upper right'
                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc=loc,
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                legend1.set_zorder(-0.05)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    labelspacing=0.15
                    loc2= (0.55, 0.635)#'lower right' # 'lower left'
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc=loc2,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

    mpl.rcParams['text.usetex'] = False

    return None

def plot_k3D_vary_fdm(fileout=None, output_path=None, table_path=None,
            z = 2., lmstar = 10.5, n_disk = 1.,
            n_bulge = 4., invq_bulge=1., Reff_bulge=1.,
            fdm_arr = [0.001, 0.25, 0.5, 0.75, 0.999],
            save_dict_stack=False,
            overwrite_dict_stack=False):
    """
    Plot 3D enclosed virial coefficient k3D for a composite disk+bulge system,
    using typical values for a disk of lmstar=10.5, but varying fDM.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lmstar: float, optional
            Log of the total stellar mass [logMsun]. Default: 10.5 logMsun
        z: float, optional
            Redshift. Default: 2.
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)
        fdm_arr: array_like, optional
            Dark matter fraction array. Default :fdm_arr = [0.001, 0.25, 0.5, 0.75, 0.999].

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_k3D_vary_fdm'
        fileout += '_lmstar_{:0.1f}'.format(lmstar)
        fileout += '.pdf'


    mpl.rcParams['text.usetex'] = True

    rstep = 0.02 #0.1 # kpc
    r_range = [0., 3.] #[0., 5.] #[0., 10.] #[0., 20.]
    r_arr = np.arange(r_range[0], r_range[1]+rstep, rstep)

    fdm_arr = np.array(fdm_arr)
    # ++++++++++++++++

    xlabel = r'$r/R_{e,\mathrm{disk}}$'
    ylabel = r'$k_{\mathrm{3D}}$'
    xlim = [r_arr.min(), r_arr.max()]
    ylim = [0.8, 1.3] #[0., 2.] #[0., 1.]

    color_arr = []
    ls_arr = []
    labels = []
    fdmextra = 0.4
    fdmrange = 1.
    for fdm in fdm_arr:
        color_arr.append(cmap_fdm((fdm+fdmextra)/(fdmrange+fdmextra)))
        ls_arr.append('-')
        labels.append(r'$f_{\mathrm{DM}}(R_{e,\mathrm{disk}})'+r'={:0.2f}$'.format(fdm))

    lw = 1.3

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 4.25
    n_cols = 1 #len(bt_arr)
    n_rows = 1
    fac = 1.05 #1.05
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)

    wspace = 0.075 #0.1 #0.25 #0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))


    ######################
    # Load bulge: n, invq don't change.
    tab_bulge = table_io.read_profile_table(n=n_bulge, invq=invq_bulge, path=table_path)
    tab_bulge_menc =    tab_bulge['menc3D_sph']
    tab_bulge_vcirc =   tab_bulge['vcirc']
    tab_bulge_rad =     tab_bulge['r']
    tab_bulge_Reff =    tab_bulge['Reff']
    tab_bulge_mass =    tab_bulge['total_mass']

    # Clean up values inside rmin:  Add the value at r=0: menc=0
    if tab_bulge['r'][0] > 0.:
        tab_bulge_rad = np.append(0., tab_bulge_rad)
        tab_bulge_menc = np.append(0., tab_bulge_menc)
        tab_bulge_vcirc = np.append(0., tab_bulge_vcirc)

    m_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_menc, fill_value=np.NaN, bounds_error=False, kind='cubic')
    v_interp_bulge = scp_interp.interp1d(tab_bulge_rad, tab_bulge_vcirc, fill_value=np.NaN, bounds_error=False, kind='cubic')

    ######################

    dict_stack = None
    f_save = output_path+'k3D_vary_fdm.pickle'
    if save_dict_stack:
        if (os.path.isfile(f_save)):
            with open(f_save, 'rb') as f:
                dict_stack = copy.deepcopy(pickle.load(f))

            if overwrite_dict_stack:
                os.remove(f_save)
                dict_stack = None

    if dict_stack is None:
        dict_stack = []
        for jj, fdm in enumerate(fdm_arr):
            val_dict = {'q':            -99.,
                        'z':            z,
                        'r_arr':        np.ones(len(r_arr)) * -99.,
                        'lmstar':       lmstar,
                        'bt':           -99.,
                        'Reff_disk':    -99.,
                        'invq_disk':    -99.,
                        'invq_near':    -99.,
                        'fgas':         -99.,
                        'lMbar':        -99.,
                        'lMhalo':       -99.,
                        'Rvir':         -99.,
                        'halo_conc':    -99.,
                        'fdm':          fdm,

                        'vcirc_disk':   np.ones(len(r_arr)) * -99.,
                        'vcirc_bulge':  np.ones(len(r_arr)) * -99.,
                        'vcirc_halo':   np.ones(len(r_arr)) * -99.,
                        'vcirc_bar':    np.ones(len(r_arr)) * -99.,
                        'vcirc_tot':    np.ones(len(r_arr)) * -99.,

                        'menc_disk':    np.ones(len(r_arr)) * -99.,
                        'menc_bulge':   np.ones(len(r_arr)) * -99.,
                        'menc_bar':     np.ones(len(r_arr)) * -99.,
                        'menc_halo':    np.ones(len(r_arr)) * -99.,
                        'menc_tot':     np.ones(len(r_arr)) * -99.,
                        'Mbar_tot':     -99.,
                        'k3d':          np.ones(len(r_arr)) * -99.
                        }
            Reff_disk = utils._mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')

            invq_disk = utils._invq_disk_lmstar_estimate(z=z, lmstar=lmstar)
            q = 1./invq_disk

            bt =        utils._bt_lmstar_relation(z=z, lmstar=lmstar, galtype='sf')


            fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmstar)

            Mstar =     np.power(10., lmstar)
            Mbaryon =   Mstar / (1.-fgas)
            Mgas = Mbaryon * fgas
            lMbar = np.log10(Mbaryon)

            val_dict['q'] = q
            val_dict['bt'] = bt
            val_dict['Reff_disk'] = Reff_disk
            val_dict['invq_disk'] = invq_disk
            val_dict['fgas'] = fgas
            val_dict['lMbar'] = lMbar
            val_dict['Mbar_tot'] = np.power(10., lMbar)


            val_dict['r_arr'] = r_arr.copy() * Reff_disk


            # JUST USE LOOKUP
            nearest_n, nearest_invq = calcs.nearest_n_invq(n=n_disk, invq=invq_disk)
            menc_disk = calcs.interpolate_sersic_profile_menc_nearest(r=val_dict['r_arr'],
                            total_mass=((1.-bt)*Mbaryon),
                            Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
            menc_bulge = (m_interp_bulge(val_dict['r_arr'] / Reff_bulge * tab_bulge_Reff) * ((bt*Mbaryon) / tab_bulge_mass) )

            menc_bar = menc_disk + menc_bulge


            vcirc_disk = calcs.interpolate_sersic_profile_VC(r=val_dict['r_arr'], total_mass=(1.-bt)*Mbaryon,
                                    Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
            vcirc_bulge = (v_interp_bulge(val_dict['r_arr'] / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))
            vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)


            vcdiskre = calcs.interpolate_sersic_profile_VC(r=Reff_disk, total_mass=(1.-bt)*Mbaryon,
                                    Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
            vcbulgere = (v_interp_bulge(Reff_disk / Reff_bulge * tab_bulge_Reff) * np.sqrt((bt*Mbaryon) / tab_bulge_mass) * np.sqrt(tab_bulge_Reff / Reff_bulge))
            vcirc_baryons_reff = np.sqrt(vcdiskre**2 + vcbulgere**2)

            halo_conc = 4.
            Mhalo = utils._Mhalo_from_fDMv_NFW(vcirc_baryons=vcirc_baryons_reff, fDMv=fdm,
                            r=Reff_disk, conc=halo_conc, z=z)

            Rvir = calcs.halo_rvir(Mvirial=Mhalo, z=z)
            lMhalo = np.log10(Mhalo)

            menc_halo = calcs.NFW_halo_enclosed_mass(r=val_dict['r_arr'], Mvirial=Mhalo, conc=halo_conc, z=z)
            menc_tot = menc_bar + menc_halo

            vcirc_halo = calcs.NFW_halo_vcirc(r=val_dict['r_arr'], Mvirial=Mhalo, conc=halo_conc, z=z)
            vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
            ####

            val_dict['lMhalo'] = lMhalo
            val_dict['Rvir'] = Rvir
            val_dict['halo_conc'] = halo_conc

            val_dict['invq_near'] = nearest_invq

            val_dict['menc_disk'] = menc_disk
            val_dict['menc_bulge'] = menc_bulge
            val_dict['menc_bar'] = menc_bar
            val_dict['menc_halo'] = menc_halo
            val_dict['menc_tot'] = menc_tot

            val_dict['vcirc_disk'] = vcirc_disk
            val_dict['vcirc_bulge'] = vcirc_bulge
            val_dict['vcirc_halo'] = vcirc_halo
            val_dict['vcirc_baryons'] = vcirc_baryons
            val_dict['vcirc_tot'] = vcirc_tot

            k3d = (menc_tot * Msun.cgs.value) * G.cgs.value / \
                                      (( val_dict['r_arr'] *1.e3*pc.cgs.value ) * \
                                       (vcirc_tot*1.e5)**2)
            val_dict['k3d'] = k3d

            print("jj={}".format(jj))
            print("     fdm={}".format(fdm))
            print("     lMhalo={}".format(lMhalo))
            print("     vcirc_baryons_reff={}".format(vcirc_baryons_reff))

            dict_stack.append(val_dict)

    print("Re,disk={}".format(Reff_disk))

    if save_dict_stack:
        if not (os.path.isfile(f_save)):
            with open(f_save, 'wb') as f:
                pickle.dump(dict_stack, f)

    ######################
    # FOR JUST THE fDM PLOTS!
    n_rows = 1

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            ax = axes[k]

            plot_cnt_lmstar = 0
            for mm, fdm in enumerate(fdm_arr):
                plot_cnt_lmstar += 1
                ax.plot(dict_stack[mm]['r_arr']/dict_stack[mm]['Reff_disk'],
                        dict_stack[mm]['k3d'],
                           ls=ls_arr[mm], color=color_arr[mm], lw=lw, label=labels[mm], zorder=-1.)

            ######################
            if ylim is None:        ylim = ax.get_ylim()

            ax.axvline(x=1., ls=':', color='darkgrey', zorder=-20.)
            ax.axvline(x=Reff_bulge/dict_stack[j]['Reff_disk'], ls='-.', color='darkgrey', zorder=-20.)

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            ########
            ax.xaxis.set_minor_locator(MultipleLocator(0.2))
            ax.xaxis.set_major_locator(MultipleLocator(1.))

            ax.yaxis.set_minor_locator(MultipleLocator(0.05))
            ax.yaxis.set_major_locator(MultipleLocator(0.2))

            if xlabel is not None:
                ax.set_xlabel(xlabel, fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if (j == 0) & (ylabel is not None):
                ax.set_ylabel(ylabel, fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            ax.tick_params(labelsize=fontsize_ticks)

            if k == 0:
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(plot_cnt_lmstar)
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                neworder2 = range(plot_cnt_lmstar, len(handles))
                handles_arr2 = []
                labels_arr2 = []
                for ii in neworder2:
                    handles_arr2.append(handles[ii])
                    labels_arr2.append(labels_leg[ii])

                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg + 1#fontsize_leg
                labelspacing=0.01 #0.15
                handletextpad=0.25
                loc = 'upper right'
                legend1 = ax.legend(handles_arr, labels_arr,
                    labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                    loc=loc,
                    numpoints=1, scatterpoints=1,
                    frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                    fontsize=fontsize_leg_tmp)
                legend1.set_zorder(-0.05)
                ax.add_artist(legend1)
                if len(handles_arr2) > 0:
                    labelspacing=0.15
                    loc2= (0.55, 0.635)
                    legend2 = ax.legend(handles_arr2, labels_arr2,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc=loc2,
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend2)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


    mpl.rcParams['text.usetex'] = False

    return None

def plot_k3D_r_vir_coeff(fileout=None, output_path=None, table_path=None,
            q_arr=[0.2, 0.4, 0.6, 0.8, 1., 1.5, 2.],
            n_arr=[1.,4.]):
    """
    Plot the 3D virial coefficient as a function of radius, k3D(r),
    for a range of intrinsic axis ratios q and Sersic indices n.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        q_arr: array_like, optional
            Range of intrinsic axis ratios to plot.
            Default: q_arr = [0.2, 0.4, 0.6, 0.8, 1., 1.5, 2.]  (mostly oblate, 2 prolate)
        n_arr: array_like, optional
            Range of Sersic indices to plot.
            Default: n_arr = [1.,4.]

        fileout:str, optional
            Override the default filename and explicitly choose the output filename (must include full path).

    """
    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'k3D_r_vir_coeff_sersic_potential.pdf'


    ####################
    q_arr = np.array(q_arr)
    n_arr = np.array(n_arr)

    color_arr = []
    labels = []
    for q in q_arr:
        if q <= 1.:
            color_arr.append(cmap_q(q))
        else:
            color_arr.append(cmapg(1./q))
        labels.append(r'$q_0={}$'.format(q))

    ls_arr = []
    labels_n = []
    lw_arr = []
    for n in n_arr:
        if n == 1.:
            ls_arr.append('-')
            lw_arr.append(1.)
        elif n == 4.:
            ls_arr.append('--')
            lw_arr.append(0.5)
        labels_n.append(r'$n={:0.1f}$'.format(n))


    # Load files:
    try:
        # read fits tables, construct ks dict.....
        ks_dict = {}
        ks_dict['tot'] = {}
        ks_dict['3D'] = {}

        for n in n_arr:
            ks_dict['tot']['n={}'.format(n)] = {}
            ks_dict['3D']['n={}'.format(n)] = {}

            for q in q_arr:
                invq = 1./q

                try:
                    tab = table_io.read_profile_table(n=n, invq=invq, path=table_path)
                    if (q == 0.2) & (n == 1.):
                        ks_dict['Reff'] = tab['Reff']

                    if (q == 0.2):
                        ks_dict['tot']['n={}'.format(n)]['rarr'] = tab['r']
                        ks_dict['3D']['n={}'.format(n)]['rarr'] = tab['r']

                    ks_dict['tot']['n={}'.format(n)]['q={}'.format(q)]  = calcs.virial_coeff_tot(tab['r'], total_mass=tab['total_mass'],
                                               q=q, Reff=tab['Reff'], n=n, i=90., vc=tab['vcirc'])
                    ks_dict['3D']['n={}'.format(n)]['q={}'.format(q)]  = calcs.virial_coeff_3D(tab['r'], total_mass=tab['total_mass'],
                                               q=q, Reff=tab['Reff'], n=n, i=90., vc=tab['vcirc'], m3D=tab['menc3D_sph'])
                except:
                    ks_dict['tot']['n={}'.format(n)]['q={}'.format(q)] = np.ones(len(ks_dict['3D']['n={}'.format(n)]['rarr']))*np.NaN
                    ks_dict['3D']['n={}'.format(n)]['q={}'.format(q)] = np.ones(len(ks_dict['3D']['n={}'.format(n)]['rarr']))*np.NaN


    except:
        # REMOVE THIS AFTER FINISHING
        pass


    types = ['3D']
    xlabel = r'$r/R_e$'
    ylabels = [r'$k_{\mathrm{3D}}(r)$']
    xlim = [0., 10.]
    ylims = [[0.8,1.3]]

    titles = [r'Enclosed 3D virial coefficient' ]

    ann_arr = [ r'$k_{\mathrm{3D}}(r) = \frac{M_{\mathrm{encl,3D}}(<r) G }{v_c(r)^2 r}$' ]
    ann_arr_pos = ['lowerright']

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 4.25
    n_cols = len(types)
    f.set_size_inches(1.15*scale*n_cols,scale)

    pad_outer = 0.2

    gs = gridspec.GridSpec(1, n_cols, wspace=pad_outer)
    axes = []
    for i in range(n_cols):
        axes.append(plt.subplot(gs[0,i]))

    for i in range(n_cols):
        ax = axes[i]
        ylim = ylims[i]
        for k, n in enumerate(n_arr):
            for j, q in enumerate(q_arr):
                k_arr = ks_dict[types[i]]['n={}'.format(n)]['q={}'.format(q)]
                r_arr = ks_dict[types[i]]['n={}'.format(n)]['rarr']/ks_dict['Reff']
                if len(k_arr) != len(r_arr):
                    raise ValueError

                ls_tmp = ls_arr[k]

                col_tmp = color_arr[j]
                if k > 0:
                    hsv = mpl.colors.rgb_to_hsv(color_arr[j][:3])
                    print('q={}, hsv={}'.format(q, hsv))
                    col_tmp = mpl.colors.hsv_to_rgb((hsv[0], hsv[1]*0.5, min(hsv[2]*1.2, 1.)))

                if k == 0:
                    lbl_tmp = labels[j]
                else:
                    if (q == 1):
                        lbl_tmp = labels_n[k]
                    else:
                        lbl_tmp = None

                if (k==1) & (q==1):
                    ax.plot(r_arr, r_arr*np.NaN, ls=ls_arr[0], color='black', lw=lw_arr[0], label=labels_n[0], zorder=-k)

                ax.plot(r_arr, k_arr, ls=ls_tmp, color=col_tmp, lw=lw_arr[k], label=lbl_tmp, zorder=-k)


        ax.axvline(x=1., ls=':', color='lightgrey', zorder=-20.)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel(xlabel, fontsize=fontsize_labels)
        ax.set_ylabel(ylabels[i], fontsize=fontsize_labels)
        ax.tick_params(labelsize=fontsize_ticks)

        if titles[i] is not None:   ax.set_title(titles[i], fontsize=fontsize_title)

        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        ax.xaxis.set_major_locator(MultipleLocator(2.))

        xydelt = 0.04
        if ann_arr_pos[i] == 'lowerright':
            xy = (1.-xydelt, xydelt)
            va='bottom'
            ha='right'
        elif ann_arr_pos[i] == 'upperright':
            xy = (1.-xydelt, 1.-xydelt)
            va='top'
            ha='right'
        ax.annotate(ann_arr[i], xy=xy,
                va=va, ha=ha, fontsize=fontsize_ann,
                xycoords='axes fraction')

        if (ylim[1]-ylim[0]) > 3:
            ax.yaxis.set_minor_locator(MultipleLocator(0.2))
            ax.yaxis.set_major_locator(MultipleLocator(1.))
        else:
            ax.yaxis.set_minor_locator(MultipleLocator(0.02))
            ax.yaxis.set_major_locator(MultipleLocator(0.1))

        if i == 0 :
            frameon = False
            borderpad = 0.25
            fontsize_leg_tmp = fontsize_leg
            labelspacing=0.15
            handletextpad=0.25
            legend = ax.legend(labelspacing=labelspacing, borderpad=borderpad,
                handletextpad=handletextpad, loc='upper right', frameon=frameon,
                numpoints=1, scatterpoints=1,fontsize=fontsize_leg_tmp)


    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()



def plot_fDMratio_vs_r(output_path=None, table_path=None, fileout=None,
             z_arr=[2.], lMstar_arr=[9.0, 9.5, 10., 10.5, 11.],
             n_disk=1., invq_disk=5.,
             Reff_bulge=1., n_bulge=4., invq_bulge=1.,
             rmin = 0., rmax=15., rstep=0.01,
             log_rmin=-0.6, log_rmax=2.2, nlogr = 101,
             logradius=False):
    """
    Plot fDM ratio vs r, over a variety of stellar masses.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lMstar_arr: array_like, optional
            Array of log stellar masses to plot, in separate panels.
            Default: [9.0, 9.5, 10., 10.5, 11.]
        z_arr: array_like, optional
            Redshift (to determine NFW halo properties). Default: z=[2.]
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        invq_disk: float, optional
            Flattening of disk component. Default: invq_disk = 5.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc.
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)

        logradius: bool, optional
            Option whether to plot log radius or linear. Default: False (plot linear).
        rmin: float, optional
            Minimum radius, if doing linear radius.  Ignored if logradius=True. [kpc]
        rmax: float, optional
            Maximum radius, if doing linear radius.  Ignored if logradius=True. [kpc]
        rstep: float, optional
            Radius stepsize, if doing linear radius. Ignored if logradius=True. [kpc]
        log_rmin: float, optional
            Log of minimum radius, if doing log radius. Ignored if logradius=False. [log(kpc)]
        log_rmax: float, optional
            Log of maximum radius, if doing log radius. Ignored if logradius=False. [log(kpc)]
        nlogr: int, optional
            Number of log radius steps, if logradius=True. Ignored if logradius=False.

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """

    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_fdm_calibration_radius'
        if logradius:  fileout += '_logradius'
        fileout += '.pdf'

    if logradius:
        r_arr = np.logspace(log_rmin, log_rmax, num=nlogr)
        rarr_plot = np.log10(r_arr)
    else:
        r_arr = np.arange(rmin, rmax+rstep, rstep)
        rarr_plot = r_arr

    q_disk = 1./invq_disk

    lMstar_arr = np.array(lMstar_arr)
    z_arr = np.array(z_arr)

    # ++++++++++++++++
    # plot:
    types = ['NFW', 'TPH0.0']

    labels = []
    lw_arr = []
    color_arr = []
    for lmstar in lMstar_arr:
        print("lmstar=", lmstar)
        labels.append(r'$\log_{10}(M_*/M_{\odot})='+r'{:0.2f}$'.format(lmstar))
        lw_arr.append( ((lmstar-lMstar_arr.min())/(lMstar_arr.max()-lMstar_arr.min()) + 1.)*0.5 )
        color_arr.append(cmap_mass( (lmstar-lMstar_arr.min())/(lMstar_arr.max()-lMstar_arr.min()) ) )


    bt_arr=[0., 0.25, 0.5, 0.75]
    ls_arr_bt = ['-', '--', '-.', (0, (3, 1, 1, 1, 1, 1))]
    labels_bt = []
    for bt in bt_arr:
        labels_bt.append(r'$B/T={:0.2f}$'.format(bt))

    titles = []
    vline_loc = []
    vline_lss = []
    vline_labels = []
    xlims = []
    ylims = []
    xlabels = []
    ylabels = []

    ylims2 = []
    ylabels2 = []

    for i, typ in enumerate(types):
        for k, z in enumerate(z_arr):
            if i == 0:
                titles.append(r'$z={:0.1f}$'.format(z))
            else:
                titles.append(None)

            if k == 0:
                if typ == 'NFW':
                    ylabels.append(r'$f_{\mathrm{DM}}^v(r)/f_{\mathrm{DM}}^m(r)$, NFW')
                elif typ == 'TPH0.0':
                    ylabels.append(r'$f_{\mathrm{DM}}^v(r)/f_{\mathrm{DM}}^m(r)$, TPH, $\alpha=0$')
            else:
                ylabels.append(None)

            if typ == 'NFW':
                ylims.append([0.75, 1.75])
            elif typ == 'TPH0.0':
                ylims.append([0.65, 2.3])

            if i == len(types) - 1:
                if logradius:
                    xlabels.append(r'$\log_{10}(r/\mathrm{[kpc]})$')
                else:
                    xlabels.append(r'$r\ \mathrm{[kpc]}$')
            else:
                xlabels.append(None)
            if logradius:
                xlims.append([log_rmin, log_rmax])
            else:
                xlims.append([rmin, rmax+0.025*(rmax-rmin)])



    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.25
    n_cols = len(z_arr)
    n_rows = len(types)
    fac = 1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)

    wspace = 0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            z = z_arr[j]

            halo_typ = types[i]

            ax = axes[k]
            xlim = xlims[k]
            ylim = ylims[k]
            ylabel = ylabels[k]
            title = titles[k]

            for mm, lmstar in enumerate(lMstar_arr):
                for jj, bt in enumerate(bt_arr):

                    bt = bt_arr[jj]
                    Reff_disk = _mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')
                    fgas =      _fgas_scaling_relation_MS(z=z, lmstar=lmstar)
                    Mbaryon = np.power(10.,lmstar)/(1.-fgas)
                    Mhalo = _smhm_relation(z=z, lmstar=lmstar)
                    halo_conc = _halo_conc_relation(z=z, lmhalo=np.log10(Mhalo))


                    ###############
                    ## Get mass, velocity components:
                    menc_disk = calcs.interpolate_sersic_profile_menc(r=r_arr, total_mass=(1.-bt)*Mbaryon,
                                            Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                    menc_bulge = calcs.interpolate_sersic_profile_menc(r=r_arr, total_mass=(bt)*Mbaryon,
                                            Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
                    if halo_typ == 'NFW':
                        menc_halo = calcs.NFW_halo_enclosed_mass(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z)
                    elif halo_typ == 'TPH0.0':
                        menc_halo = calcs.TPH_halo_enclosed_mass(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)

                    menc_baryons = menc_disk + menc_bulge
                    menc_tot = menc_baryons + menc_halo
                    fdm_menc = menc_halo/menc_tot

                    #####
                    vcirc_disk = calcs.interpolate_sersic_profile_VC(r=r_arr, total_mass=(1.-bt)*Mbaryon,
                                            Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                    vcirc_bulge = calcs.interpolate_sersic_profile_VC(r=r_arr, total_mass=(bt)*Mbaryon,
                                            Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
                    if halo_typ == 'NFW':
                        vcirc_halo = calcs.NFW_halo_vcirc(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z)
                    elif halo_typ == 'TPH0.0':
                        vcirc_halo = calcs.TPH_halo_vcirc(r=r_arr, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)

                    vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
                    vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
                    fdm_vsq = vcirc_halo**2/vcirc_tot**2

                    fdm_comp = fdm_vsq / fdm_menc

                    if jj == 0:
                        lbl_tmp = labels[mm]
                    elif mm == (len(lMstar_arr)-1):
                        lbl_tmp = labels_bt[jj]
                    else:
                        lbl_tmp = None

                    ax.plot(rarr_plot, fdm_comp, ls=ls_arr_bt[jj], color=color_arr[mm],
                            lw=lw_arr[mm], label=lbl_tmp)

                    if (jj == 0) & (mm == (len(lMstar_arr)-1)):
                        lbl_tmp = labels_bt[jj]
                        ax.plot(rarr_plot*np.NaN, fdm_comp*np.NaN, ls=ls_arr_bt[jj], color=color_arr[mm],
                                lw=lw_arr[mm], label=lbl_tmp)

                    if jj == 0:
                        ax.scatter([Reff_disk], [(ylim[1]-ylim[0])*0.045 + ylim[0]], marker='|', color=color_arr[mm], s=25)

                        if (k == 0) & (mm == (len(lMstar_arr)-1)):
                            xdelt = (xlim[1]-xlim[0])*0.035
                            xypos = (Reff_disk + xdelt, (ylim[1]-ylim[0])*0.045 + ylim[0])
                            ax.annotate(r'$R_{e,\,\mathrm{disk}}$', xy=xypos, ha='left', va='center', color=color_arr[mm], fontsize=fontsize_ann)


            ax.axhline(y=1., ls=':', color='lightgrey', zorder=-20.)

            if ylim is None:  ylim = ax.get_ylim()

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            ########
            if logradius:
                ax.xaxis.set_minor_locator(MultipleLocator(0.1))
                if (j > 0) & (i == n_rows-1):
                    ax.xaxis.set_major_locator(FixedLocator([-2., -1., 0., 1., 2.]))
                    ax.xaxis.set_major_formatter(FixedFormatter(["", "-1", "0", "1", "2"]))
                else:
                    ax.xaxis.set_major_locator(MultipleLocator(1.))
            else:
                ax.xaxis.set_minor_locator(MultipleLocator(1.))
                if (j > 0) & (i == n_rows-1):
                    ax.xaxis.set_major_locator(FixedLocator([0., 5., 10., 15.]))
                    ax.xaxis.set_major_formatter(FixedFormatter(["", "5", "10", "15"]))
                else:
                    ax.xaxis.set_major_locator(MultipleLocator(5.))

            #
            if (k == 0):
                ax.yaxis.set_major_locator(MultipleLocator(0.2))
                ax.yaxis.set_minor_locator(MultipleLocator(0.05))
            else:
                ax.yaxis.set_major_locator(MultipleLocator(0.5))
                ax.yaxis.set_minor_locator(MultipleLocator(0.1))

            ax.tick_params(labelsize=fontsize_ticks)

            if xlabels[k] is not None:
                ax.set_xlabel(xlabels[k], fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if ylabels[k] is not None:
                ax.set_ylabel(ylabels[k], fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            if titles[k] is not None:
                ax.set_title(titles[k], fontsize=fontsize_title)

            if (k == 0) | ((i == n_rows -1) & (j == 0)) | ((i == 0) & (j == 1)):
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(len(handles))
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                ###############
                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25
                loc3 = 'lower right'
                if logradius:
                    loc2 = 'upper left'
                else:
                    loc2 = 'upper left'

                if (k == 0):
                    legend1 = ax.legend(handles_arr, labels_arr,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc='upper right',
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend1)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()


def plot_fDMratio_vs_fDMvReff(output_path=None, table_path=None, fileout=None,
             z_arr=[2.], lMstar_arr=[9.0, 9.5, 10., 10.5, 11.],
             n_disk=1., invq_disk=5.,
             Reff_bulge=1., n_bulge=4., invq_bulge=1.):
    """
    Plot DM ratio vs fDM_v(Reff), over a variety of stellar masses.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lMstar_arr: array_like, optional
            Array of log stellar masses to plot, in separate panels.
            Default: [9.0, 9.5, 10., 10.5, 11.]
        z_arr: array_like, optional
            Redshift (to determine NFW halo properties). Default: z=[2.]
        n_disk: float, optional
            Sersic index of disk component. Default: n_disk = 1.
        invq_disk: float, optional
            Flattening of disk component. Default: invq_disk = 5.
        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc.
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """

    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_fdm_calibration_fDMvReff'
        fileout += '.pdf'


    fDMstep = 0.1
    fDMvReff_arr = np.arange(0., 1.+fDMstep, fDMstep)

    q_disk = 1./invq_disk

    lMstar_arr = np.array(lMstar_arr)
    z_arr = np.array(z_arr)

    # ++++++++++++++++
    # plot:
    types = ['NFW', 'TPH']

    labels = []
    lw_arr = []
    color_arr = []
    for lmstar in lMstar_arr:
        print("lmstar=", lmstar)
        labels.append(r'$\log_{10}(M_*/M_{\odot})='+r'{:0.2f}$'.format(lmstar))
        lw_arr.append( ((lmstar-lMstar_arr.min())/(lMstar_arr.max()-lMstar_arr.min()) + 1.)*0.5 )
        color_arr.append(cmap_mass( (lmstar-lMstar_arr.min())/(lMstar_arr.max()-lMstar_arr.min()) ) )

    if len(lMstar_arr) == 1:
        lw_arr = [1.]
        color_arr = [cmap_mass(1.)]


    bt_arr=[0., 0.25, 0.5, 0.75]
    ls_arr_bt = ['-', '--', '-.', (0, (3, 1, 1, 1, 1, 1))]
    labels_bt = []
    for bt in bt_arr:
        labels_bt.append(r'$B/T={:0.2f}$'.format(bt))

    titles = []
    vline_loc = []
    vline_lss = []
    vline_labels = []
    xlims = []
    ylims = []
    xlabels = []
    ylabels = []

    ylims2 = []
    ylabels2 = []

    for i, typ in enumerate(types):
        for k, z in enumerate(z_arr):
            if i == 0:
                titles.append(r'$z={:0.1f}$'.format(z))
            else:
                titles.append(None)

            if k == 0:
                if typ == 'NFW':
                    ylabels.append(r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})/f_{\mathrm{DM}}^m(R_{e,\mathrm{disk}})$, NFW')
                elif typ == 'TPH0.0':
                    ylabels.append(r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})/f_{\mathrm{DM}}^m(R_{e,\mathrm{disk}})$, TPH, $\alpha=0$')
                elif typ == 'TPH':
                    ylabels.append(r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})/f_{\mathrm{DM}}^m(R_{e,\mathrm{disk}})$, TPH')
            else:
                ylabels.append(None)

            if typ == 'NFW':
                ylims.append([0.85, 1.1])
            elif typ == 'TPH0.0':
                ylims.append([0.85, 1.1])
            elif typ == 'TPH':
                ylims.append([0.85, 1.1])

            if i == len(types) - 1:
                xlabels.append(r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})$')
            else:
                xlabels.append(None)

            xlims.append([0.,1.])



    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 3.25
    n_cols = len(z_arr)
    n_rows = len(types)
    fac = 1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)

    wspace = 0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            axes.append(plt.subplot(gs[i,j]))

    for i in range(n_rows):
        for j in range(n_cols):
            k = i*n_cols + j

            z = z_arr[j]

            halo_typ = types[i]

            ax = axes[k]
            xlim = xlims[k]
            ylim = ylims[k]
            ylabel = ylabels[k]
            title = titles[k]

            for mm, lmstar in enumerate(lMstar_arr):
                for jj, bt in enumerate(bt_arr):

                    bt = bt_arr[jj]
                    Reff_disk = _mstar_Reff_relation(z=z, lmstar=lmstar, galtype='sf')
                    fgas =      _fgas_scaling_relation_MS(z=z, lmstar=lmstar)
                    Mbaryon = np.power(10.,lmstar)/(1.-fgas)


                    ###############
                    ## Get mass, velocity components:
                    menc_disk = calcs.interpolate_sersic_profile_menc(r=Reff_disk, total_mass=(1.-bt)*Mbaryon,
                                            Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                    menc_bulge = calcs.interpolate_sersic_profile_menc(r=Reff_disk, total_mass=(bt)*Mbaryon,
                                            Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
                    #
                    vcirc_disk = calcs.interpolate_sersic_profile_VC(r=Reff_disk, total_mass=(1.-bt)*Mbaryon,
                                            Reff=Reff_disk, n=n_disk, invq=invq_disk, path=table_path)
                    vcirc_bulge = calcs.interpolate_sersic_profile_VC(r=Reff_disk, total_mass=(bt)*Mbaryon,
                                            Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)

                    menc_baryons = menc_disk + menc_bulge
                    vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)
                    #####
                    fdm_comp_arr = np.ones(len(fDMvReff_arr)) * -99.
                    for ll, fDMvReff in enumerate(fDMvReff_arr):
                        Mhalo_SMHM = utils._smhm_relation(z=z, lmstar=lmstar)
                        halo_conc = utils._halo_conc_relation(z=z, lmhalo=np.log10(Mhalo_SMHM))
                        if fDMvReff == 0.:
                            Mhalo = 1.e2
                        elif fDMvReff == 1.:
                            Mhalo = 1.e18
                        else:
                            if halo_typ == 'NFW':
                                Mhalo = utils._Mhalo_from_fDMv_NFW(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff, r=Reff_disk, conc=halo_conc, z=z)
                            elif halo_typ == 'TPH0.0':
                                try:
                                    Mhalo = utils._Mhalo_from_fDMv_TPH(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff,
                                            r=Reff_disk, conc=halo_conc, z=z, alpha=0.)
                                except:
                                    Mhalo = np.NaN

                        #########
                        if halo_typ == 'TPH':
                            Mhalo = Mhalo_SMHM
                            if fDMvReff == 0.:
                                Mhalo = 1.e2
                                alphaTPH = 0.
                            elif fDMvReff == 1.:
                                Mhalo = 1.e18
                                alphaTPH = 1.
                            else:
                                alphaTPH = utils._alpha_from_fDMv_TPH(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff,
                                                r=Reff_disk, conc=halo_conc, z=z, Mhalo=Mhalo)

                        if np.isfinite(Mhalo):
                            if halo_typ == 'NFW':
                                menc_halo = calcs.NFW_halo_enclosed_mass(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                            elif halo_typ == 'TPH0.0':
                                menc_halo = calcs.TPH_halo_enclosed_mass(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)
                            elif halo_typ == 'TPH':
                                menc_halo = calcs.TPH_halo_enclosed_mass(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=alphaTPH)

                            menc_tot = menc_baryons + menc_halo
                            fdm_menc = menc_halo/menc_tot

                            #####

                            if halo_typ == 'NFW':
                                vcirc_halo = calcs.NFW_halo_vcirc(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                            elif halo_typ == 'TPH0.0':
                                vcirc_halo = calcs.TPH_halo_vcirc(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)
                            elif halo_typ == 'TPH':
                                vcirc_halo = calcs.TPH_halo_vcirc(r=Reff_disk, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=alphaTPH)

                            vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
                            fdm_vsq = vcirc_halo**2/vcirc_tot**2


                            fdm_comp_arr[ll] = fdm_vsq/fdm_menc

                        else:
                            fdm_comp_arr[ll] = np.NaN


                    if jj == 0:
                        lbl_tmp = labels[mm]
                    elif mm == (len(lMstar_arr)-1):
                        lbl_tmp = labels_bt[jj]
                    else:
                        lbl_tmp = None

                    ax.plot(fDMvReff_arr, fdm_comp_arr, ls=ls_arr_bt[jj], color=color_arr[mm],
                        lw=lw_arr[mm], label=lbl_tmp)

                    if (jj == 0) & (mm == (len(lMstar_arr)-1)):
                        lbl_tmp = labels_bt[jj]
                        ax.plot(fDMvReff_arr*np.NaN, fdm_comp_arr*np.NaN, ls=ls_arr_bt[jj], color=color_arr[mm],
                                lw=lw_arr[mm], label=lbl_tmp)

            ax.axhline(y=1., ls=':', color='lightgrey', zorder=-20.)

            if ylim is None:  ylim = ax.get_ylim()

            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            ########
            ax.xaxis.set_minor_locator(MultipleLocator(0.05))
            ax.xaxis.set_major_locator(MultipleLocator(0.25))
            if (j > 0) & (i == n_rows-1):
                ax.xaxis.set_major_locator(FixedLocator([0., 0.25, 0.5, 0.75, 1.0]))
                ax.xaxis.set_major_formatter(FixedFormatter(["", "0.25", "0.50", "0.75", "1.00"]))
            else:
                ax.xaxis.set_major_locator(MultipleLocator(0.25))

            if (k == 0):
                ax.yaxis.set_minor_locator(MultipleLocator(0.025))
                ax.yaxis.set_major_locator(MultipleLocator(0.1))
            else:
                ax.yaxis.set_minor_locator(MultipleLocator(0.025))
                ax.yaxis.set_major_locator(MultipleLocator(0.1))


            ax.tick_params(labelsize=fontsize_ticks)

            if xlabels[k] is not None:
                ax.set_xlabel(xlabels[k], fontsize=fontsize_labels)
            else:
                ax.set_xticklabels([])

            if ylabels[k] is not None:
                ax.set_ylabel(ylabels[k], fontsize=fontsize_labels)
            else:
                ax.set_yticklabels([])

            if titles[k] is not None:
                ax.set_title(titles[k], fontsize=fontsize_title)

            if (k == 0) | ((i == n_rows -1) & (j == 0)) | ((i == 0) & (j == 1)):
                handles, labels_leg = ax.get_legend_handles_labels()
                neworder = range(len(handles))
                handles_arr = []
                labels_arr = []
                for ii in neworder:
                    handles_arr.append(handles[ii])
                    labels_arr.append(labels_leg[ii])

                ###############
                frameon = True
                framealpha = 1.
                edgecolor = 'none'
                borderpad = 0.25
                fontsize_leg_tmp = fontsize_leg
                labelspacing=0.15
                handletextpad=0.25
                loc3 = 'lower right'
                loc2 = 'upper left'

                if (k == 0):
                    legend1 = ax.legend(handles_arr, labels_arr,
                        labelspacing=labelspacing, borderpad=borderpad, handletextpad=handletextpad,
                        loc= 'upper right',
                        numpoints=1, scatterpoints=1,
                        frameon=frameon, framealpha=framealpha, edgecolor=edgecolor,
                        fontsize=fontsize_leg_tmp)
                    ax.add_artist(legend1)

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

def plot_fDMratio_grid(output_path=None, table_path=None, fileout=None,
             fDMvReff_arr = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.],
             BT_arr = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.],
             Reff_disk_arr = [3., 5., 7., 10., 15.],
             invq_disk_arr=[1., 2., 3., 4., 5., 8.,10.],
             n_disk_arr=[0.5, 1., 1.5, 2.],
             Reff_bulge=1., n_bulge=4.,
             invq_bulge=1.,
             Mbaryon=np.power(10., 11.),
             halo_conc=4.,
             fDMvReff_0=0.2,
             BT_0 = 0.2,
             Reff_disk_0 = 5.,
             invq_disk_0 = 5.,
             n_disk_0 = 1.,
             z=2.,
             halo_typ = 'NFW',
             grid_fDM_ratio_stack = None,
             grid_fDM_ratio_pair=None):
    """
    Plot fDM ratio over a variety of fDM, B/T, Reff_disk, invq_disk, n_disk.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        fDMvReff_arr: array_like, optional
            fDMvReff array. Default: [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
        BT_arr: array_like, optional
            B/T ratio array. Default: [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
        Reff_disk_arr: array_like, optional
            Disk effective radius array [kpc]. Default: [3., 5., 7., 10., 15.] kpc
        invq_disk_arr: array_like, optional
            Flattening of disk component. Default: [1., 2., 3., 4., 5., 8.,10.]
        n_disk_arr: array_like, optional
            Sersic index of disk component. Default: [0.5, 1., 1.5, 2.]

        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc.
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)
        Mbaryon: float, optional
            Baryonic mass. Default: 1.e11 Msun
        z: float, optional
            Redshift (to determine NFW halo properties). Default: z=2.

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """

    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_fdm_ratio_grid'
        if halo_typ != 'NFW':
            fileout += '_{}'.format(halo_typ)
        fileout += '.pdf'

    # Ensure all are np arrays:
    fDMvReff_arr = np.array(fDMvReff_arr)
    BT_arr = np.array(BT_arr)
    Reff_disk_arr = np.array(Reff_disk_arr)
    invq_disk_arr = np.array(invq_disk_arr)
    n_disk_arr = np.array(n_disk_arr)

    q_disk_arr = 1./invq_disk_arr

    # ++++++++++++++++
    # plot:
    keys = [ 'fDMvReff', 'BT', 'Reff_disk', 'q_disk', 'n_disk' ]
    labels = [r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})$',
              r'$B/T$', r'$R_{e,\mathrm{disk}}$',
              r'$q_{0,\mathrm{disk}}$', r'$n_{\mathrm{disk}}$']

    cmap = cmap_im
    ecrect = 'gainsboro'

    arr_stack = [fDMvReff_arr,
                 BT_arr, Reff_disk_arr,
                 invq_disk_arr, n_disk_arr]

    lims = [ [0.0, 1.0], [0.0, 1.0], [1.0, 15.0], [0.0, 1.0], [0.5, 2.0] ]

    keyc = 'fDM_comp'
    label_c = r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})/f_{\mathrm{DM}}^m(R_{e,\mathrm{disk}})$'
    vmin_c = 0.885
    vmax_c = 1.0001

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 2.75
    n_cols = len(keys) - 1
    n_rows = len(keys) - 1
    fac = 1.02 #1.15
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)

    wspace = 0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            if (j <= i):
                axes.append(plt.subplot(gs[i,j]))
            else:
                if ((i == 0) & (j== 1)) | ((i == 2) & (j==3)) :
                    axes.append(plt.subplot(gs[i,j]))
                elif ((i == 0) & (j== 2)):
                    axes.append(plt.subplot(gs[i:i+2,j:j+2]))
                else:
                    axes.append(None)

    if grid_fDM_ratio_stack is None:
        stack_cnt = 0
        grid_fDM_ratio_pair = []

        for i in range(n_rows):
            keyy = keys[i+1]
            yarr = arr_stack[i+1]

            for j in range(n_cols):
                k = i*n_cols + j
                keyx = keys[j]
                xarr = arr_stack[j]

                if (j <= i):
                    grid_fDM_ratio = np.ones((len(yarr), len(xarr))) * np.NaN
                    for mm, y in enumerate(yarr):
                        for jj, x in enumerate(xarr):

                            fDMvReff_tmp = fDMvReff_0
                            BT_tmp = BT_0
                            Reff_disk_tmp = Reff_disk_0
                            invq_disk_tmp = invq_disk_0
                            n_disk_tmp = n_disk_0

                            ###
                            if keyx == 'fDMvReff':
                                fDMvReff_tmp = x
                            elif keyx == 'BT':
                                BT_tmp = x
                            elif keyx == 'Reff_disk':
                                Reff_disk_tmp = x
                            elif keyx == 'q_disk':
                                invq_disk_tmp = x
                            elif keyx == 'n_disk':
                                n_disk_tmp = x
                            ####
                            if keyy == 'fDMvReff':
                                fDMvReff_tmp = y
                            elif keyy == 'BT':
                                BT_tmp = y
                            elif keyy == 'Reff_disk':
                                Reff_disk_tmp = y
                            elif keyy == 'q_disk':
                                invq_disk_tmp = y
                            elif keyy == 'n_disk':
                                n_disk_tmp = y


                            ###############
                            ## Get mass, velocity components:
                            menc_disk = calcs.interpolate_sersic_profile_menc(r=Reff_disk_tmp, total_mass=(1.-BT_tmp)*Mbaryon,
                                                    Reff=Reff_disk_tmp, n=n_disk_tmp, invq=invq_disk_tmp, path=table_path)
                            menc_bulge = calcs.interpolate_sersic_profile_menc(r=Reff_disk_tmp, total_mass=(BT_tmp)*Mbaryon,
                                                    Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
                            #
                            vcirc_disk = calcs.interpolate_sersic_profile_VC(r=Reff_disk_tmp, total_mass=(1.-BT_tmp)*Mbaryon,
                                                    Reff=Reff_disk_tmp, n=n_disk_tmp, invq=invq_disk_tmp, path=table_path)
                            vcirc_bulge = calcs.interpolate_sersic_profile_VC(r=Reff_disk_tmp, total_mass=(BT_tmp)*Mbaryon,
                                                    Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)

                            menc_baryons = menc_disk + menc_bulge
                            vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)

                            # Get corresponding halo mass:
                            if fDMvReff_tmp == 0.:
                                Mhalo = 1.e2
                            elif fDMvReff_tmp == 1.:
                                Mhalo = 1.e18
                            else:
                                if halo_typ == 'NFW':
                                    Mhalo = _Mhalo_from_fDMv_NFW(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff_tmp,
                                                r=Reff_disk_tmp, conc=halo_conc, z=z)
                                elif halo_typ == 'TPH0.0':
                                    try:
                                        Mhalo = _Mhalo_from_fDMv_TPH(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff_tmp,
                                                r=Reff_disk_tmp, conc=halo_conc, z=z, alpha=0.)
                                    except:
                                        Mhalo = np.NaN

                            #########
                            if halo_typ == 'TPH':
                                lmstar = _solver_lmstar_fgas_mbar(z=z, Mbar=Mbaryon)
                                Mhalo_SMHM = _smhm_relation(z=z, lmstar=lmstar)
                                Mhalo = Mhalo_SMHM
                                if fDMvReff_tmp == 0.:
                                    Mhalo = 1.e2
                                    alphaTPH = 0.
                                elif fDMvReff_tmp == 1.:
                                    Mhalo = 1.e18
                                    alphaTPH = 1.
                                else:
                                    alphaTPH = _alpha_from_fDMv_TPH(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff_tmp,
                                                    r=Reff_disk_tmp, conc=halo_conc, z=z, Mhalo=Mhalo)

                            #########
                            if np.isfinite(Mhalo):
                                if halo_typ == 'NFW':
                                    menc_halo = calcs.NFW_halo_enclosed_mass(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z)
                                elif halo_typ == 'TPH0.0':
                                    menc_halo = calcs.TPH_halo_enclosed_mass(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)
                                elif halo_typ == 'TPH':
                                    menc_halo = calcs.TPH_halo_enclosed_mass(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=alphaTPH)

                                menc_tot = menc_baryons + menc_halo
                                fdm_menc = menc_halo/menc_tot

                                ####
                                if halo_typ == 'NFW':
                                    vcirc_halo = calcs.NFW_halo_vcirc(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z)
                                elif halo_typ == 'TPH0.0':
                                    vcirc_halo = calcs.TPH_halo_vcirc(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)
                                elif halo_typ == 'TPH':
                                    vcirc_halo = calcs.TPH_halo_vcirc(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=alphaTPH)

                                vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)
                                fdm_vsq = vcirc_halo**2/vcirc_tot**2


                                grid_fDM_ratio[mm, jj] = fdm_vsq/fdm_menc

                            else:
                                grid_fDM_ratio[mm, jj] = np.NaN
                    #
                    if grid_fDM_ratio_stack is None:
                        grid_fDM_ratio_stack = []
                    grid_fDM_ratio_stack.append(grid_fDM_ratio)
                    grid_fDM_ratio_pair.append('{}-{}'.format(keyx, keyy))

    stack_cnt = 0
    for i in range(n_rows):
        keyy = keys[i+1]
        ylim = lims[i+1]
        ylabel = labels[i+1]

        for j in range(n_cols):
            k = i*n_cols + j
            ax = axes[k]
            keyx = keys[j]
            xlim = lims[j]

            xarr = arr_stack[j]
            # Reset each time
            yarr = arr_stack[i+1]

            if (i == n_rows-1):
                xlabel = labels[j]
            else:
                xlabel = None

            if j > 0:
                ylabel = None

            if (j > i):
                if (i == 0) & (j == 2):
                    # COLORBAR
                    cax, kw = colorbar.make_axes_gridspec(ax, pad=0.01,
                            fraction=5./101., aspect=20.)
                    cbar = plt.colorbar(im_fDM_grid, cax=cax, extend='both', **kw)
                    cbar.ax.tick_params(labelsize=fontsize_ticks_sm)
                    cbar.set_label(label_c, fontsize=fontsize_labels_sm)
                    ax.tick_params(labelbottom='off', labelleft='off')
                    for sp in ['top', 'bottom', 'left', 'right']: ax.spines[sp].set_visible(False)
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])

                    ############
                    bbox_props = dict(boxstyle="square", fc="None", ec=ecrect, lw=1)
                    ann_str = r'$\mathbf{Fiducial:}$'
                    ax.annotate(ann_str, xy=(0.1, 0.75),
                                xycoords='axes fraction', va='top',
                                ha='left', fontsize=fontsize_labels_sm,
                                bbox=bbox_props)
                    ann_str = r'$z={:0.1f}$'.format(z)
                    ann_str += '\n'
                    ann_str += r'{} halo'.format(halo_typ)
                    ann_str += '\n'
                    ann_str += r'$\mathrm{conc}_{\mathrm{halo}}='+r'{:0.1f}$'.format(halo_conc)
                    ann_str += '\n'
                    ann_str += r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})='+r'{:0.1f}$'.format(fDMvReff_0)

                    ax.annotate(ann_str, xy=(0.1, 0.5),
                                xycoords='axes fraction', va='center',
                                ha='left', fontsize=fontsize_ann_lg)

                    ann_str = r'$\log_{10}(M_{\mathrm{bar}}/M_{\odot})'+r'={:0.1f}$'.format(np.log10(Mbaryon))
                    ann_str += '\n'
                    ann_str += r'$B/T={:0.2f}$'.format(BT_0)
                    ann_str += '\n'
                    ann_str += r'$R_{e,\mathrm{disk}}'+r'={:0.1f}$'.format(Reff_disk_0)
                    ann_str += '\n'
                    ann_str += r'$q_{0,\mathrm{disk}}'+r'={:0.2f}$'.format(1./invq_disk_0)
                    ann_str += '\n'
                    ann_str += r'$n_{\mathrm{disk}}'+r'={:0.1f}$'.format(n_disk_0)
                    ann_str += '\n'
                    ###
                    ann_str += r'$R_{e,\mathrm{bulge}}'+r'={:0.1f}$'.format(Reff_bulge)
                    ann_str += '\n'
                    ann_str += r'$q_{0,\mathrm{bulge}}'+r'={:0.2f}$'.format(1./invq_bulge)
                    ann_str += '\n'
                    ann_str += r'$n_{\mathrm{bulge}}'+r'={:0.1f}$'.format(n_bulge)

                    ax.annotate(ann_str, xy=(0.5, 0.5),
                                xycoords='axes fraction', va='center',
                                ha='left', fontsize=fontsize_ann_lg)

                else:
                    if ax is not None:
                        ax.axis('off')
            else:
                # Get fiducial values:
                if keyx == 'fDMvReff':
                    xfid = fDMvReff_0
                elif keyx == 'BT':
                    xfid = BT_0
                elif keyx == 'Reff_disk':
                    xfid = Reff_disk_0
                elif keyx == 'q_disk':
                    xfid = 1./invq_disk_0
                elif keyx == 'n_disk':
                    xfid = x
                ####
                if keyy == 'fDMvReff':
                    yfid = fDMvReff_0
                elif keyy == 'BT':
                    yfid = BT_0
                elif keyy == 'Reff_disk':
                    yfid = Reff_disk_0
                elif keyy == 'q_disk':
                    yfid = 1./invq_disk_0
                elif keyy == 'n_disk':
                    yfid = n_disk_0

                ####
                grid_fDM_ratio = grid_fDM_ratio_stack[stack_cnt]
                grid_fDM_names = grid_fDM_ratio_pair[stack_cnt]
                stack_cnt_cur = stack_cnt
                stack_cnt += 1

                ####
                if keyx == 'q_disk':
                    xarr = 1./xarr
                if keyy == 'q_disk':
                    yarr = 1./yarr

                ###
                # ADAPTIVE GRID SIZE BASED ON X,Y SAMPLING:
                xarr_edges = np.ones(len(xarr)+1)
                xarr_edges[1:-1] = 0.5*(xarr[1:] + xarr[:-1])
                xarr_edges[0] = xarr[0] - (xarr_edges[1] - xarr[0])
                xarr_edges[-1] = xarr[-1] + (xarr[-1] - xarr_edges[-2])

                yarr_edges = np.ones(len(yarr)+1)
                yarr_edges[1:-1] = 0.5*(yarr[1:] + yarr[:-1])
                yarr_edges[0] = yarr[0] - (yarr_edges[1] - yarr[0])
                yarr_edges[-1] = yarr[-1] + (yarr[-1] - yarr_edges[-2])

                ###
                # EQUAL PIXEL SPACING:
                xarr_edges = np.arange(len(xarr)+1)
                yarr_edges = np.arange(len(yarr)+1)
                if keyx == 'q_disk':
                    xarr_edges = xarr_edges[::-1]
                if keyy == 'q_disk':
                    yarr_edges = yarr_edges[::-1]

                im_fDM_grid = ax.pcolormesh(xarr_edges, yarr_edges, grid_fDM_ratio, cmap=cmap, vmin=vmin_c, vmax=vmax_c)

                whmx = np.where(xarr == xfid)[0]
                whmy = np.where(yarr == yfid)[0]
                if (len(whmx)==1) & (len(whmy)==1):
                    rect = Rectangle((xarr_edges[whmx[0]], yarr_edges[whmy[0]]),
                                xarr_edges[whmx[0]+1]-xarr_edges[whmx[0]],
                                yarr_edges[whmy[0]+1]-yarr_edges[whmy[0]],
                                angle=0., lw=1., edgecolor=ecrect, facecolor='None')
                    ax.add_patch(rect)

                ####
                ax.xaxis.set_major_locator(FixedLocator(0.5*(xarr_edges[1:] + xarr_edges[:-1])))
                ax.yaxis.set_major_locator(FixedLocator(0.5*(yarr_edges[1:] + yarr_edges[:-1])))

                xarr_formatter = ["{}".format(x) for x in xarr]
                yarr_formatter = ["{}".format(y) for y in yarr]
                xarr_formatter = np.array(xarr_formatter)
                yarr_formatter = np.array(yarr_formatter)
                if keyx == 'q_disk':
                    whm = np.where(1./xarr == 3.)[0]
                    xarr_formatter[whm] = "0.33"
                if keyy == 'q_disk':
                    whm = np.where(1./yarr == 3.)[0]
                    yarr_formatter[whm] = "0.33"

                if (keyx == "BT") | (keyx == "fDMvReff"):
                    xarr_tmp = np.copy(xarr)
                    xarr_tmp[1::2] = -99.
                    xarr_formatter[xarr_tmp==-99.] = ""
                #
                if (keyy == "BT") | (keyy == "fDMvReff"):
                    yarr_tmp = np.copy(yarr)
                    yarr_tmp[1::2] = -99.
                    yarr_formatter[yarr_tmp==-99.] = ""

                ax.xaxis.set_major_formatter(FixedFormatter(xarr_formatter.tolist()))
                ax.yaxis.set_major_formatter(FixedFormatter(yarr_formatter.tolist()))

                ax.tick_params(labelsize=fontsize_ticks)

                if xlabels[k] is not None:
                    ax.set_xlabel(xlabels[k], fontsize=fontsize_labels)
                else:
                    ax.set_xticklabels([])

                if ylabels[k] is not None:
                    ax.set_ylabel(ylabels[k], fontsize=fontsize_labels)
                else:
                    ax.set_yticklabels([])

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

    return grid_fDM_ratio_stack, grid_fDM_ratio_pair


def plot_ktot_inf_grid(output_path=None, table_path=None, fileout=None,
             lmass_arr = [9., 9.5, 10., 10.5, 11., 11.5],
             fDMvReff_arr = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.],
             BT_arr = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.],
             Reff_disk_arr = [2., 3.5, 5., 7., 10.], invq_disk_arr=[1., 2., 3., 4., 5., 8.,10.],
             n_disk_arr=[0.5, 1., 1.5, 2.],
             Reff_bulge=1., n_bulge=4.,
             invq_bulge=1.,
             halo_conc=4.,
             lmass_0 = 10.5,
             fDMvReff_0=0.2,
             BT_0 = 0.0,
             Reff_disk_0 = 3.5,
             invq_disk_0 = 5.,
             n_disk_0 = 1.,
             z=2.,
             halo_typ = 'NFW',
             grid_fDM_ratio_stack = None,
             grid_fDM_ratio_pair=None):
    """
    Plot virial coeffiecient ktot over a variety of lmstar, fDM, B/T,
    Reff_disk, invq_disk, n_disk.

    Saves plot to PDF.

    Parameters
    ----------
        output_path: str
            Path to directory where the output plot will be saved.
        table_path: str
            Path to directory containing the Sersic profile tables.

        lmass_arr: array_like, optional
            Log stellar mass array. Default: [9., 9.5, 10., 10.5, 11., 11.5] logMsun
        fDMvReff_arr: array_like, optional
            fDMvReff array. Default: [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
        BT_arr: array_like, optional
            B/T ratio array. Default: [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
        Reff_disk_arr: array_like, optional
            Disk effective radius array [kpc]. Default: [3., 5., 7., 10., 15.] kpc
        invq_disk_arr: array_like, optional
            Flattening of disk component. Default: [1., 2., 3., 4., 5., 8.,10.]
        n_disk_arr: array_like, optional
            Sersic index of disk component. Default: [0.5, 1., 1.5, 2.]

        Reff_bulge: float, optional
            Sersic projected 2D half-light (assumed half-mass) radius of bulge component [kpc].
            Default: 1kpc.
        n_bulge: float, optional
            Sersic index of bulge component. Default: n_bulge = 4.
        invq_bulge: float, optional
            Flattening of bulge component. Default: invq_bulge = 1. (spherical)
        Mbaryon: float, optional
            Baryonic mass. Default: 1.e11 Msun
        z: float, optional
            Redshift (to determine NFW halo properties). Default: z=2.

        fileout: str, optional
            Override the default filename and explicitly choose the output filename
            (must include full path).

    """

    if (output_path is None) & (fileout is None):     raise ValueError("Must set 'output_path' if 'fileout' is not set !")
    if table_path is None:      raise ValueError("Must set 'table_path' !")

    if (fileout is None):
        # Ensure trailing slash:
        if output_path[-1] != '/':  output_path += '/'
        fileout = output_path+'plot_ktot_inf_grid'
        if halo_typ != 'NFW':
            fileout += '_{}'.format(halo_typ)
        fileout += '.pdf'

    # Ensure all are np arrays:
    lmass_arr = np.array(lmass_arr)
    fDMvReff_arr = np.array(fDMvReff_arr)
    BT_arr = np.array(BT_arr)
    Reff_disk_arr = np.array(Reff_disk_arr)
    invq_disk_arr = np.array(invq_disk_arr)
    n_disk_arr = np.array(n_disk_arr)

    q_disk_arr = 1./invq_disk_arr

    # ++++++++++++++++
    # plot:
    keys = [ 'lmass', 'fDMvReff', 'BT', 'Reff_disk', 'q_disk', 'n_disk' ]
    labels = [r'$\log_{10}(M_*/M_{\odot})$',
              r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})$',
              r'$B/T$', r'$R_{e,\mathrm{disk}}$',
              r'$q_{0,\mathrm{disk}}$', r'$n_{\mathrm{disk}}$']

    cmap = cmap_im2
    ecrect = 'gainsboro'

    arr_stack = [lmass_arr, fDMvReff_arr,
                 BT_arr, Reff_disk_arr,
                 invq_disk_arr, n_disk_arr]

    lims = [ [9., 11.5], [0.0, 1.0], [0.0, 1.0], [1.0, 15.0], [0.0, 1.0], [0.5, 2.0] ]

    keyc = 'fDM_comp'
    label_c = r'$k_{\mathrm{tot,\, estimated}}(R_{e,\mathrm{disk}})$'
    vmin_c = 1.9
    vmax_c = 2.5

    ######################################
    # Setup plot:
    f = plt.figure()
    scale = 2.75
    n_cols = len(keys) - 1
    n_rows = len(keys) - 1
    fac = 1.02
    f.set_size_inches(fac*scale*n_cols,scale*n_rows)

    wspace = 0.025
    hspace = wspace
    gs = gridspec.GridSpec(n_rows, n_cols, wspace=wspace, hspace=hspace)
    axes = []
    for i in range(n_rows):
        for j in range(n_cols):
            if (j <= i):
                axes.append(plt.subplot(gs[i,j]))
            else:
                if ((i == 0) & (j== 1)) | ((i == 2) & (j==3)) :
                    axes.append(plt.subplot(gs[i,j]))
                elif ((i == 0) & (j== 2)):
                    axes.append(plt.subplot(gs[i:i+2,j:j+2]))
                else:
                    axes.append(None)

    if grid_fDM_ratio_stack is None:
        stack_cnt = 0
        grid_fDM_ratio_pair = []

        for i in range(n_rows):
            keyy = keys[i+1]
            yarr = arr_stack[i+1]

            for j in range(n_cols):
                k = i*n_cols + j
                keyx = keys[j]

                xarr = arr_stack[j]

                if (j <= i):
                    grid_fDM_ratio = np.ones((len(yarr), len(xarr))) * np.NaN
                    for mm, y in enumerate(yarr):
                        for jj, x in enumerate(xarr):
                            fDMvReff_tmp = fDMvReff_0
                            BT_tmp = BT_0
                            Reff_disk_tmp = Reff_disk_0
                            invq_disk_tmp = invq_disk_0
                            n_disk_tmp = n_disk_0
                            lmass_tmp = lmass_0

                            #####
                            if keyx == 'lmass':
                                lmass_tmp = x
                            elif keyx == 'fDMvReff':
                                fDMvReff_tmp = x
                            elif keyx == 'BT':
                                BT_tmp = x
                            elif keyx == 'Reff_disk':
                                Reff_disk_tmp = x
                            elif keyx == 'q_disk':
                                invq_disk_tmp = x
                            elif keyx == 'n_disk':
                                n_disk_tmp = x
                            ####
                            if keyy == 'lmass':
                                lmass_tmp = y
                            elif keyy == 'fDMvReff':
                                fDMvReff_tmp = y
                            elif keyy == 'BT':
                                BT_tmp = y
                            elif keyy == 'Reff_disk':
                                Reff_disk_tmp = y
                            elif keyy == 'q_disk':
                                invq_disk_tmp = y
                            elif keyy == 'n_disk':
                                n_disk_tmp = y

                            # Get Mbaryon:
                            fgas =      utils._fgas_scaling_relation_MS(z=z, lmstar=lmass_tmp)
                            Mbaryon =   np.power(10.,lmass_tmp)/(1.-fgas)

                            ###############
                            ## Get mass, velocity components:
                            # Get rhalf disk:
                            tab = table_io.read_profile_table(n=n_disk_tmp, invq=invq_disk_tmp,  path=table_path)
                            rhalf_disk = tab['rhalf3D_sph'] * (Reff_disk_tmp / tab['Reff'])
                            tab = None

                            menc_disk = calcs.interpolate_sersic_profile_menc(r=rhalf_disk, total_mass=(1.-BT_tmp)*Mbaryon,
                                                    Reff=Reff_disk_tmp, n=n_disk_tmp, invq=invq_disk_tmp, path=table_path)
                            menc_bulge = calcs.interpolate_sersic_profile_menc(r=rhalf_disk, total_mass=(BT_tmp)*Mbaryon,
                                                    Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)
                            #
                            vcirc_disk = calcs.interpolate_sersic_profile_VC(r=Reff_disk_tmp, total_mass=(1.-BT_tmp)*Mbaryon,
                                                    Reff=Reff_disk_tmp, n=n_disk_tmp, invq=invq_disk_tmp, path=table_path)
                            vcirc_bulge = calcs.interpolate_sersic_profile_VC(r=Reff_disk_tmp, total_mass=(BT_tmp)*Mbaryon,
                                                    Reff=Reff_bulge, n=n_bulge, invq=invq_bulge, path=table_path)

                            menc_baryons = menc_disk + menc_bulge
                            vcirc_baryons = np.sqrt(vcirc_disk**2 + vcirc_bulge**2)

                            # Get corresponding halo mass:
                            if fDMvReff_tmp == 0.:
                                Mhalo = 1.e2
                            elif fDMvReff_tmp == 1.:
                                Mhalo = 1.e18
                            else:
                                if halo_typ == 'NFW':
                                    Mhalo = utils._Mhalo_from_fDMv_NFW(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff_tmp,
                                                r=Reff_disk_tmp, conc=halo_conc, z=z)
                                elif halo_typ == 'TPH0.0':
                                    try:
                                        Mhalo = utils._Mhalo_from_fDMv_TPH(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff_tmp,
                                                r=Reff_disk_tmp, conc=halo_conc, z=z, alpha=0.)
                                    except:
                                        Mhalo = np.NaN

                            #########
                            if halo_typ == 'TPH':
                                Mhalo_SMHM = utils._smhm_relation(z=z, lmstar=lmass_tmp)
                                Mhalo = Mhalo_SMHM
                                if fDMvReff_tmp == 0.:
                                    Mhalo = 1.e2
                                    alphaTPH = 0.
                                elif fDMvReff_tmp == 1.:
                                    Mhalo = 1.e18
                                    alphaTPH = 1.
                                else:
                                    alphaTPH = utils._alpha_from_fDMv_TPH(vcirc_baryons=vcirc_baryons, fDMv=fDMvReff_tmp,
                                                    r=Reff_disk_tmp, conc=halo_conc, z=z, Mhalo=Mhalo)

                            #########
                            if np.isfinite(Mhalo):
                                if halo_typ == 'NFW':
                                    menc_halo = calcs.NFW_halo_enclosed_mass(r=rhalf_disk, Mvirial=Mhalo, conc=halo_conc, z=z)
                                elif halo_typ == 'TPH0.0':
                                    menc_halo = calcs.TPH_halo_enclosed_mass(r=rhalf_disk, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)
                                elif halo_typ == 'TPH':
                                    menc_halo = calcs.TPH_halo_enclosed_mass(r=rhalf_disk, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=alphaTPH)

                                menc_tot_half = menc_baryons + menc_halo

                                ####
                                if halo_typ == 'NFW':
                                    vcirc_halo = calcs.NFW_halo_vcirc(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z)
                                elif halo_typ == 'TPH0.0':
                                    vcirc_halo = calcs.TPH_halo_vcirc(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=0.)
                                elif halo_typ == 'TPH':
                                    vcirc_halo = calcs.TPH_halo_vcirc(r=Reff_disk_tmp, Mvirial=Mhalo, conc=halo_conc, z=z, alpha=alphaTPH)

                                vcirc_tot = np.sqrt(vcirc_baryons**2 + vcirc_halo**2)

                                ktot_est = calcs.virial_coeff_tot(Reff_disk_tmp, total_mass=2.*menc_tot_half,
                                               vc=vcirc_tot, q=None, Reff=None, n=None, i=None)

                                grid_fDM_ratio[mm, jj] = ktot_est

                            else:
                                grid_fDM_ratio[mm, jj] = np.NaN

                    if grid_fDM_ratio_stack is None:
                        grid_fDM_ratio_stack = []
                    grid_fDM_ratio_stack.append(grid_fDM_ratio)
                    grid_fDM_ratio_pair.append('{}-{}'.format(keyx, keyy))

    stack_cnt = 0
    for i in range(n_rows):
        keyy = keys[i+1]
        ylim = lims[i+1]
        ylabel = labels[i+1]

        for j in range(n_cols):
            k = i*n_cols + j
            ax = axes[k]
            keyx = keys[j]
            xlim = lims[j]

            xarr = arr_stack[j]
            # Reset each time
            yarr = arr_stack[i+1]
            if (i == n_rows-1):
                xlabel = labels[j]
            else:
                xlabel = None
            if j > 0:
                ylabel = None

            if (j > i):
                if (i == 0) & (j == 2):
                    # COLORBAR
                    cax, kw = colorbar.make_axes_gridspec(ax, pad=0.01,
                            fraction=5./101., aspect=20.)
                    cbar = plt.colorbar(im_fDM_grid, cax=cax, extend='both', **kw)
                    cbar.ax.tick_params(labelsize=fontsize_ticks_sm)
                    cbar.set_label(label_c, fontsize=fontsize_labels_sm)
                    ax.tick_params(labelbottom='off', labelleft='off')
                    for sp in ['top', 'bottom', 'left', 'right']: ax.spines[sp].set_visible(False)
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])

                    ############
                    bbox_props = dict(boxstyle="square", fc="None", ec=ecrect, lw=1)
                    ann_str = r'$\mathbf{Fiducial:}$'
                    ax.annotate(ann_str, xy=(0.1, 0.75),
                                xycoords='axes fraction', va='top',
                                ha='left', fontsize=fontsize_labels_sm,
                                bbox=bbox_props)
                    ann_str = r'$z={:0.1f}$'.format(z)
                    ann_str += '\n'
                    ann_str += r'{} halo'.format(halo_typ)
                    ann_str += '\n'
                    ann_str += r'$\mathrm{conc}_{\mathrm{halo}}='+r'{:0.1f}$'.format(halo_conc)
                    ann_str += '\n'
                    ann_str += r'$f_{\mathrm{DM}}^v(R_{e,\mathrm{disk}})='+r'{:0.1f}$'.format(fDMvReff_0)

                    ax.annotate(ann_str, xy=(0.1, 0.5),
                                xycoords='axes fraction', va='center',
                                ha='left', fontsize=fontsize_ann_lg)

                    ann_str = r'$\log_{10}(M_{*}/M_{\odot})'+r'={:0.1f}$'.format(lmass_0)
                    ann_str += '\n'
                    ann_str += r'$B/T={:0.2f}$'.format(BT_0)
                    ann_str += '\n'
                    ann_str += r'$R_{e,\mathrm{disk}}'+r'={:0.1f}$'.format(Reff_disk_0)
                    ann_str += '\n'
                    ann_str += r'$q_{0,\mathrm{disk}}'+r'={:0.2f}$'.format(1./invq_disk_0)
                    ann_str += '\n'
                    ann_str += r'$n_{\mathrm{disk}}'+r'={:0.1f}$'.format(n_disk_0)
                    ann_str += '\n'
                    ###
                    ann_str += r'$R_{e,\mathrm{bulge}}'+r'={:0.1f}$'.format(Reff_bulge)
                    ann_str += '\n'
                    ann_str += r'$q_{0,\mathrm{bulge}}'+r'={:0.2f}$'.format(1./invq_bulge)
                    ann_str += '\n'
                    ann_str += r'$n_{\mathrm{bulge}}'+r'={:0.1f}$'.format(n_bulge)

                    ax.annotate(ann_str, xy=(0.5, 0.5),
                                xycoords='axes fraction', va='center',
                                ha='left', fontsize=fontsize_ann_lg)

                else:
                    if ax is not None:
                        ax.axis('off')
            else:
                # Get fiducial values:
                if keyx == 'lmass':
                    xfid = lmass_0
                elif keyx == 'fDMvReff':
                    xfid = fDMvReff_0
                elif keyx == 'BT':
                    xfid = BT_0
                elif keyx == 'Reff_disk':
                    xfid = Reff_disk_0
                elif keyx == 'q_disk':
                    xfid = 1./invq_disk_0
                elif keyx == 'n_disk':
                    xfid = x
                ####
                if keyy == 'lmass':
                    yfid = lmass_0
                elif keyy == 'fDMvReff':
                    yfid = fDMvReff_0
                elif keyy == 'BT':
                    yfid = BT_0
                elif keyy == 'Reff_disk':
                    yfid = Reff_disk_0
                elif keyy == 'q_disk':
                    yfid = 1./invq_disk_0
                elif keyy == 'n_disk':
                    yfid = n_disk_0

                ####
                grid_fDM_ratio = grid_fDM_ratio_stack[stack_cnt]
                grid_fDM_names = grid_fDM_ratio_pair[stack_cnt]
                stack_cnt_cur = stack_cnt
                stack_cnt += 1

                ####
                if keyx == 'q_disk':
                    xarr = 1./xarr
                if keyy == 'q_disk':
                    yarr = 1./yarr

                ###
                # ADAPTIVE GRID SIZE BASED ON X,Y SAMPLING:
                xarr_edges = np.ones(len(xarr)+1)
                xarr_edges[1:-1] = 0.5*(xarr[1:] + xarr[:-1])
                xarr_edges[0] = xarr[0] - (xarr_edges[1] - xarr[0])
                xarr_edges[-1] = xarr[-1] + (xarr[-1] - xarr_edges[-2])

                yarr_edges = np.ones(len(yarr)+1)
                yarr_edges[1:-1] = 0.5*(yarr[1:] + yarr[:-1])
                yarr_edges[0] = yarr[0] - (yarr_edges[1] - yarr[0])
                yarr_edges[-1] = yarr[-1] + (yarr[-1] - yarr_edges[-2])

                ###
                # EQUAL PIXEL SPACING:
                xarr_edges = np.arange(len(xarr)+1)
                yarr_edges = np.arange(len(yarr)+1)
                if keyx == 'q_disk':
                    xarr_edges = xarr_edges[::-1]
                if keyy == 'q_disk':
                    yarr_edges = yarr_edges[::-1]

                im_fDM_grid = ax.pcolormesh(xarr_edges, yarr_edges, grid_fDM_ratio, cmap=cmap, vmin=vmin_c, vmax=vmax_c)

                whmx = np.where(xarr == xfid)[0]
                whmy = np.where(yarr == yfid)[0]
                if (len(whmx)==1) & (len(whmy)==1):
                    rect = Rectangle((xarr_edges[whmx[0]], yarr_edges[whmy[0]]),
                                xarr_edges[whmx[0]+1]-xarr_edges[whmx[0]],
                                yarr_edges[whmy[0]+1]-yarr_edges[whmy[0]],
                                angle=0., lw=1., edgecolor=ecrect, facecolor='None')
                    ax.add_patch(rect)

                ####
                ax.xaxis.set_major_locator(FixedLocator(0.5*(xarr_edges[1:] + xarr_edges[:-1])))
                ax.yaxis.set_major_locator(FixedLocator(0.5*(yarr_edges[1:] + yarr_edges[:-1])))

                xarr_formatter = ["{}".format(x) for x in xarr]
                yarr_formatter = ["{}".format(y) for y in yarr]
                xarr_formatter = np.array(xarr_formatter)
                yarr_formatter = np.array(yarr_formatter)
                if keyx == 'q_disk':
                    whm = np.where(1./xarr == 3.)[0]
                    xarr_formatter[whm] = "0.33"
                if keyy == 'q_disk':
                    whm = np.where(1./yarr == 3.)[0]
                    yarr_formatter[whm] = "0.33"

                if (keyx == "BT") | (keyx == "fDMvReff"):
                    xarr_tmp = np.copy(xarr)
                    xarr_tmp[1::2] = -99.
                    xarr_formatter[xarr_tmp==-99.] = ""
                #
                if (keyy == "BT") | (keyy == "fDMvReff"):
                    yarr_tmp = np.copy(yarr)
                    yarr_tmp[1::2] = -99.
                    yarr_formatter[yarr_tmp==-99.] = ""

                ax.xaxis.set_major_formatter(FixedFormatter(xarr_formatter.tolist()))
                ax.yaxis.set_major_formatter(FixedFormatter(yarr_formatter.tolist()))

                ax.tick_params(labelsize=fontsize_ticks)

                if xlabels[k] is not None:
                    ax.set_xlabel(xlabels[k], fontsize=fontsize_labels)
                else:
                    ax.set_xticklabels([])

                if ylabels[k] is not None:
                    ax.set_ylabel(ylabels[k], fontsize=fontsize_labels)
                else:
                    ax.set_yticklabels([])

    if fileout is not None:
        plt.savefig(fileout, bbox_inches='tight', dpi=600)
        plt.close()
    else:
        plt.show()

    return grid_fDM_ratio_stack, grid_fDM_ratio_pair

def make_all_paper_plots(output_path=None, table_path=None):
    """
    Wrapper function to make all plots for the paper.

    Saves plots in PDF format.

    Parameters
    ----------
        output_path: str
            Path to the directory where the plots will be saved.

        table_path: str
            Path to the directory where the Sersic profile tables are located.

    Returns
    -------

    """

    # Figure 1
    plot_compare_mencl(output_path=output_path, table_path=table_path, q_arr=[1., 0.4, 0.2])

    # Figure 2
    plot_rhalf_3D_sersic_potential(output_path=output_path, table_path=table_path)

    # Figure 3
    plot_composite_menc_vcirc_profile_invert(output_path=output_path, table_path=table_path,
                q_arr=[1., 0.4, 0.2], n_arr=[1., 4.])

    # Figure 4
    plot_virial_coeff(output_path=output_path, table_path=table_path,
                q_arr=[0.2, 0.4, 0.6, 0.8, 1., 1.5, 2.])

    # Figure 5
    plot_example_galaxy_mencl_vcirc(bt_arr=[0., 0.25, 0.5, 0.75, 1.0],
                output_path=output_path, table_path=table_path,
                z=2., Mbaryon=5.e10,
                Reff_disk=5., n_disk=1., invq_disk=5.,
                Reff_bulge=1., n_bulge=4., invq_bulge=1.,
                Mhalo=1.e12, halo_conc=4.,
                logradius=False, rmin=0., rmax=15., rstep=0.01)

    # Figure 6
    plot_fdm_calibration(Mbaryon_arr=[10**10.5],
                q_disk_arr = [0.01, 0.05, 0.1, 0.2, 0.25, 0.4, 0.6, 0.8, 1.],
                Mhalo_arr=[1.e12],
                Reff_disk_arr=[5.],
                halo_conc_arr=[4.],
                output_path=output_path, table_path=table_path,
                del_fDM=False)


    # Figure 7
    plot_toy_impl_fDM_calibration_z_evol(output_path=output_path, table_path=table_path,
                n_disk=1., Reff_bulge=1., n_bulge=4., invq_bulge=1.,
                del_fDM=False)

    # Figure 8
    plot_alpha_vs_r(output_path=output_path, table_path=table_path,
                n_arr=[0.5, 1., 2., 4., 8.])

    # Figure 9
    plot_AD_sersic_potential_alpha_vs_r(output_path=output_path, table_path=table_path,
                sigma0_arr = [30., 60., 90.],
                q_arr=[1., 0.2],
                n_arr=[0.5, 1., 2., 4.])

    # Figure 10


    return None


if __name__ == "__main__":
    # From the command line, call the wrapper to make all plots. Input args: output_path, table_path

    output_path = sys.argv[1]
    table_path = sys.argv[2]

    make_all_paper_plots(output_path=output_path, table_path=table_path)