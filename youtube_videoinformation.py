import gdata.youtube
import gdata.youtube.service
import inspect
import os
import optparse
from urlparse import urlparse

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True
yt_service.email = 'amlearner@gmail.com'
yt_service.password = 'PASSWORD'
yt_service.developer_key =\
'AI39si5FpQvRdE6qr891vm12xcAC-sh5Fln8fzn-pgmfjzZiQ-P7v5MDj2Nr-sUy0Vn_aS5tNrCzrAS60AO2uImjzG5Kn07tHg'

def fetch_information(data_dir, video_id):
    videofilename = os.path.join(data_dir, video_id + '.yt')
    if not os.path.exists(videofilename):
        try:
            entry = yt_service.GetYouTubeVideoEntry(video_id = video_id)
        except gdata.service.RequestError as e:
            print e
            return 
        videofile = open(videofilename, 'w')
        videofile.write(str(entry))
    return

def parse_args():
    parser = optparse.OptionParser(description = 'YouTube Video\
            information')
    parser.add_option('--data_dir', action = 'store',\
        help = 'Directory to which the data has to be saved')
    parser.add_option('--input', action = 'store',\
        help = 'File which has YouTube URLs')
    return parser

def correct_options(options):
    if not options.data_dir:
        return False
    if not options.input:
        return False
    return True

def parse_link(url):
    parseresult = urlparse(url)
    query_params = parseresult.query.split('&')
    for query_param in query_params:
        if query_param.startswith('v='):
            return query_param.replace('v=', '')

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return
    
    youtubelinksfile = open(options.input, 'r')
    count = 0
    for line in youtubelinksfile:
        video_id = parse_link(line.strip())
        if not video_id:
            continue
        print count, video_id
        fetch_information(options.data_dir, video_id)
        count += 1

if __name__ == '__main__':
    main()
