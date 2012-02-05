#!/usr/bin/env python

# Script to plot the follow back phenomena amongst advertisers in TWitter

import sys
import datetime
import string
import argparse
import os
import gc
import ast
import numpy
import matplotlib
import matplotlib.font_manager as fm
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import ScalarFormatter
from graph_functions import *
from plot_engine import *

# Figure dimensions
fig_width = 5
fig_length = 2.25 


matplotlib.rcParams['axes.labelsize'] = 10
matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10

LEGEND_PROP = matplotlib.font_manager.FontProperties(size=9)
TITLE_PROP = matplotlib.font_manager.FontProperties(size=9)
LABEL_PROP = matplotlib.font_manager.FontProperties(size=9)
MARKERS = ['b-+', 'g-x', 'c-s', 'm-^', 'y->', 'r-p']
MARKEVERY = 10 

# Can be used to adjust the border and spacing of the figure
fig_left = 0.15
fig_right = 0.91
fig_bottom = 0.21
fig_top = 0.94
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

def extract_list(line):
    line_without_brackets = line[1:-1]
    splitline = line_without_brackets.split(', ')
    output = list()
    for item in splitline:
        output.append(int(item))
    return set(output)

def get_followback_rate(data_dir):
    followback_rate = list()
    for filename in os.listdir(data_dir):
        print filename
        file = open(os.path.join(data_dir, filename), 'r')
        file.readline()
        followers_line = file.readline().strip()
        friends_line = file.readline().strip()
        followers = extract_list(followers_line)
        friends = extract_list(friends_line)
        if len(followers) < 1000:
            continue
        followback_rate.append(len(friends & followers) / \
            float(len(followers)))
        followers = None
        friends = None
        gc.collect()
    return followback_rate

def main():
    parser = argparse.ArgumentParser(description = 'Generate follow back graph')
    parser.add_argument('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_argument('--destination', required = True, dest =\
        'destination_dir', help = 'Directory to which graphs should be saved')
    parser.add_argument('--data_dir', required = True,\
        help = 'Directory which has files with user info')
    args = parser.parse_args()

    fig = create_figure()
    plot_data = get_followback_rate(args.data_dir)
    subplot = fig.add_subplot(1, 1, 1)
    plot_cdf(subplot, plot_data)
    subplot.set_xlabel('Follow back ratio', fontproperties = LABEL_PROP)
    subplot.set_ylabel('CDF', fontproperties = LABEL_PROP)
    subplot.set_title('Follow back rate', fontproperties = TITLE_PROP) 
    subplot.set_ylim(0, 1)
    print_figure(fig, args.destination_dir, 'follow_back_individual', args.extension)

if __name__ == '__main__':
    main()
