import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import glob, os
import numpy as np
import matplotlib.pyplot as plt

class Segment(object):
	def __init__(self, interval, speakers):
		self.interval = interval
		self.speakers = speakers[:]
	def __repr__(self):
		return "{} {}".format(self.interval, self.speakers)


def unionSpeakerIntervals(speakerStarts, speakerEnds):
	trackingSpeakers = []
	startInterval = 0
	endInterval = 0
	uniqueSpeakerSegments = []

	speakerStarts.sort(key = lambda x: x[1])
	speakerEnds.sort(key= lambda x: x[1])

	while len(speakerStarts) != 0 or len(speakerEnds) != 0:
		if len(speakerStarts) == 0:
			nextEnd = speakerEnds[0][1]
			nextStart = nextEnd + 1
		elif len(speakerEnds) == 0:
			nextStart = speakerStarts[0][1]
			nextEnd = nextStart + 1
		else:
			nextEnd = speakerEnds[0][1]
			nextStart = speakerStarts[0][1]
		
		#is the next boundary point a start or an end of an interval
		if nextStart < nextEnd:
			#next boundary point is at the start of an interval
			#save the unique segment up until this point
			endInterval = nextStart

			uniqueSpeakerSegments.append(Segment((startInterval, endInterval), trackingSpeakers[:]))
			
			#begin tracking new speaker
			newSpeaker = speakerStarts.pop(0)
			#print("Start: {}".format(newSpeaker))
			trackingSpeakers.append(newSpeaker[0])
			
			#update starting point of new interval
			startInterval = nextStart
		else:
			#next boundary point is at the end of the interval
			endInterval = nextEnd
			#save unique segment up until this point
			uniqueSpeakerSegments.append(Segment((startInterval, endInterval), trackingSpeakers[:]))
			#stop tracking speaker that had endInterval
			endingSpeaker = speakerEnds.pop(0)
			try:
				trackingSpeakers.remove(endingSpeaker[0])
			except:
				print('error')
			startInterval = nextEnd

	return uniqueSpeakerSegments

os.chdir("../segments")
count = 0

speakerStarts = defaultdict(list)
speakerEnds = defaultdict(list)

#overlap detection only on the 2012a
for file in glob.glob("[A-Z][A-Z][0-9][0-9][0-9][0-9][a-z].?.segments.xml"):
	p = re.compile(r"\.([A-Z])\.")
	pPart = re.compile(r"([A-Z][A-Z][0-9][0-9][0-9][0-9][a-z])\.")
	speakerLabel = p.search(file).group(1)
	part = pPart.search(file).group(1)
	#speakers[speakerLabel] = []
	tree = ET.parse(file)
	root = tree.getroot()
	
	for child in root:
		start_time = float(child.attrib['transcriber_start'])
		end_time = float(child.attrib['transcriber_end'])
		speakerStarts[part].append((speakerLabel,start_time))
		speakerEnds[part].append((speakerLabel, end_time))



sum = [0] * 6
sumTotal = 0
sumOverlap = 0
num = 0

overlapDurations = []
for part in speakerStarts:
	for timeslice in unionSpeakerIntervals(speakerStarts[part][:], speakerEnds[part][:]):
			sum[len(timeslice.speakers)] += timeslice.interval[1] - timeslice.interval[0]
			if len(timeslice.speakers) > 1:
				sumOverlap += timeslice.interval[1] - timeslice.interval[0]
				overlapDurations.append(timeslice.interval[1] - timeslice.interval[0])
				num += 1

mybins = np.arange(0,5,0.2)
hist, bins = np.histogram(overlapDurations, bins=mybins)
bin_counts = zip(bins, bins[1:], hist)
for bin_start, bin_end, count in bin_counts:
    print('{:0.1f}-{:0.1f}: {}'.format(bin_start, bin_end, count))




averageOverLap = sumOverlap/num
singleRatio = sum[1] / (sum[1] + sum[2] + sum[3] + sum[4])
overlapRatio =  (sum[2] + sum[3] + sum[4]+ sum[5])/ (sum[1] + sum[2] + sum[3] + sum[4]+ sum[5])
twoOverlapRatio = sum[2]/(sum[1] + sum[2] + sum[3] + sum[4]+ sum[5])
threeOverlapRatio = sum[3]/(sum[1] + sum[2] + sum[3] + sum[4]+ sum[5])
fourOverlapRatio = sum[4]/(sum[1] + sum[2] + sum[3] + sum[4]+ sum[5])
fiveOverlapRatio = sum[5]/(sum[1] + sum[2] + sum[3] + sum[4] + sum[5])
print("Single Speaker Ratio: {}".format(singleRatio))
print("Two Overlapped Ratio: {}".format(twoOverlapRatio))
print("Three Overlapped Ratio: {}".format(threeOverlapRatio))
print("Four Overlapped Ratio: {}".format(fourOverlapRatio))
print("Five Overlapped Ratio: {}".format(fiveOverlapRatio))
print("Average Overlap length: {}".format(averageOverLap))

plt.hist(overlapDurations , cumulative=True, normed="true", bins=mybins, histtype='bar', ec='black')
plt.xlim([0, 5])
plt.xlabel("overlap duration (s)")
plt.ylabel("density")
plt.title("Cumulative Distribution of Overlapping Durations")
plt.show()

plt.hist(overlapDurations , normed="true", bins=mybins, histtype='bar', ec='black')
plt.xlim([0, 5])
plt.title("Distribution of Overlapping Durations")
plt.xlabel("overlap duration (s)")
plt.ylabel("density")
plt.show()
