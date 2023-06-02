# beat detection using librosa

import librosa
import textgrid
import sys

argc = len(sys.argv)
fname = sys.argv[1]
quarter_offset = 0 if argc <= 2 else int(sys.argv[2])
tightness = 1024 if argc <= 3 else int(sys.argv[3])
# higher tightness => more uniform interval length

# beat detection
y, sr = librosa.load(fname)
duration = librosa.get_duration(y=y, sr=sr)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, tightness=tightness)
print('Estimated tempo: {:.2f} beats per minute'.format(tempo))
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

# division + writing to TextGrid file
tg = textgrid.TextGrid(fname.replace('.wav', ''), 0, duration)
itvl_lengths = []
metric_dict = {'measure': [], 'half': [], 'quarter': [], 'eighth': [], 'sixteenth': []}
for i, time in list(enumerate(beat_times))[:-1]:
    next_time = beat_times[i+1]
    dur = next_time - time
    itvl_lengths.append(dur)
    metric_dict['quarter'].append(time)
    if i % 2 == quarter_offset % 2:
        metric_dict['half'].append(time)
    if i % 4 == quarter_offset % 4:
        metric_dict['measure'].append(time)
    eighths, sixteenths = [], []
    for i in range(4):
        interp_time = time + (dur * (i / 4))
        if i % 2 == 0:
            eighths.append(interp_time)
        sixteenths.append(interp_time)
    metric_dict['eighth'] += eighths
    metric_dict['sixteenth'] += sixteenths
    
for div in metric_dict:
    grid = metric_dict[div]
    tier = textgrid.IntervalTier(div, 0, duration)
    for i, time in list(enumerate(grid))[:-1]:
        itvl = textgrid.Interval(time, grid[i+1], '')
        tier.addInterval(itvl)
    tg.append(tier)

print(f'Min/max interval length: {min(itvl_lengths)} / {max(itvl_lengths)}')

f = open(fname.replace('wav', 'TextGrid'), 'w')
tg.write(f)
f.close()
