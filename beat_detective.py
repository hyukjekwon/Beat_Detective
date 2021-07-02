# Beat detection using Parselmouth (Jadoul, Thompson, & de Boer 2018)
# Andrew Lamont
# June 2021

# call with python 3
# args: file name, tempo of song in bpm, number of beats per measure, (optional: number of beats +/- to offset the downbeat by)

import sys
import parselmouth
import textgrid #http://github.com/kylebgorman/textgrid/

# file name of song
song = sys.argv[1]

# set tempo of song
beats_per_minute = int(sys.argv[2])

# set how many beats per measure
beats_per_measure = int(sys.argv[3])

# set the offset
offset = 0
if len(sys.argv) == 5:
	offset = int(sys.argv[4])

# open the wav file
snd = parselmouth.Sound(song)

# the file's duration in milliseconds
snd_length = snd.get_total_duration() * 1000

# get intensity profile, time step is a millisecond
intensity = snd.to_intensity(time_step = .001)

# how many milliseconds between downbeats
measure_duration = (60000 / beats_per_minute) * beats_per_measure

# iterate through milliseconds that could start a measure looking for maximum intensity
best_downbeat = -1
best_intensity = -1
downbeat = 0
while downbeat < measure_duration:
	total_intensity = 0.0
	db = downbeat
	while db < snd_length:
		total_intensity += intensity.get_value(db/1000)
		total_intensity -= high_intensity.get_value(db/1000)
		db += measure_duration
	if total_intensity > best_intensity:
		best_downbeat = downbeat
		best_intensity = total_intensity
	downbeat += 1

if offset:
	best_downbeat += (offset / beats_per_measure) * measure_duration
if best_downbeat < 0:
	best_downbeat += measure_duration

# create interval tiers for subdivisions
measures = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'measure')
halves = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'half')
quarters = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'quarter')
eighths = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'eighth')
sixteenths = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'sixteenth')

# create interval tiers for annotation
metrics = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'metric text')
micros = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'micro-timed text')

# add subdivision annotations
m_onset = best_downbeat / 1000
while m_onset < (snd_length - measure_duration) / 1000:
	m_dur = measure_duration / 1000

	measures.addInterval(textgrid.Interval(m_onset, m_onset + m_dur, ''))

	for i in range(2):
		halves.addInterval(textgrid.Interval(m_onset + (i/2) * m_dur, m_onset + ((i+1)/2) * m_dur, ''))

	for i in range(4):
		quarters.addInterval(textgrid.Interval(m_onset + (i/4) * m_dur, m_onset + ((i+1)/4) * m_dur, ''))

	for i in range(8):
		eighths.addInterval(textgrid.Interval(m_onset + (i/8) * m_dur, m_onset + ((i+1)/8) * m_dur, ''))

	for i in range(16):
		sixteenths.addInterval(textgrid.Interval(m_onset + (i/16) * m_dur, m_onset + ((i+1)/16) * m_dur, ''))

	m_onset += m_dur

# add to a text grid
tg = textgrid.TextGrid(maxTime = snd_length/1000)
tg.append(measures)
tg.append(halves)
tg.append(quarters)
tg.append(eighths)
tg.append(sixteenths)
tg.append(metrics)
tg.append(micros)

# write TextGrid file
tg.write(song + '.TextGrid')
