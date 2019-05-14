# Public Speaking Feedback Tool

###Wellesley cs349 Natural Language Processing - Final Project (Spring 2016)

####Elizabeth Hau & Emily Ahn

[Project write-up](https://docs.google.com/document/d/11ngIBgPLcDaetmm4vspy42Xs7gXQ7gaqcx6F-Bvmqyk/edit?usp=sharing)
### Goal & Motivation
Public speaking can be challenging and nerve-wracking, but having good speaking skills for giving presentations and disseminating ideas is both essential and practical. People often unknowingly use filler words such as “umm”, “uhh”, or “like” while giving presentations, and it would be good to make them more aware of how often they use these words. This is a program that would analyze a given speech and count the number of filler words used, provided the filler words the program should look for in the speech. The goal of this project is to build a tool that could provide feedback to people as they try to improve their public speaking skills. 


### The files
- `utils.py`: Allows users to record themselves using the microphone of their local computer and saves the recorded file as 'demo.wav' in the data directory. 
- `speech_to_text.py`: Given an audio file, runs the CMUSphinx decoder, which generates transcriptions for the files and writes the hypotheses to a file in the `data/hyp_test` directory. If run in single file mode, also compares the transcription with the gold standard and displays a short message to the user.
- `analyze_text.py`: Assuming we already have the transcriptions, read the hypotheses, process it and report the results.

### Data
- `data/`: directory containing recordings of our own speech to test the system + 2 directories: `hyp_ted` and `hyp_test`
- `data/hyp_ted`: TED talks: directory containing transcriptions of 10 TED talks, ~20 minutes each, 5 male, 5 female, varying age, gender, and topic
- `data/hyp_test`: directory containing transcriptions of recordings of our own speech

## To run the program

1. **Create an audio file**
  
    (can skip this step if already have a 16000 Hz mono-channel file)

  Running `utils.py` will start recording your speech using your local computer's microphone. The recording stops either when the user hits the 'Enter' key or has been silent for a long period of time (i.e. if continuous silence time > SILENT_THRESHOLD)
    <blockquote>
        python utils.py
  </blockquote>
  The recording should be saved as `demo.wav` in the `data` directory
  
2. **Obtain transcriptions**
  
  Run `speech_to_text.py` with one of the following commands:
    
    1. Batch mode: 
      
        <blockquote>`python speech_to_text.py` </blockquote>
        runs the decoder on all files in the default data directory (ignoring directories such as `hyp_ted` and `hyp_test`) and throws an error if a file is not in correct format (e.g. there is a text file in `data/`)
    2. Single file mode: 
        
        <blockquote>`python speech_to_text.py filename`</blockquote> assumes the file name provided is in the default data directory and

        <blockquote>`python speech_to_text.py datadir filename`</blockquote> assumes the first argument is the data directory and the second is the file name
    
  Running `speech_to_text.py` gets the transcriptions of the files and stores them in `data/hyp_test`. If ran in single mode, `speech_to_text.py` also reports the number and percentage of filler words said in the speech, compares it with the gold standard, and displays a short message.
  
  The feedback on filler words upon running `speech_to_text.py` should be displayed in the terminal (only in single file mode) as follows in this sample output.
   
  ````
    ************* RESULTS ****************
    total_words: 53
    number of  [SPEECH] said: 4
    percent of filler words 0.0754716981132
    compared to TED standard frequency of filler words (0.005589%)...
    Keep practicing! You still use too many filler words
    ````
    

3. **Batch feedback**

  If you already have the transcription(s) of the file(s), run <blockquote>`python analyze_text.py hypdir`</blockquote> to get feedback on all the hypotheses files in the directory containing all these files. This program also assumes that `hypdir` contains only text files that are the hypotheses (i.e. .txt files in the correct format). 
  
  An example feedback on some files displayed in the terminal: 
  
  ````
  *********** FILE:  hypothesis-demo1.txt ****************
  total_words: 53
  number of  [SPEECH] said: 4
  percent of filler words 0.0754716981132
  compared to TED standard frequency of filler words (0.005589%)...
  Keep practicing! You still use too many filler words
  total_words: 73
  number of  <sil> said: 18
  percent of filler words 0.246575342466
  compared to TED standard frequency of filler words (0.005589%)...
  Keep practicing! You still use too many filler words
  % of "um"s said (['SPEECH']) 0.0754716981132
  % of "<sil>" 0.246575342466
  file is: hypothesis-ar_1_16000.txt
  
  *********** FILE:  hypothesis-ar_1_16000.txt ****************
  total_words: 48
  number of  [SPEECH] said: 3
  percent of filler words 0.0625
  compared to TED standard frequency of filler words (0.005589%)...
  Keep practicing! You still use too many filler words
  total_words: 63
  number of  <sil> said: 12
  percent of filler words 0.190476190476
  compared to TED standard frequency of filler words (0.005589%)...
  Keep practicing! You still use too many filler words
  % of "um"s said (['SPEECH']) 0.0625
  % of "<sil>" 0.190476190476
  file is: hypothesis-demo1_converted.txt
  ````
  
