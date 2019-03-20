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


subprocess.call('./remove-chunks.sh')

fileOffset = getNumberOfFiles()



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

    # print("Total number of files:", i+1)

    return i+1



def callback(in_data, frame_count, time_info, status): # also responsible for putting the data into the queue

    # in_data is each chunk corresponding to 0.5 sec size

    global run, timeout, data, silence_threshold, fileOffset, writing, frames



    if time.time() > timeout: # stream will continue till timeout is invoked
        run = False
    data_new = np.frombuffer(in_data, dtype='int16')


    if np.abs(data_new).mean() < silence_threshold: # find the mean of the chunk for that small duration
        sys.stdout.write('-')
        writing = False

        if (writing == False) and (len(frames) != 0):  # if not writing and data is non empty, store in wav file

            # get new filename
            # print("saving")
            filename = './samples/test' + str(fileOffset) + '.wav'
            fileOffset = fileOffset + 1

            storeWavFile(frames, filename, False)

            #get mfcc of the file just saves and predict


            # stream.stop_stream()

            data = average(findMfcc(filename))
            q.put(data)



            # print(data)
            # data = normalize(data)
            # print(data)

            # predictsingle(model, data)


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

    # Queue to communicate between the audio callback and main thread

    model = loadmodel()

    run = True

    silence_threshold = 100  # not in db

    # Run the demo for a timeout seconds
    timeout = time.time() + 2 * 60  # 2 minutes from now

    # Data buffer for the input wavform

    stream = get_audio_input_stream(callback)  # creates the PyAudio() instance with callback function
    # every time
    stream.start_stream()

    try:
        while True:

            data = q.get()
            n = normalize(data)
            # print(n)
            predictsingle(model,n)



            # new_trigger = has_new_triggerword(preds, chunk_duration, feed_duration)
            #
            # if new_trigger:
            #     sys.stdout.write('1')

    except (KeyboardInterrupt, SystemExit):
        stream.stop_stream()
        stream.close()
        timeout = time.time()
        run = False

    stream.stop_stream()
    stream.close()


