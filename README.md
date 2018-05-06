[![Build Status](https://travis-ci.org/EliosMolina/audio_degrader.svg?branch=master)](https://travis-ci.org/EliosMolina/audio_degrader)
# audio_degrader.py

This tool allows to introduce controlled degradations to audio.

Applications:
* evaluate Music Information Systems under different degrees of degradations
* prepare augmented data for training of machine learning systems

It is similar to the [Audio Degradation Toolbox in Matlab by Sebastian Ewert and Matthias Mauch][1], but simpler, and in python. I'm using it for creating my own synthetic datasets.

### Temporary limitation:
For the moment, it only works with .WAV files with codec `pcm_s16le` (16 bits .WAV).

## Degradations available
* mp3 compression
* gain
* normalization
* add background noise: e.g. [white-noise,
                              brown-noise,
                              ambience-pub,
                              old-vinyl,
                              hum,
                              applause]
* apply smartphone-like distortion
* apply classroom reverb
* apply dynamic range compression
* apply time-stretching
* apply pitch-shifting
* apply equalization

All of them can be combined sequentially in the specified order.

## Usage

```
usage: audio_degrader.py [-h]
                         input_wav [degradation,value [degradation,value ...]]
                         output_wav

Process audio with a sequence of degradations
    Accepted degradadations:
        start,time: Remove audio until start. Value in seconds.
        mp3,quality: Mp3 compression. Value is quality (1-5)
        gain,db: Gain. Value is dB (e.g. gain,-20.3).
        normalize,percentage: Normalize. Percentage in 0.0-1.0 (1.0=full range)
        mix,"sound_path"//snr: Mix with sound at a specified SNR
        impulse-response,"impulse_response_path"//level: Apply impulse response
                                                         Level 0.0-1.0
        dr-compression,degree: Dynamic range compression. Degree 1,2 or 3.
        time-stretching,ratio: Apply time streting.
        pitch-shifting,cents: Apply pitch shifting.
        eq,freq_hz//bw_hz//gain_db: Apply equalization with sox.


positional arguments:
  input_wav          Input audio wav
  degradation,value  List of sequential degradations
  output_wav         Output audio wav

optional arguments:
  -h, --help         show this help message and exit

Note: all audios are transcoded to mono, pcm_s16le
```

### Examples
```
$ python audio_degrader.py test.wav gain,-15 ambience-pub,6 dr-compression,3 mp3,1 gain,15 out.wav
```
