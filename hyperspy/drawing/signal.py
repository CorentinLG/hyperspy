# -*- coding: utf-8 -*-
# Copyright 2007-2011 The Hyperspy developers
#
# This file is part of  Hyperspy.
#
#  Hyperspy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  Hyperspy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  Hyperspy.  If not, see <http://www.gnu.org/licenses/>.

# This file contains plotting code generic to the Signal class.

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets
from mpl_toolkits.axes_grid1 import make_axes_locatable

import widgets
import utils

def _plot_quiver_scatter_overlay(image, axes_manager,
                                 calibrate=True, shifts=None, 
                                 char=None, ax=None, comp_label=None,
                                 img_cmap=plt.cm.gray,
                                 sc_cmap=plt.cm.jet,
                                 quiver_color='white',
                                 vector_scale=100,
                                 ):
    """quiver plot notes:
       
       The vector_scale parameter scales the quiver
           plot arrows.  The vector is defined as
           one data unit along the X axis.  If shifts
           are small, set vector_scale so that when
           they are multiplied by vector_scale, they
           are on the scale of the image plot.
    """
    if ax==None:
        ax=plt.gca()
    axes=axes_manager._slicing_axes
    extent=None
    if calibrate:
        extent=(axes[0].low_value,
                axes[0].high_value,
                axes[1].high_value,
                axes[1].low_value)
        if shifts is not None:
            slocs=shifts['location'].squeeze()
            shifts=shifts['shift'].squeeze()
            slocs[:,0]=slocs[:,0]*axes[0].scale+axes[0].offset
            slocs[:,1]=slocs[:,1]*axes[1].scale+axes[1].offset
            shifts[:,0]=shifts[:,0]*axes[0].scale+axes[0].offset
            shifts[:,1]=shifts[:,1]*axes[1].scale+axes[1].offset
        if char is not None:
            clocs=char['location'].squeeze()
            clocs[:,0]=clocs[:,0]*axes[0].scale+axes[0].offset
            clocs[:,1]=clocs[:,1]*axes[1].scale+axes[1].offset
    ax.imshow(image,interpolation='nearest',
              cmap=img_cmap,extent=extent)
    if comp_label:
        plt.title(comp_label)
    if shifts <> None:
        ax.quiver(slocs[:,0],slocs[:,1],
                  shifts[:,0], shifts[:,1],
                  units='x',color=quiver_color,
                  scale=vector_scale, scale_units='x')
    if char <> None:
        sc=ax.scatter(clocs[:,0],clocs[:,1],
                   c=char['char'], cmap=sc_cmap)
        div=make_axes_locatable(ax)
        cax=div.append_axes('right',size="5%",pad=0.05)
        plt.colorbar(sc,cax=cax)
    if extent:
        ax.set_xlim(extent[:2])
        ax.set_ylim(extent[2:])
    else:
        ax.set_xlim(0,image.shape[0])
        ax.set_ylim(image.shape[1],0)
    return ax
        
def _plot_1D_component(factors, idx, axes_manager, ax=None, 
                       calibrate=True, comp_label=None,
                       same_window=False):
    if ax==None:
        ax=plt.gca()
    axis=axes_manager._slicing_axes[0]
    if calibrate:
        x=axis.axis
        plt.xlabel(axis.units)
    else:
        x=np.arange(axis.size)
        plt.xlabel('Channel index')
    ax.plot(x,factors[:,idx],label='%s %i'%(comp_label,idx))
    if comp_label and not same_window:
        plt.title('%s %s' % (comp_label,idx))
    return ax

def _plot_2D_component(factors, idx, axes_manager, 
                       calibrate=True, ax=None,
                       comp_label=None, cmap=plt.cm.jet,
                       ):
    if ax==None:
        ax=plt.gca()
    axes=axes_manager._slicing_axes
    shape=(axes[1].size,axes[0].size)
    extent=None
    if calibrate:
        extent=(axes[0].low_value,
                axes[0].high_value,
                axes[1].high_value,
                axes[1].low_value)
    if comp_label:
        plt.title('%s %s' % (comp_label,idx))
    im=ax.imshow(factors[:,idx].reshape(shape),
                 cmap=cmap, interpolation = 'nearest',
                 extent=extent)
    div=make_axes_locatable(ax)
    cax=div.append_axes("right",size="5%",pad=0.05)
    plt.colorbar(im,cax=cax)
    return ax

def _plot_component(axes_manager,
                    factors=None, idx=None,
                    on_peaks=False, comp_label=None,
                    image=None, calibrate=True, 
                    shifts=None, char=None, 
                    ax=None, img_cmap=plt.cm.gray,
                    sc_cmap=plt.cm.jet,
                    cmap=plt.cm.jet,
                    quiver_color='white',
                    vector_scale=100,):
    if axes_manager.signal_dimension==1:
        return self._plot_1D_component(factors=factors,
                        idx=idx,axes_manager=axes_manager,
                        ax=ax, calibrate=calibrate,
                        comp_label=comp_label,
                        same_window=same_window)
    elif axes_manager.signal_dimension==2:
        if on_peaks:
            return self._plot_quiver_scatter_overlay(
                        image=image,
                        axes_manager=axes_manager,
                        shifts=shifts,char=char,ax=ax,
                        comp_label=comp_label,
                        img_cmap=img_cmap,
                        sc_cmap=sc_cmap,
                        quiver_color=quiver_color,
                        vector_scale=vector_scale)
        else:
            return _plot_2D_component(factors=factors, 
                                      idx=idx, 
                                      axes_manager=axes_manager,
                                      calibrate=calibrate,ax=ax, 
                                      cmap=cmap,
                                      comp_label=comp_label)

def _plot_score(scores, idx, axes_manager, ax=None, 
                comp_label=None, no_nans=True, 
                calibrate=True, cmap=plt.cm.gray,
                same_window=False):
    if ax==None:
        ax=plt.gca()
    if no_nans:
        scores=np.nan_to_num(scores)
    axes=axes_manager._non_slicing_axes
    if axes_manager.navigation_dimension==2:
        extent=None
        # get calibration from a passed axes_manager
        shape=axes_manager.navigation_shape
        if calibrate:
            extent=(axes[1].low_value,
                    axes[1].high_value,
                    axes[0].high_value,
                    axes[0].low_value)
        im=ax.imshow(scores[idx].reshape(shape),cmap=cmap,extent=extent,
                     interpolation='nearest')
        if calibrate:
            plt.xlabel(axes[1].units)
            plt.ylabel(axes[0].units)
        else:
            plt.xlabel('pixels')
            plt.ylabel('pixels')
        if comp_label:
            plt.title('%s %s'%(comp_label,idx))
        div=make_axes_locatable(ax)
        cax=div.append_axes("right",size="5%",pad=0.05)
        plt.colorbar(im,cax=cax)
    elif axes_manager.navigation_dimension == 1:
        if calibrate:
            x=axes[0].axis
        else:
            x=np.arange(axes[0].size)
        ax.step(x,scores[idx],
                label='%s %s'%(comp_label,idx))
        if comp_label and not same_window:
            plt.title('%s %s'%(comp_label,idx))
        plt.ylabel('Score, Arb. Units')
        if calibrate:
            if axes[0].units<>'undefined':
                plt.xlabel(axes[0].units)
            else:
                plt.xlabel('depth')
        else:
            plt.xlabel('depth')
    else:
        messages.warning_exit('View not supported')