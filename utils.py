import pyaudio
import wave
import numpy as np
import math
import os
import librosa
import scipy
from keras.models import model_from_json

# these constants are used to simplify specifying a default argument for below functions while importing

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
status = True
pathtojson = './models/model.json'
pathtoh5 = './models/model.h5'

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

def importmfccfromdir(path = './samples'):

    '''

    :param path: the directory that contains the audio chunks to convert
    :return: a numpy nd array with each row containing the average mfcc for each word in dir
    '''

    list = absoluteFilePaths(path)
    data = []


    for file in list:
        mfcc = average(findMfcc(file))
        # deltah = delta(mfcc)
        #temp = np.concatenate((mfcc, deltah))
        data.append(mfcc)
    return np.array(data)


def diff(a, b): # a-b
    b = set(b)
    return [item for item in a if item not in b]



def absoluteFilePaths(directory):
   for dirpath,_,filenames in os.walk(directory):
       if ('.DS_Store' in filenames):
        filenames.remove('.DS_Store')
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))



def average(mfcc):
    # take an n coefficient mfcc for multiple samples and finds its nx1 size average array
    # print ("averaging mfcc")
    ave = []
    for i in range(mfcc.shape[0]):
        ave.append(np.mean(mfcc[i,:]))
    ave_numpy = np.array(ave)
    # print (ave_numpy)

    return ave_numpy



def predict(model, data):


    # print("shape of data {}".format(data.shape))

    classes = model.predict(data)

    # instance = model.predict(data)


    # print("done predicting, printing")

    for instance in classes:
        print(instance)
        print(parseinstance(instance))

    # print(parseinstance(instance))

def predictsingle(model, data):

    data = np.expand_dims(data, axis=0)
    instance = model.predict(data)
    print(instance.shape)

    print(parse_singleinstance(instance))





def loadmodel(pathjson = pathtojson, pathh5 = pathtoh5):

    print("using model: {}".format(pathtojson))

    # load json and create model
    json_file = open(pathtojson, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # load weights into new model

    loaded_model.load_weights(pathtoh5)
    print("Loaded model from disk")

    loaded_model.compile(loss='categorical_crossentropy',
                         optimizer='adam',
                         metrics=['accuracy'])

    print("compiled the loaded model with cat. cross entropy with adam optim...")

    return loaded_model



def parseinstance(instance):
    return "ll" if instance[1] > instance[0] else "nonll"


def parse_singleinstance(instance):
    return "ll" if instance[0, 1] > instance[0, 0] else "nonll"


def normalizeall(soundDataHere):

    '''

    :param soundDataHere: takes a list of numpy arrays (row wise)
    :return: returns the normalised list
    '''

    print("normalizing the sound data, for {} files".format(len(soundDataHere)))

    for i in range(len(soundDataHere)):
        print("normalizing the sound data, for {}st chunk".format(i))
        mean = np.mean(soundDataHere[i])
        std = np.std(soundDataHere[i])
        soundDataHere[i] = (soundDataHere[i] - mean) / std
        print("done")

    return soundDataHere

def normalize(data):
    """

    :param data: takes a 1d numpy array
    :return: its normalised version
    """

    mean = np.mean(data)
    std = np.std(data)

    n = (data - mean) / std


    return np.array(n)


def findMfcc(path):
    y1, sr1 = librosa.load(path)
    mfcc = librosa.feature.mfcc(y1, sr1)
    return mfcc



if __name__ == '__main__':



    model = loadmodel(pathtojson, pathtoh5)

    data = importmfccfromdir()
    print(data.shape)
    normalizeall(data)

    predict(model, data)


    # print(("main"))
    #
    # a = ['a', 'b', 'c']
    # b = ['a', 'b', 'c', 'd', 'e']
    #
    # print(diff(b,a))


