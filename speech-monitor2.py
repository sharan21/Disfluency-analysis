import pyaudio
import sys
import time
import numpy as np
from keras.models import Model, load_model, Sequential, model_from_json

from stutteranalyser import stutteranalyser
import sys

from pydub import AudioSegment
from pydub.silence import split_on_silence
from utils import *



class speechmonitor:

    def __init__(self):
        print("hello")

        self.chunk_duration = 0.1
        self.fs = 44100
        self.chunk_samples = int(self.fs * self.chunk_duration)

        self.DEFAULT_CHUNKNAME = './chunks/chunk{}.wav'

        self.frames = []

        self.pauseduration = []
        self.pausetemp = 0

        self.wordduration = []
        self.wordtemp = 0

        self.silencenow = False
        self.silence_threshold = 100

        self.fileOffset = getNumberOfFiles('./chunks')

        self.run = True

        self.pathtochunks = './chunks'

        self.timestart = time.time()
        self.duration = 10




    def __del__(self):
        print("deleting")


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


    def predict(self):

        # print ("Importing Averages Mfccs...")
        data = librosaMfcc(self.pathforchunks)
        data = normalizeSoundData(data)
        # print data

        classes = loadandpredict(self.pathtomodeljson, self.pathtomodelh5, data)

        return classes

    def statistics(self):

        print ("building statistics on last 10 seconds...")

        classes = self.predict()
        self.wordcount = float(len(classes))

        self.llcount = float(len([classes[i] for i in range(len(classes)) if(classes[i,0] < classes[i,1])]))

        self.nonllcount = self.wordcount - self.llcount
        self.llratio = self.llcount/self.wordcount


        self.status= True if self.llratio > 0.8 else False

        print("{}% fluency in your speech".format(self.llratio*100))






    def callback(self, in_data, frame_count, time_info, status):  # also responsible for putting the data into the queue

        # in_data is each chunk corresponding to 0.5 sec size

        # global run, duration, timestart, silencenow, wordtemp, pausetemp, wordduration, pauses

        if (time.time() - self.timestart) > self.duration:  # stream will continue till timeout is invoked
            if self.silencenow:
                self.wordduration.append(time.time() - self.wordtemp)

            self.run = False

            self.wordduration.pop()

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
                self.wordduration.append(time.time() - self.wordtemp)

        return (in_data, pyaudio.paContinue)



if __name__ == '__main__':

    s = speechmonitor()
    sentence = stutteranalyser()

    stream = s.get_audio_input_stream()

    while s.run:
        continue


    storeWavFile(s.frames, './sentences/testing.wav')

    s.splitWavFileAndStore('./sentences/testing.wav')

    print(s.wordduration)

    stream.stop_stream()
    stream.close()

    sentence.statistics()





