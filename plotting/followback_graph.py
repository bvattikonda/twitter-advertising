#!/usr/bin/env python

# Script to plot the follow back phenomena amongst advertisers in TWitter

import sys
import datetime
import string
import argparse
import os
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

def get_user_connections(user_id, connections_filename):
    connections_file = open(connections_filename, 'r')
    for line in connections_file:
        splitline = line.strip().split('-')
        fetched_userid = int(splitline[0])
        if user_id == fetched_userid:
            followers = ast.literal_eval(splitline[1])
            friends = ast.literal_eval(splitline[2])
            connections_file.close()
            return followers, friends
    connections_file.close()
    raise Exception('User information not fetched before %d' % (user_id))

def load_root_users(root_usersfilename):
    root_usersfile = open(root_usersfilename, 'r')
    root_users = set()
    for line in root_usersfile:
        root_users.add(int(line.strip()))
    return root_users

def get_followback_rate(root_users, connections_filename):
    followback_rate = list()
    for user in root_users:
        followers, friends = get_user_connections(user, connections_filename)
        if len(followers) < 1000:
            continue
        followback_rate.append(len(set(friends) & set(followers)) / \
            float(len(followers)))
    return followback_rate

def main():
    parser = argparse.ArgumentParser(description = 'Generate follow back graph')
    parser.add_argument('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_argument('--destination', required = True, dest =\
        'destination_dir', help = 'Directory to which graphs should be saved')
    parser.add_argument('--connections', required = True,\
        help = 'Text file of connections')
    parser.add_argument('--root', required = True,\
        help = 'Text file with the root users')
    args = parser.parse_args()

    fig = create_figure()
    root_users = load_root_users(args.root)
    plot_data = get_followback_rate(root_users, args.connections)
    subplot = fig.add_subplot(1, 1, 1)
    plot_cdf(subplot, plot_data)
    subplot.set_xlabel('Follow back ratio', fontproperties = LABEL_PROP)
    subplot.set_ylabel('CDF', fontproperties = LABEL_PROP)
    subplot.set_title('Follow back rate', fontproperties = TITLE_PROP) 
    subplot.set_ylim(0, 1)
    print_figure(fig, args.destination_dir, 'follow_back', args.extension)

if __name__ == '__main__':
    main()
