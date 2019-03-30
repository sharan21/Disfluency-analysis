import pyaudio
import sys
import time
import numpy as np
import subprocess
from queue import Queue
# from keras.models import Model, load_model, Sequential, model_from_json

from pydub import AudioSegment
from pydub.silence import split_on_silence
from utils import *


chunk_duration = 0.05 # Each read length in seconds from mic.
fs = 44100 # sampling rate for mic
chunk_samples = int(fs * chunk_duration) # Each read length in number of samples.

DEFAULT_CHUNKNAME = './chunks/chunk{}.wav'

frames = []


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

    global run, duration, timestart


    if (time.time() - timestart) > duration: # stream will continue till timeout is invoked
        run = False

    data_new = np.frombuffer(in_data, dtype='int16')
    frames.append(in_data)


    if np.abs(data_new).mean() < silence_threshold: # find the mean of the chunk for that small duration
        sys.stdout.write('-')

        return (in_data, pyaudio.paContinue)

    else:
        sys.stdout.write('.')


    return (in_data, pyaudio.paContinue)




if __name__ == '__main__':

    # Queue to communicate between the audio callback and main thread

    model = loadmodel()


    silence_threshold = 100  # not in db



    stream = get_audio_input_stream(callback)  # creates the PyAudio() instance with callback function
    stream.start_stream()


    while run:
        continue

    storeWavFile(frames, './sentences/testing.wav')

    splitWavFileAndStore('./sentences/testing.wav')



    stream.stop_stream()
    stream.close()


