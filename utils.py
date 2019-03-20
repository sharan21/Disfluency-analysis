import pyaudio
import wave
import numpy as np
import math
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
status = True

p = pyaudio.PyAudio()




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


if __name__ == '__main__':
    print(("main"))

