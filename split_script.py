"""
Cut FineGym dataset videos into clips and sublicps.
Each clip contains the whole exercise (event)
Each subclip contains a move/step (segment, action)
"""

"""
Command to reduce video size before executing this code:
-n: Do not overwrite
-y: Do overwrite

for file in videos/*/*.mp4
do
    if ! grep -q _reduced <<< "$file"; then
        ffmpeg -hwaccel cuda -n -i "$file" -vf "scale=max(256\,2*round((256*iw/ih)/2)):-2" -c:a copy "${file%.*}_reduced.mp4"
    fi
done

# To check video size
for file in videos/*/*_reduced.mp4
do
    if grep -q _reduced <<< "$file"; then
        aux=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 $file)
        IFS='x' read -r size_width string <<< "$aux"
        if [ $((size_width%2)) -eq "1" ]; then
            echo $file
        fi
    fi
done
"""

import os
import json
import subprocess
from multiprocessing import Pool
from pathlib import Path

folder_dataset = 'dataset_info/finegym'
# for 'segment' the 'events' have to be already extracted.
# for 'stage' the 'segments' have to be already extracted (only with events could be enough if there is no case of
# stages in videos with more than one segment)
to_extract = 'event'  # ['event', 'segment', 'stage']


def main():
    with open(os.path.join(folder_dataset, 'annotations/finegym_annotation_info_v1.1.json'), 'r') as f:
        annotations = json.load(f)

    for folder_name in ['event_videos', 'stage_videos', 'action_videos']:
        folder_path = os.path.join(folder_dataset, folder_name)
        if not os.path.exists(folder_path): os.mkdir(folder_path)

    # To use multiprocessing pool, cancel the two lines below
    # pool = Pool(processes=50)
    # pool.map(process_video, annotations.items())

    # To not use multiprocessing pool, cancel the two lines below
    for item in annotations.items():
        # 2 videos that are all set and have actions and stages
        if item[0] in ["0LtLS9wROrk", "1Fdwuy2V9EY","1rkcLEAMTpw","1JsRXIoR3C0","2pBxfMAIaXY"]:
            # print(item)
            process_video(item)


def process_video(inputs):
    video_id, events = inputs
    timestamps = []
    paths_new = []
    paths_original = []
    path_original_video = os.path.join('videos', video_id, f'{video_id}_reduced.mp4')
    for event_id, event_data in events.items():
        event_label = event_data['event']
        event_timestamp = event_data['timestamps']
        name_clip = video_id + '_' + event_id
        path_clip = os.path.join(folder_dataset, 'event_videos', f'{name_clip}.mp4')
        
        # Extract video at level of "event"
        if to_extract == 'event':
            paths_original.append(path_original_video)
            paths_new.append(path_clip)
            timestamps.append(event_timestamp[0])
        
        # Extract video at level of "segment"
        elif to_extract == 'segment' and event_data['segments'] is not None:
            for segment_id, segment_data in event_data['segments'].items():
                name_subclip = video_id + '_' + event_id + '_' + segment_id
                path_subclip = os.path.join(folder_dataset, 'action_videos', f'{name_subclip}.mp4')
                # this is only to extract the clips with more than 1 stage that were extracted incorrectly before
                # if len(segment_data['timestamps']) > 1:
                paths_original.append(path_clip)
                paths_new.append(path_subclip)
                ts = segment_data['timestamps']
                timestamps.append([ts[0][0], ts[len(ts)-1][1]])
        
        # Extract video at level of "stage"
        elif to_extract == 'stage' and event_data['segments'] is not None:
            num_segments = len(event_data['segments'])
            for segment_id, stages in event_data['segments'].items():
                if stages['stages'] > 1:
                    # Check if there is any case where #segments > 1 and there is a segment with more than one stage.
                    # I think it never happens.
                    if num_segments > 1:
                        print(f'This case happens in event {event_id}, segment {segment_id}')
                    for k in range(stages['stages']):
                        name_clip = video_id + '_' + event_id
                        path_clip = os.path.join(folder_dataset, 'event_videos', f'{name_clip}.mp4')
                        name_subsubclip = video_id + '_' + event_id + '_' + segment_id + '_' + str(k)
                        path_subsubclip = os.path.join(folder_dataset, 'stage_videos', f'{name_subsubclip}.mp4')
                        paths_original.append(path_clip)
                        paths_new.append(path_subsubclip)
                        timestamps.append(stages['timestamps'][k])

    extract_video(paths_original, paths_new, timestamps)


def extract_video(paths_original, paths_new, timestamps):
    for path_original, path_new, timestamp in zip(paths_original, paths_new, timestamps):
        if os.path.isfile(path_original) and not (os.path.isfile(path_new) and Path(path_new).stat().st_size > 1000):
            # -y overwrites
            # Extract video from path_original to path_new at specific level using ffmpeg.
            instruction = f'ffmpeg -hwaccel cuda -y -hide_banner -loglevel error -i {path_original} -ss {timestamp[0]} -to {timestamp[1]} -c:v h264_nvenc -c:a copy {path_new}'
            subprocess.call(instruction, shell=True)
            print('Done:', os.path.basename(path_new))

if __name__ == '__main__':
    main()
