# Beat detection using Parselmouth (Jadoul, Thompson, & de Boer 2018)
# Andrew Lamont
# Summer 2021

# call with python 3
# args: file name, tempo of song in bpm, number of beats per measure, (optional: number of beats +/- to offset the downbeat by)

import sys
import parselmouth
import textgrid #http://github.com/kylebgorman/textgrid/

# file name of song
song = sys.argv[1]

# set tempo of song
beats_per_minute = float(sys.argv[2])

# set how many beats per measure
beats_per_measure = int(sys.argv[3])

# set how many quarter notes to offset the downbeats
offset = 0
if len(sys.argv) == 5:
	offset = float(sys.argv[4])

# open the wav file
snd = parselmouth.Sound(song)

# the file's duration in milliseconds
snd_length = snd.get_total_duration() * 1000

# get intensity profile, time step is a millisecond
# whole spectrum, >5000 Hz, <500 Hz
intensity = snd.to_intensity(time_step = .001)
upper_intensity = snd.to_intensity(time_step = .001, minimum_pitch = 5000)
lower_intensity = snd.to_intensity(time_step = .001, minimum_pitch = 500)

# iterate through microtempos
best_bpm = -1

bpm = beats_per_minute - 0.99
while bpm < beats_per_minute + 1:
	# how many milliseconds between downbeats
	measure_duration = (60000 / bpm) * beats_per_measure

	# iterate through milliseconds that could start a measure looking for maximum intensity
	# exclude first and last 15 seconds
	best_downbeat = -1
	best_intensity = -1
	downbeat = 15000
	while downbeat < (measure_duration + 15000):
		total_intensity = 0.0
		db = downbeat
		total_downbeats = 0
		while db < snd_length - 15000:
			# intensity below 500 Hz
			lower = intensity.get_value(db/1000) - lower_intensity.get_value(db/1000)
			# intensity above 5000 Hz
			upper = upper_intensity.get_value(db/1000)
			total_intensity += lower + upper
#			total_intensity += intensity.get_value(db/1000)
			db += measure_duration
			total_downbeats += 1
		average_intensity = total_intensity / total_downbeats
		if average_intensity > best_intensity:
			best_downbeat = downbeat
			best_intensity = total_intensity
			if best_bpm != bpm:
				best_bpm = bpm
		downbeat += 1

	bpm += 0.01

measure_duration = (60000 / best_bpm) * beats_per_measure
print('Best BPM:', best_bpm)

if offset:
	best_downbeat += (offset / beats_per_measure) * measure_duration
if best_downbeat < 0:
	best_downbeat += measure_duration

# create interval tiers for subdivisions
measures   = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'measure')
halves     = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'half')
quarters   = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'quarter')
eighths    = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'eighth')
sixteenths = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'sixteenth')

# create interval tiers for annotation
metrics = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'metric text')
micros = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'micro-timed text')

# add subdivision annotations
m_onset = (best_downbeat - 15000) / 1000
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
