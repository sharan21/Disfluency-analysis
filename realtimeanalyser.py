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
writing = False


# subprocess.call('./empty_temp.sh')

fileOffset = getNumberOfFiles('./test')

q = Queue()


# model = load_model('./models/tr_model.h5')


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

    return i+1



def callback(in_data, frame_count, time_info, status): # also responsible for putting the data into the queue

    # in_data is each chunk corresponding to 0.5 sec size

    global run, timeout, data, silence_threshold, fileOffset, writing, frames


    if time.time() > timeout:
        run = False
    data_new = np.frombuffer(in_data, dtype='int16')


    if np.abs(data_new).mean() < silence_threshold:
        sys.stdout.write('-')
        writing = False

        if (writing == False) and (len(frames) != 0):  # if not writing and data is non empty, store in wav file

            filename = './test/test' + str(fileOffset) + '.wav'
            fileOffset = fileOffset + 1

            storeWavFile(frames, filename)

            data = average(findMfcc(filename))
            q.put(data)



            frames = []

        return (in_data, pyaudio.paContinue)

    else:
        # print('writing')
        sys.stdout.write('.')
        frames.append(in_data)
        writing = True


    # splitWavFileAndStore(filename)

    return (in_data, pyaudio.paContinue)


if __name__ == '__main__':


    # model = loadmodel('./models/average9.json', './models/average9.h5')

    run = True

    silence_threshold = 100  # not in db

    # Run the demo for a timeout seconds
    timeout = time.time() + 2 * 60  # 2 minutes from now

    # Data buffer for the input wavform

    stream = get_audio_input_stream(callback)
    stream.start_stream()

    try:
        while True:

            data = q.get() # blocking mode
            # n = normalize(data)
            # print(n)
            # predictsingle(model,n)


    except (KeyboardInterrupt, SystemExit):
        stream.stop_stream()
        stream.close()
        timeout = time.time()
        run = False

    stream.stop_stream()
    stream.close()


