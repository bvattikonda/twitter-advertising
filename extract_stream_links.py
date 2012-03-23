#!/usr/bin/env python 

# Get the links that are present in the sample tweets that we have
# collected so far

import os
import json
import optparse
import logging
import sys

def get_filename(stream_dir, count):
    filenames = os.listdir(stream_dir)
    for filename in filenames:
        if filename.startswith('sample_' + str(count) + '_'):
            return filename
    return None

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Extract URLs',\
        usage = usage)
    parser.add_option('--stream_data', action = 'store',\
        help = 'Directory which has all the streaming data stored')
    return parser

def correct_options(options):
    if not options.stream_data:
        return False
    if not os.path.exists(options.stream_data):
        return False
    return True
 
def get_extracted(data_dir):
    filenames = os.listdir(data_dir)
    extracted = 0
    for filename in filenames:
        if filename.startswith('links_') and\
            filename.endswith('.links'):
            end = int(filename.split('.')[0].split('_')[-1])
            if extracted < end:
                extracted = end
    return extracted

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()

    # set up logging
    logging.basicConfig(filename = os.path.join(options.stream_data,\
        'links.log'),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)

    extracted = get_extracted(options.stream_data)
    logging.critical('Starting at %d' % (extracted))
    while True:
        filename = get_filename(options.stream_data, extracted)
        current_filename = os.path.join(options.stream_data,\
                filename)
        if not os.path.exists(current_filename):
            logging.critical('Finished extracting all existing files')
            break

        logging.info('Extracting links from %s' % (filename))
        begin = int(filename.replace('.tweets', '').split('_')[1])
        end = int(filename.replace('.tweets', '').split('_')[-1])
        current_file = open(current_filename)
        links_filename = os.path.join(options.stream_data, 'links_' +\
                    str(begin) + '_' + str(end) + '.links')
        links_file = open(links_filename, 'w')
        while True:
            line = current_file.readline()
            if not len(line):
                break
            try:
                tweet = json.loads(line)
            except:
                links_file.close()
                os.remove(links_filename)
                raise
            for url in tweet['entities']['urls']:
                if url['expanded_url']:
                    baseURL = url['expanded_url'].strip()
                elif url['url']:
                    baseURL = url['url'].strip()
                else:
                    continue
                links_file.write(baseURL + '\n')

        links_file.close()
        current_file.close()
        extracted = end

if __name__ == '__main__':
    main()
