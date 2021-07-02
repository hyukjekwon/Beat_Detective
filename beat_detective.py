# Beat detection using Parselmouth (Jadoul, Thompson, & de Boer 2018)
# Andrew Lamont
# June 2021

# call with python 3
# args: file name, tempo of song in bpm, number of beats per measure

import sys
import parselmouth
import textgrid #http://github.com/kylebgorman/textgrid/

# file name of song
song = sys.argv[1]

# set tempo of song
beats_per_minute = int(sys.argv[2])

# set how many beats per measure
beats_per_measure = int(sys.argv[3])

# how many milliseconds between downbeats
measure_duration = int((60000.0 / beats_per_minute) * beats_per_measure)

# open the wav file
snd = parselmouth.Sound(song)

# the file's duration in milliseconds
snd_length = int(snd.get_total_duration() * 1000)

# get intensity profile, time step is a millisecond
intensity = snd.to_intensity(time_step = .001)

# iterate through milliseconds that could start a measure looking for maximum intensity
best_downbeat = -1
best_intensity = -1
for downbeat in range(measure_duration):
	total_intensity = 0.0
	for db in range(downbeat, snd_length, measure_duration):
		total_intensity += intensity.get_value(db/1000)
	if total_intensity > best_intensity:
		best_downbeat = downbeat
		best_intensity = total_intensity

# create interval tiers for subdivisions
measures = textgrid.IntervalTier(maxTime = snd_length/1000)

# add subdivision annotations
for db in range(best_downbeat, snd_length, 2*measure_duration):
	downbeats.addInterval(textgrid.Interval(db/1000, db/1000 + measure_duration,''))

# turn into a text grid
tg = textgrid.TextGrid(maxTime = snd_length/1000)
tg.append(measures)

# write TextGrid file
tg.write(song + '.TextGrid')
