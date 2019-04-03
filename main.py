from recorder import speechmonitor
from analyser import stuttermonitor
import time
from modules.get_words import storeWavFile


timenow = time.time()


if __name__ == '__main__':

    print('running main...')


    for i in range(10):

        recorder = speechmonitor('mainrecorder', 10)
        sentence = stuttermonitor('sentence{}'.format(i+1))

        stream = recorder.get_audio_input_stream()

        while recorder.run:
            continue

        # from utils.py
        storeWavFile(recorder.frames, './sentences/testing.wav')

        recorder.splitWavFileAndStore('./sentences/testing.wav')

        print(recorder.wordduration)

        # takes chunks from chunks dir
        sentence.buildstatistics()
        sentence.savestatistics()

        del sentence

    stream.stop_stream()
    stream.close()
