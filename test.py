import pyaudio
import wave
import numpy as np
import math
from matplotlib import pyplot as plt
import time
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
RECORD_SECONDS = 3
minimumWordSize = 300  # if the size of the word is <= this, reject the chunk
maximumWordSize = 2000

status = True





def startRecording(seconds = RECORD_SECONDS):
    frames = []

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)


    t = 0
    temp = []
    timenow = time.time()


    while time.time() - timenow < 5: # 5 seconds duration
        print("* recording")
        frames.clear()
        for i in range(0, int(RATE / CHUNK * seconds)):
            data = stream.read(CHUNK)
            temp.append(np.mean(np.fromstring(stream.read(CHUNK), dtype=np.int16)))
            # print(len(temp))
            # print(temp)

            frames.append(data)
            # print(data)

        print ("finished")

        storeWavFile(frames, './test'+str(t)+'.wav')
        t = t+1
        plt.plot(temp)
        plt.show()


    print("done ")




    stream.stop_stream()
    stream.close()
    p.terminate()





def storeWavFile(frames, filename):

    waveFile = wave.open(filename, 'wb')

    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(p.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)

    waveFile.writeframes(b''.join(frames))

    waveFile.close()

    print("Done recording, stored in output.wav")


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


if __name__ == '__main__':

    startRecording()