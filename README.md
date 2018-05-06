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
usage: audio_degrader [-h] [--in-wav IN_WAV]
                      [--degradations [degradation,value [degradation,value ...]]]
                      [--out-wav OUT_WAV] [--list-resources]

Process audio with a sequence of degradations
    Accepted degradadations:
        start,time: Remove audio until start. Value in seconds.
        mp3,quality: Mp3 compression. Value is quality (1-5)
        gain,db: Gain. Value is dB (e.g. gain,-20.3).
        normalize,percentage: Normalize. Percentage in 0.0-1.0 (1.0=full range)
        mix,"sound_path"//snr: Mix with sound at a specified SNR.
                               See --list-resources to check installed sounds.
        impulse-response,"impulse_response_path"//level: Apply impulse response
                                                         Level 0.0-1.0
                                See --list-resources to check installed sounds.
        dr-compression,degree: Dynamic range compression. Degree 1,2 or 3.
        time-stretching,ratio: Apply time streting.
        pitch-shifting,cents: Apply pitch shifting.
        eq,freq_hz//bw_hz//gain_db: Apply equalization with sox.


optional arguments:
  -h, --help            show this help message and exit
  --in-wav IN_WAV       Input audio wav
  --degradations [degradation,value [degradation,value ...]]
                        List of sequential degradations
  --out-wav OUT_WAV     Output audio wav
  --list-resources      List all available resources

Note: all audios are transcoded to mono, pcm_s16le
```

In addition, a set of sounds and impulse reponses are also installed along with the package:

```
$ audio_degrader --list-resources
Available resources
(see 'mix' and 'impulse-response' degradations):
  /Library/Python/2.7/site-packages/audio_degrader/resources/impulse_responses/ir_classroom.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/impulse_responses/ir_smartphone_mic.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/ambience-pub.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/applause.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/brown-noise.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/debate1.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/debate2.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/helen.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/hum.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/vinyl.wav
  /Library/Python/2.7/site-packages/audio_degrader/resources/sounds/white-noise.wav
```

## Example

```
$ audio_degrader --in-wav test30s_44100_mono_pcm16le.wav --degradations gain,-15 mix,"/Library/Python/2.7/site-packages/audio_degrader/resources/sounds/ambience-pub.wav"//12 dr-compression,3 mp3,1 gain,15 --out-wav out.wav
```


[1]: https://code.soundsoftware.ac.uk/projects/audio-degradation-toolbox