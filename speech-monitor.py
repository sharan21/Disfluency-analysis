import pyaudio
from queue import Queue
import sys
import time
from matplotlib import pyplot as plt
import numpy as np
from keras.models import Model, load_model, Sequential
import matplotlib.mlab as mlab
from utils import storeWavFile
from pydub import AudioSegment
from pydub.silence import split_on_silence
from utils import getNumberOfFiles


chunk_duration = 0.5 # Each read length in seconds from mic.
fs = 44100 # sampling rate for mic
chunk_samples = int(fs * chunk_duration) # Each read length in number of samples.

# Each model input data duration in seconds, need to be an integer numbers of chunk_duration
feed_duration = 10 # the input size for the model
feed_samples = int(fs * feed_duration)
DEFAULT_CHUNKNAME = './chunks/chunk{}.wav'

frames = []
writing = False
fileOffset = getNumberOfFiles()


assert feed_duration/chunk_duration == int(feed_duration/chunk_duration)

model = load_model('./models/tr_model.h5')


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


def get_spectrogram(data):
    """
    Function to compute a spectrogram.

    Argument:
    predictions -- one channel / dual channel audio data as numpy array

    Returns:
    pxx -- spectrogram, 2-D array, columns are the periodograms of successive segments.
    """
    nfft = 200  # Length of each window segment
    fs = 8000  # Sampling frequencies
    noverlap = 120  # Overlap between windows
    nchannels = data.ndim
    if nchannels == 1:
        pxx, _, _ = mlab.specgram(data, nfft, fs, noverlap=noverlap)
    elif nchannels == 2:
        pxx, _, _ = mlab.specgram(data[:, 0], nfft, fs, noverlap=noverlap)
    return pxx


def plt_spectrogram(data):
    """
    Function to compute and plot a spectrogram.

    Argument:
    predictions -- one channel / dual channel audio data as numpy array

    Returns:
    pxx -- spectrogram, 2-D array, columns are the periodograms of successive segments.
    """
    nfft = 200  # Length of each window segment
    fs = 8000  # Sampling frequencies
    noverlap = 120  # Overlap between windows
    nchannels = data.ndim
    if nchannels == 1:
        pxx, _, _, _ = plt.specgram(data, nfft, fs, noverlap=noverlap)
    elif nchannels == 2:
        pxx, _, _, _ = plt.specgram(data[:, 0], nfft, fs, noverlap=noverlap)
    return pxx


def detect_triggerword_spectrum(x):
    """
    Function to predict the location of the trigger word.

    Argument:
    x -- spectrum of shape (freqs, Tx)
    i.e. (Number of frequencies, The number time steps)

    Returns:
    predictions -- flattened numpy array to shape (number of output time steps)
    """
    # the spectogram outputs  and we want (Tx, freqs) to input into the model
    x = x.swapaxes(0, 1)
    x = np.expand_dims(x, axis=0)
    predictions = model.predict(x)
    return predictions.reshape(-1)


def has_new_triggerword(predictions, chunk_duration, feed_duration, threshold=0.5):
    """
    Function to detect new trigger word in the latest chunk of input audio.
    It is looking for the rising edge of the predictions data belongs to the
    last/latest chunk.

    Argument:
    predictions -- predicted labels from model
    chunk_duration -- time in second of a chunk
    feed_duration -- time in second of the input to model
    threshold -- threshold for probability above a certain to be considered positive

    Returns:
    True if new trigger word detected in the latest chunk
    """
    predictions = predictions > threshold
    chunk_predictions_samples = int(len(predictions) * chunk_duration / feed_duration)
    chunk_predictions = predictions[-chunk_predictions_samples:]
    level = chunk_predictions[0]
    for pred in chunk_predictions:
        if pred > level:
            return True
        else:
            level = pred
    return False



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

            frames = []

        return (in_data, pyaudio.paContinue)

    else:
        # print('writing')
        sys.stdout.write('.')
        frames.append(in_data)


        writing = True



    # splitWavFileAndStore(filename)



    # if len(data) > feed_samples: # this line only runs when there is fresh data greater than 10 seconds
    #
    #     data = data[-feed_samples:]
    #
    #
    #
    #
    #     # Process data async by sending a queue.
    #     q.put(data)

    return (in_data, pyaudio.paContinue)


if __name__ == '__main__':

    # Queue to communicate between the audio callback and main thread
    q = Queue()

    run = True

    silence_threshold = 100  # not in db

    # Run the demo for a timeout seconds
    timeout = time.time() + 0.5 * 60  # 0.5 minutes from now

    # Data buffer for the input wavform
    data = np.zeros(feed_samples, dtype='int16')

    stream = get_audio_input_stream(callback)  # creates the PyAudio() instance with callback function
    # every time
    stream.start_stream()

    try:
        while run:

            data = q.get()  # FIFO

            print(run)

            # # he uses spectrum data to make preds
            # spectrum = get_spectrogram(data)
            # # preds = detect_triggerword_spectrum(spectrum)
            #
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


