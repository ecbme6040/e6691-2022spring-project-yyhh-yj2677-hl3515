"""
Download FineGym dataset from youtube according to video id.
"""

import json
import os

"""
Assign output path here!
"""
output_path = './videos'
if not os.path.exists(output_path):
    os.mkdir(output_path)

"""
Give path of annotations to get youtube ids.
"""
json_path = 'dataset_info/finegym/annotations/finegym_annotation_info_v1.1.json'
data = json.load(open(json_path, 'r'))
youtube_ids = list(data.keys())

"""
Download all videos according to youtube ids using yt-dlp tool.
"""
for youtube_id in youtube_ids:
    vid_loc = output_path + '/' + str(youtube_id)
    url = 'http://www.youtube.com/watch?v=%s' % youtube_id
    if not os.path.exists(vid_loc):
        os.mkdir(vid_loc)
    os.system('yt-dlp -o ' + vid_loc + '/' + youtube_id + '.mp4' + ' -f mp4 ' + url)
