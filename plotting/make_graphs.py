#!/usr/bin/env python

# This script is the main graph to generate graphs for twitter data

import sys
import datetime
import string
import argparse
import os
import numpy
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
        
def main():
    parser = argparse.ArgumentParser(description = 'Generate graphs')
    parser.add_argument('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_argument('--destination', required = True, dest =\
        'destination_dir', help = 'Directory to which graphs should be saved')
    parser.add_argument('--adusers', required = True, dest =\
        'ad_pickle_dir', help = 'Directory of advertisers\' pickle files')
    parser.add_argument('--normusers', required = True, dest =\
        'norm_pickle_dir', help = 'Directory of normal users\' pickle files')
    args = parser.parse_args()

    # non-disclosure graph
#    print 'Generating non-disclosure graph'
#    fig = create_figure()
#    subplot = fig.add_subplot(1, 1, 1)
#    plot_data = non_disclosure(args.ad_pickle_dir)
#    plot_cdf(subplot, plot_data)
#    subplot.set_xlabel('% Non-disclosure', fontproperties = LABEL_PROP)
#    subplot.set_ylabel('CDF of users', fontproperties = LABEL_PROP)
#    print_figure(fig, args.destination_dir, 'non_disclosure', args.extension)
#
#    # repeated links graph
#    print 'Generating repeated links graph'
#    fig = create_figure()
#    subplot = fig.add_subplot(1, 1, 1)
#    plot_data = repeated_links(args.ad_pickle_dir)
#    plot_cdf(subplot, [value for key, value in plot_data.iteritems()])
#    subplot.set_xlabel('Number of users tweeting same link', fontproperties =\
#       LABEL_PROP)
#    subplot.set_ylabel('CDF', fontproperties = LABEL_PROP)
#    print_figure(fig, args.destination_dir, 'repeated_links', args.extension)
#
#    # connections graphs for advertisers and normal users
#    print 'Generating connections graph'
#    fig = create_figure()
#    fig.set_size_inches(fig_width, fig_length * 2, forward = True)
#    subplot = fig.add_subplot(2, 1, 1)
#    advertisers_data, normal_users_data = number_of_connections(\
#        args.ad_pickle_dir, args.norm_pickle_dir)
#    plot_cdf(subplot, [followers for followers, friends in advertisers_data],\
#        label = 'Followers', marker = '+', color = 'b') 
#    plot_cdf(subplot, [friends for followers, friends in advertisers_data],\
#        label = 'Friends', marker = 'x', color = 'g')
#    subplot.set_title('Advertisers', fontproperties = TITLE_PROP)
#    subplot.legend(loc = 4, prop = LEGEND_PROP)
#    subplot.set_xlim(0, 4000)
#
#    subplot = fig.add_subplot(2, 1, 2)
#    plot_cdf(subplot, [followers for followers, friends in normal_users_data],\
#        label = 'Followers', marker = '+', color = 'b') 
#    plot_cdf(subplot, [friends for followers, friends in normal_users_data],\
#        label = 'Friends', marker = 'x', color = 'g')
#    subplot.legend(loc = 4, prop = LEGEND_PROP)
#    subplot.set_title('Normal users', fontproperties = TITLE_PROP)
#    subplot.set_xlim(0, 4000)
#    print_figure(fig, args.destination_dir, 'connections', args.extension)
#
#    # retweets graph
#    print 'Generating retweets graph'
#    fig = create_figure()
#    subplot = fig.add_subplot(1, 1, 1)
#    ad_plot_data, norm_plot_data = percentage_retweets(args.ad_pickle_dir,\
#        args.norm_pickle_dir)
#    ad_line = plot_cdf(subplot, ad_plot_data)
#    norm_line = plot_cdf(subplot, norm_plot_data)
#    subplot.legend((ad_line, norm_line), ('Advertisers', 'Normal users'),\
#        prop = LEGEND_PROP)
#    subplot.set_xlabel('% retweets', fontproperties = LABEL_PROP)
#    subplot.set_ylabel('CDF', fontproperties = LABEL_PROP)
#    print_figure(fig, args.destination_dir, 'retweets', args.extension)

    # domain statistics
    print 'Generating domain statistics graph'
    fig = create_figure()
    subplot = fig.add_subplot(1, 1, 1)
    disclosed_ads, undisclosed_ads = domain_stats(args.ad_pickle_dir)
    keys = set(disclosed_ads) | set(undisclosed_ads)
    total_ads = {key: disclosed_ads[key] + undisclosed_ads[key] for key in keys}
    disclosed_bar = plot_bar(subplot, [disclosed_ads[key] * 100.0 /\
        float(total_ads[key]) for key in keys], color = 'blue')
    undisclosed_bar = plot_bar(subplot, [undisclosed_ads[key] * 100.0 /\
        float(total_ads[key]) for key in keys], bottom = [disclosed_ads[key]\
        * 100.0 / float(total_ads[key]) for key in keys], color = 'red')
    print keys
    subplot.set_xticks(numpy.arange(len(keys)) + 0.35 / 2)
    subplot.set_xticklabels([string.replace(key, '(^|\\.)', '').rstrip('$') for\
        key in keys], fontproperties = fm.FontProperties(size=4))
    subplot.set_xlabel('Domain name', fontproperties = LABEL_PROP)
    subplot.set_ylabel('Number of tweets', fontproperties = LABEL_PROP)
    print_figure(fig, args.destination_dir, 'domain_stats', args.extension)

if __name__ == '__main__':
    main()
