import pyaudio
import wave
import numpy as np
import math
import os
import scipy

# these constants are used to simplify specifying a default argument for below functions while importing

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
status = True

p = pyaudio.PyAudio()

def startRecording(seconds = RECORD_SECONDS):
    frames = []

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("* recording")

    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    return frames





def storeWavFile(frames, filename, verbosity = True):

    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(p.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    print ("Done recording, stored in output.wav") if verbosity else 0


def db_to_float(db, using_amplitude=True):
    """
    Converts the input db to a float, which represents the equivalent
    ratio in power.
    """
    db = float(db)
    if using_amplitude:
        return 10 ** (db / 20)
    else:  # using power
        return 10 ** (db / 10)

def getNumberOfFiles(path = './samples'):
    list = os.listdir(path)  # dir is your directory path
    number_files = len(list)

    # print ("Number of Files found in all_chunks:", number_files-1)
    return number_files

def detectnoiselevel(seconds = 5): # in dBFS

    print ("detecting noise level...")
    print ("recording for {} seconds".format(seconds))

    frames = startRecording(seconds)
    storeWavFile(frames, './chunks')

    data = importAllFromDir('./temp')

    print (20*math.log10(np.mean(data)/32767))


def importAllFromDir(path):

    list = os.listdir(path)

    if '.DS_Store' in list:
        list.remove('.DS_Store')

    print ("There are {} chunks in directory {}".format(len(list), path))

    sounddata = []

    for i in range(len(list)):

        rate, data = scipy.io.wavfile.read(path+'/'+list[i])

        # rectifies sound signal
        sounddata.append(np.absolute(data))

    return sounddata




if __name__ == '__main__':
    print(("main"))

    detectnoiselevel(3)

