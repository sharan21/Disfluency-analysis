import time
import sys
from pydub import AudioSegment
from pydub.silence import split_on_silence
from utils import storeWavFile, getNumberOfFiles
import pyaudio
import numpy as np
from modules.get_words import startRecording, storeWavFile, checkChunk
from pydub import AudioSegment
from pydub.silence import split_on_silence
import subprocess
from modules.get_mfcc import *
import os
from modules.get_mfcc import absoluteFilePaths
from modules.normalize_data import normalizeSoundData

__author__ = 'Sharan Narasimhan'

''' *************************** fluencymetric.py ******************************
    This file allows users to record themselves using the microphone of
    their local computer and saves the recorded file, splits it into its 
    correspondind words and counts the number of disfluencies present. 
    It then optioanlly saves the results
     into a logs.txt file.
    *******************************************************************
'''

class recorder:
    '''
    this class can record audio, store it, isolate words, and measure pause durations
    It first records the sentence then splits it
    '''

    def __init__(self, name='recorder', duration=10):

        print("object initialised...")

        self.instancename = name
        self.mfccarray = []
        self.simthresh = 100
        self.chunk_duration = 0.1
        self.fs = 44100
        self.chunk_samples = int(self.fs * self.chunk_duration)
        self.DEFAULT_CHUNKNAME = './chunks/chunk{}.wav'
        self.frames = []
        self.pausedurations = []
        self.wordtemp = 0
        self.silencenow = False
        self.silence_threshold = 100
        self.fileOffset = getNumberOfFiles('./chunks')
        self.run = True
        self.pathtochunks = './chunks'
        self.pathlist = []
        self.timestart = time.time()
        self.duration = duration

        # self.pathforsentences = './sentences/class1.wav'
        self.pathforsentences = './data/demo.wav'
        self.frames = []
        self.wordmatches = []


        #thresholds
        self.pausethresh = 0.5

        #disfluencies
        self.repetitions = 0
        self.blockages = 0

        # stats
        self.wordcount = 0
        self.wordlist = []
        self.disfluency = 0.0


    def __del__(self):
        print("deleting")
        # subprocess.call('./empty_temp.sh')
        print('deleted chunks')


    def getmfccarray(self):
        print("finding mfccs for words in './chunks")
        self.mfccarray = mfccarray(self.pathtochunks)


    def get_audio_input_stream(self):
        stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.fs,
            input=True,
            frames_per_buffer=self.chunk_samples,
            input_device_index=0,
            stream_callback=self.callback)
        return stream


    def splitWavFileAndStore(self, filename, minsillen=60, silthresh=-60):
        line = AudioSegment.from_wav(filename)

        audio_chunks = split_on_silence(line, min_silence_len=minsillen,
                                        silence_thresh=silthresh)  # isolation of words is done here

        rejectedOffset = 0

        for i, chunk in enumerate(audio_chunks):  # audio_chunks is a python list


            out_file = self.DEFAULT_CHUNKNAME.format(i + self.fileOffset)
            # print("size of chunk{}: {} ".format(i+fileOffset, len(chunk)))
            # print ("exporting", out_file)
            chunk.export(out_file, format="wav")
            # print("done exporting...")

        # print("Total number of files:", i+1)

        return i + 1


    def callback(self, in_data, frame_count, time_info, status):


        if (time.time() - self.timestart) > self.duration:  # stream will continue till timeout is invoked
            if self.silencenow:
                self.pausedurations.append(time.time() - self.wordtemp)

            self.run = False

            # self.pausedurations.pop()

        data_new = np.frombuffer(in_data, dtype='int16')
        self.frames.append(in_data)

        if np.abs(data_new).mean() < self.silence_threshold:  # find the mean of the chunk for that small duration
            sys.stdout.write('-')
            if not self.silencenow:
                self.silencenow = True
                # start counting
                self.wordtemp = time.time()

            return (in_data, pyaudio.paContinue)

        else:
            sys.stdout.write('.')

            if self.silencenow:
                self.silencenow = False
                self.pausedurations.append(time.time() - self.wordtemp)

        return (in_data, pyaudio.paContinue)

    def buildstatistics(self):

        print("building statistics on last 10 seconds...")
        print("{}% fluency in your speech".format(self.llratio * 100))

    def savestatistics(self):

        print("saving stats into the disk")
        f = open("./logs/stats.txt", "a")
        f.write("Name of Instance : '{}' \n".format(self.instancename))
        f.write("")

    def analyse(self):

        print("analysing the chunks in './chunks...")

        self.pathlist = [path for path in absoluteFilePaths(recorder.pathtochunks) if(path != '.DS_Store')]
        # self.pathlist.remove([path for path in self.pathlist if 'chunk1.wav' in path][0])
        print("path list is {}".format(self.pathlist))
        recorder.mfccarray = getndimMfcc(recorder.pathlist)
        print("asserting that all chunks have equal no. of coefficients")
        assert ([ele for ele in [len(mfcc) for mfcc in recorder.mfccarray]].count(20) == len(recorder.mfccarray))
        print("TRUE!")

        # for i in range(len(recorder.mfccarray)-1):
        #     print("distance between word {} and word {}: ".format(i + 1, i + 2))
        #     computeDistace(recorder.mfccarray[i], recorder.mfccarray[i + 1])

        self.wordcount = len(self.mfccarray)
        self.wordlist = np.arange(self.wordcount)
        print("initial wordlist is {}".format(self.wordlist))


        for i in range(len(self.wordlist)):
            if(self.wordlist[i] != i):
                continue
            for j in range(i,len(self.wordlist),1):
                if(i is j):
                    continue
                print("distanc btw sound {} and {} is {}".format(i,j,computeDistace(self.mfccarray[i], self.mfccarray[j])))
                if(computeDistace(self.mfccarray[i], self.mfccarray[j]) <= self.simthresh):
                    print("found similar words!")
                    self.wordlist[j] = i

                print("wordlist is {}".format(self.wordlist))
            print("final wordlist is {}".format(self.wordlist))

    def countrepetitons(self):
        for i in range(len(self.wordlist)-1):
            if(self.wordlist[i+1]==self.wordlist[i]):
                self.repetitions += 1
        print("number of continuous repetitions: {}".format(self.repetitions))


    def countblockages(self):
        self.blockages = len([ele for ele in self.pausedurations if(ele >= self.pausethresh)])
        print("number of blockages is {}".format(self.blockages))


    def writestats(self):

        self.disfluency = float(self.repetitions + self.blockages)/float(self.wordcount)

        print("saving stats into the disk")

        f = open("./logs/stats.txt", "a")

        f.write("No of Blocks:{} No of Reps: {} Word Count: {} Disfluency Ratio: {} \n".format(self.blockages, self.repetitions, self.wordcount, self.disfluency))


if __name__ == '__main__':



    list = absoluteFilePaths("./data")

    recorder = recorder('rec', 8)

    # stream = recorder.get_audio_input_stream()
    #
    # while recorder.run:
    #     continue
    #
    # stream.stop_stream()
    # stream.close()
    #
    # storeWavFile(recorder.frames, recorder.pathforsentences)

    start = time.time()

    for l in list:


        recorder.splitWavFileAndStore(l)

        print(recorder.pausedurations)

        recorder.analyse()

        #find and count disfluencies
        recorder.countrepetitons()
        recorder.countblockages()
        recorder.writestats()


        subprocess.call('./empty_temp.sh')

    end = time.time()

    print('time elapsed:', (end - start))

    os.system("python3 speech_to_text.py")











