# Beat detection using Parselmouth (Jadoul, Thompson, & de Boer 2018)
# Original code framework by Andrew Lamont
# "Dumb" edits made by Hyuk-Je Kwon
# Summer 2021
​
# call with python 3
# args: file name, flattened tempo of song in bpm, first prominent downbeat, last prominent downbeat
​
import sys
import parselmouth
import textgrid #http://github.com/kylebgorman/textgrid/
​
# file name of song
song = sys.argv[1]
​
# set flattened tempo of song (i.e. if 85.0, 85.5, or 85.9 bpm => input should be 85)
bpm_flat = int(sys.argv[2])
​
# set the first prominent downbeat of the song
t1 = float(sys.argv[3])
​
# set the last prominent downbeat of the song
t2 = float(sys.argv[4])
​
# open the wav file
snd = parselmouth.Sound(song)
​
# the file's duration in milliseconds
snd_length = snd.get_total_duration() * 1000
​
# how many milliseconds between each downbeat
measure_duration = 240000 / bpm_flat
​
# get total milliseconds between first downbeat and last downbeat
total_metric_length = 1000 * (t2 - t1)
​
# find the total number of measures between the first and last downbeat
num_measures = int(metric_length / measure_duration)
​
# use the number of measures to get a more accurate measure duration
true_measure_dur = total_metric_length / num_measures
​
# calculate the new bpm by using the true measure duration
true_bpm = 240000 / true_measure_dur
​
# create interval tiers for subdivisions
measures = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'measure')
halves = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'half')
quarters = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'quarter')
eighths = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'eighth')
sixteenths = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'sixteenth')
​
# create interval tiers for annotation
metrics = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'metric text')
micros = textgrid.IntervalTier(maxTime = snd_length/1000, name = 'micro-timed text')
​
# add subdivision annotations
m_onset = first_downbeat
while m_onset < (snd_length - true_measure_dur) / 1000:
	m_dur = true_measure_dur / 1000
​
	measures.addInterval(textgrid.Interval(m_onset, m_onset + m_dur, ''))
​
	for i in range(2):
		halves.addInterval(textgrid.Interval(m_onset + (i/2) * m_dur, m_onset + ((i+1)/2) * m_dur, ''))
​
	for i in range(4):
		quarters.addInterval(textgrid.Interval(m_onset + (i/4) * m_dur, m_onset + ((i+1)/4) * m_dur, ''))
​
	for i in range(8):
		eighths.addInterval(textgrid.Interval(m_onset + (i/8) * m_dur, m_onset + ((i+1)/8) * m_dur, ''))
​
	for i in range(16):
		sixteenths.addInterval(textgrid.Interval(m_onset + (i/16) * m_dur, m_onset + ((i+1)/16) * m_dur, ''))
​
	m_onset += m_dur
​
# add to a text grid
tg = textgrid.TextGrid(maxTime = snd_length/1000)
tg.append(measures)
tg.append(halves)
tg.append(quarters)
tg.append(eighths)
tg.append(sixteenths)
tg.append(metrics)
tg.append(micros)
​
# write TextGrid file
tg.write(song + '.TextGrid')
​
# print new bpm
print('The new bpm is ' + true_bpm)
