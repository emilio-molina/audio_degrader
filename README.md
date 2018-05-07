[![Build Status](https://travis-ci.org/EliosMolina/audio_degrader.svg?branch=master)](https://travis-ci.org/EliosMolina/audio_degrader)
# audio_degrader

This tool allows to introduce controlled degradations to audio.

## Installation

`pip install audio_degrader`

The program depends on `sox` and `ffmpeg`, so you might need to install them as well.

## Applications
* Evaluate Music Information Retrieval systems under different degrees of degradations
* Prepare augmented data for training of machine learning systems

It is similar to the [Audio Degradation Toolbox in Matlab by Sebastian Ewert and Matthias Mauch][1] (for Matlab).


## Usage

The script `audio_degrader` is installed along with the python package.

```
$ audio_degrader
usage: audio_degrader [-h] [-i INPUT]
                      [-d [degradation,value [degradation,value ...]]]
                      [-o OUTPUT] [-l]

Process audio with a sequence of degradations
    Accepted degradadations:
        start,time: Remove audio until start. Value in seconds.
        mp3,quality: Mp3 compression. Value is quality (1-5)
        gain,db: Gain. Value is dB (e.g. gain,-20.3).
        normalize,percentage: Normalize. Percentage in 0.0-1.0 (1.0=full range)
        mix,"sound_path"//snr: Mix with sound at a specified SNR.
                               See --list-resources option.
        impulse-response,"impulse_response_path"//level: Apply impulse response
                                                         Level 0.0-1.0
                               See --list-resources option.
        dr-compression,degree: Dynamic range compression. Degree 1,2 or 3.
        time-stretching,ratio: Apply time streting.
        pitch-shifting,cents: Apply pitch shifting.
        eq,freq_hz//bw_hz//gain_db: Apply equalization with sox.


optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input audio wav
  -d [degradation,value [degradation,value ...]], --degradations [degradation,value [degradation,value ...]]
                        List of sequential degradations
  -o OUTPUT, --output OUTPUT
                        Output audio wav
  -l, --list-resources  List all available resources

Note: all audios are transcoded to mono, pcm_s16le

Example:
    audio_degrader -i input.wav -d gain,-15 mix,"sounds/ambience-pub.wav"//12 dr-compression,3 mp3,1 gain,15 -o output.wav
```

In addition, a set of sounds and impulse reponses are also installed along with the package:

```
$ audio_degrader -l
Available resources
Directory: /Users/emiliomolina/git/audio_degrader/audio_degrader/resources
  impulse_responses/ir_classroom.wav
  impulse_responses/ir_smartphone_mic.wav
  sounds/ambience-pub.wav
  sounds/applause.wav
  sounds/brown-noise.wav
  sounds/debate1.wav
  sounds/debate2.wav
  sounds/helen.wav
  sounds/hum.wav
  sounds/vinyl.wav
  sounds/white-noise.wav
```

## Examples

```
# Microphone recording style

$ audio_degrader -i input.wav -d gain,-15 mix,"sounds/ambience-pub.wav"//18 impulse-response,"impulse_responses/ir_smartphone_mic.wav"//0.8 dr-compression,2 eq,50//100//-6 gain,6 -o out.wav
```


[1]: https://code.soundsoftware.ac.uk/projects/audio-degradation-toolbox