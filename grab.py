#!/usr/bin/python

# grab.py - Grab frames from videos with ffmpeg.
# Copyright (C) 2017  Adam Monsen <haircut@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

 
# Grabs frames from videos with ffmpeg. Use multiple cores.
# Minimum resolution is 1 second--this is a shortcut to get less frames.
 
 
import json
import subprocess
from multiprocessing import Pool
import os
 
frameList = []
 
def isWithinSuturingSegment(annotations, timepointSeconds):
    for annotation in annotations:
        startSeconds = annotation['startSeconds']
        endSeconds = annotation['endSeconds']
        if timepointSeconds > startSeconds and timepointSeconds < endSeconds:
            return True
    return False
 
with open('available-suturing-segments.json') as f:
    j = json.load(f)
 
    for video in j:
        videoId = video['videoId']
        videoDuration = video['durationSeconds']
 
        # generate many ffmpeg frame-grabbing commands
        start = 1
        stop = videoDuration
        step = 4 # Reduce to grab more frames
        for timepointSeconds in xrange(start, stop, step):
            inputFilename = '/home/adam/Downloads/suturing-videos/{}.mp4'.format(videoId)
            outputFilename = '{}-{}.jpg'.format(video['videoId'], timepointSeconds)
            if isWithinSuturingSegment(video['annotations'], timepointSeconds):
                outputFilename = 'suturing/{}'.format(outputFilename)
            else:
                outputFilename = 'not-suturing/{}'.format(outputFilename)
            outputFilename = '/home/adam/local/{}'.format(outputFilename)
 
            commandString = 'ffmpeg -loglevel quiet -ss {} -i {} -frames:v 1 {}'.format(
                timepointSeconds, inputFilename, outputFilename)
 
            frameList.append({
                'outputFilename': outputFilename,
                'commandString': commandString,
            })
 
def grabFrame(f):
    if os.path.isfile(f['outputFilename']):
        print 'already completed {}'.format(f['outputFilename'])
    else:
        print 'processing {}'.format(f['outputFilename'])
        subprocess.check_call(f['commandString'].split())
 
p = Pool(4) # for my 4-core laptop
p.map(grabFrame, frameList)
