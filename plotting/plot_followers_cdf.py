#!/usr/bin/env python

# Script to plot the CDF of amount of money that the publishers make on adly

import sys
import datetime
import string
import argparse
import os
import json
import ast
import matplotlib
import matplotlib.font_manager as fm
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import ScalarFormatter
from collections import defaultdict
from graph_functions import *
from plot_engine import *

# Figure dimensions
fig_width = 5
fig_length = 2.25 

matplotlib.rcParams['axes.labelsize'] = 10
matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10

LEGEND_PROP = matplotlib.font_manager.FontProperties(size=7)
TITLE_PROP = matplotlib.font_manager.FontProperties(size=9)
LABEL_PROP = matplotlib.font_manager.FontProperties(size=9)
COLORS = ['b', 'g', 'c', 'm', 'y', 'r']
MARKERS = ['+', 'x', 's', '^', '>', 'p']
MARKEVERY = 100

# Can be used to adjust the border and spacing of the figure
fig_left = 0.15
fig_right = 0.91
fig_bottom = 0.21
fig_top = 0.89
fig_hspace = 0.5

###############################################################################
# Configuration parameters end here
###############################################################################

def create_figure():
    fig = Figure()
    fig.set_size_inches(fig_width, fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)
    return fig

def print_figure(fig, destination_directory, filename, extension):
    canvas = FigureCanvasAgg(fig)
    if extension == '.png':
        canvas.print_figure(os.path.join(destination_directory, \
            filename + extension), dpi = 110)
    elif extension == '.eps':
        canvas.print_eps(os.path.join(destination_directory,\
            filename + extension), dpi = 110)

def get_args():
    parser = argparse.ArgumentParser(description = 'Generate earnings graph')
    parser.add_argument('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_argument('--destination', required = True, dest =\
        'destination_dir', help = 'Directory to which graphs should be saved')
    parser.add_argument('--datafile', required = True,\
        help = 'File which has all the numbers')
    return parser.parse_args()

def main():
    args = get_args()    
    fig = create_figure()
    plot_data = defaultdict(list)
    all_data = list()
    for line in open(args.datafile, 'r'):
        key, value = line.strip().split('\t')
        plot_data[key].append(int(value))
        all_data.append(int(value))
    print len(all_data)
    subplot = fig.add_subplot(1, 1, 1)
    count = 0
    for key in plot_data:
        plot_cdf(subplot, plot_data[key],\
            color = COLORS[count],\
            marker = MARKERS[count],\
            markevery = MARKEVERY,\
            label = key)
        count += 1 
    plot_cdf(subplot, all_data,\
        color = 'k',\
        marker = '*',\
        label = 'All',\
        markevery = MARKEVERY)
    subplot.set_xlabel('Number of followers', fontproperties = LABEL_PROP)
    subplot.set_ylabel('CDF', fontproperties = LABEL_PROP)
    subplot.set_title('Number of followers', fontproperties = TITLE_PROP) 
    subplot.legend(prop = LEGEND_PROP, loc = (0.8, 0.2))
    subplot.set_ylim(0, 1)
    subplot.set_xlim(0, 4000)
    print_figure(fig, args.destination_dir,\
        'followers', args.extension)

if __name__ == '__main__':
    main()
