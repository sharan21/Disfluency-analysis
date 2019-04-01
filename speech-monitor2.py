import pyaudio
import sys
import time
import numpy as np
from queue import Queue
from keras.models import Model, load_model, Sequential, model_from_json

from pydub import AudioSegment
from pydub.silence import split_on_silence
from utils import *


chunk_duration = 0.1
fs = 44100
chunk_samples = int(fs * chunk_duration)

DEFAULT_CHUNKNAME = './chunks/chunk{}.wav'

frames = []

pauseduration = []
pausetemp = 0

wordduration = []
wordtemp = 0

silencenow = False


fileOffset = getNumberOfFiles('./chunks')

run = True

timestart = time.time()
duration = 10



def get_audio_input_stream(callback):
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=fs,
        input=True,
        frames_per_buffer=chunk_samples,
        input_device_index=0,
        stream_callback=callback)
    return stream




def splitWavFileAndStore(filename, minsillen= 60, silthresh = -60):

    line = AudioSegment.from_wav(filename)

    audio_chunks = split_on_silence(line, min_silence_len=minsillen, silence_thresh=silthresh)  # isolation of words is done here

    rejectedOffset = 0

    for i, chunk in enumerate(audio_chunks): # audio_chunks is a python list



        out_file = DEFAULT_CHUNKNAME.format(i+fileOffset)
        # print("size of chunk{}: {} ".format(i+fileOffset, len(chunk)))
        # print ("exporting", out_file)
        chunk.export(out_file, format="wav")
        # print("done exporting...")

    # print("Total number of files:", i+1)

    return i+1



def callback(in_data, frame_count, time_info, status): # also responsible for putting the data into the queue

    # in_data is each chunk corresponding to 0.5 sec size

    global run, duration, timestart, silencenow, wordtemp, pausetemp, wordduration, pauses


    if (time.time() - timestart) > duration: # stream will continue till timeout is invoked
        if silencenow:
            wordduration.append(time.time() - wordtemp)

        run = False

    data_new = np.frombuffer(in_data, dtype='int16')
    frames.append(in_data)


    if np.abs(data_new).mean() < silence_threshold: # find the mean of the chunk for that small duration
        sys.stdout.write('-')
        if not silencenow:
            silencenow = True
            # start counting
            wordtemp = time.time()


        return (in_data, pyaudio.paContinue)

    else:
        sys.stdout.write('.')

        if silencenow:
            silencenow = False
            wordduration.append(time.time()-wordtemp)








    return (in_data, pyaudio.paContinue)






if __name__ == '__main__':


    # model = loadmodel('./models/average9.json', './models/average9.h5')

    silence_threshold = 100

    stream = get_audio_input_stream(callback)


    while run:
        continue

    wordduration.pop()

    storeWavFile(frames, './sentences/testing.wav')

    splitWavFileAndStore('./sentences/testing.wav')

    print(wordduration)

    stream.stop_stream()
    stream.close()


