[![Build Status](https://travis-ci.org/EliosMolina/audio_degrader.svg?branch=master)](https://travis-ci.org/EliosMolina/audio_degrader)
# audio_degrader

This tool allows to introduce controlled degradations to audio.

## Installation

`pip install audio_degrader`

The program depends on `sox`, `ffmpeg` and `rubberband`, so you might need to install them as well. Recommended `brew` in OSX and `apt-get` in linux (for rubberband, in linux use rubberband-cli).

## Applications
* Evaluate Music Information Retrieval systems under different degrees of degradations
* Prepare augmented data for training of machine learning systems

It is similar to the [Audio Degradation Toolbox in Matlab by Sebastian Ewert and Matthias Mauch][1] (for Matlab).


## Usage

The script `audio_degrader` is installed along with the python package.

```
$ audio_degrader --help
usage: audio_degrader [-h] [-i INPUT] [-t TMPDIR]
                      [-d [degradation,params [degradation,params ...]]]
                      [-o OUTPUT] [-l] [-v VERBOSITY_LEVEL]

Process audio with a sequence of degradations:
    convolution,impulse_response,level: Convolve input with specified impulse response
        parameters:
            impulse_response: Full or relative path (to resources dir) of impulse response
            level: Wet level (0.0=dry, 1.0=wet)
        example:
            convolution,impulse_responses/ir_classroom.wav,1.0
    dr_compression,degree: Apply dynamic range compression
        parameters:
            degree: Degree of compression. Presets from 0 (soft) to 3 (hard)
        example:
            dr_compression,0
    equalize,central_freq,bandwidth,gain: Apply a two-pole peaking equalisation (EQ) filter
        parameters:
            central_freq: Central frequency of filter in Hz
            bandwidth: Bandwith of filter in Hz
            gain: Gain of filter in dBs
        example:
            equalize,100,50,-10
    gain,value: Apply gain expressed in dBs
        parameters:
            value: Gain value [dB]
        example:
            gain,6
    mix,noise,snr: Mix input with a specified noise. The noise can be specified with its full path or relative to the resources directory (see -l option)
        parameters:
            noise: Full or relative path (to resources dir) of noise
            snr: Desired Signal-to-Noise-Ratio [dB]
        example:
            mix,sounds/ambience-pub.wav,6
    mp3,bitrate: Emulate mp3 transcoding
        parameters:
            bitrate: Quality [bps]
        example:
            mp3,320k
    normalize: Normalize amplitude of audio to range [-1.0, 1.0]
        parameters:
        example:
            normalize
    pitch_shift,pitch_shift_factor: Apply pitch shifting
        parameters:
            pitch_shift_factor: Pitch shift factor
        example:
            pitch_shift,0.9
    resample,sample_rate: Resample to given sample rate
        parameters:
            sample_rate: Desired sample rate [Hz]
        example:
            resample,8000
    speed,speed: Change playback speed
        parameters:
            speed: Playback speed factor
        example:
            speed,0.9
    time_stretch,time_stretch_factor: Apply time stretching
        parameters:
            time_stretch_factor: Time stretch factor
        example:
            time_stretch,0.9
    trim_from,start_time: Trim audio from a given start time
        parameters:
            start_time: Trim start [seconds]
        example:
            trim_from,0.1

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input audio wav
  -t TMPDIR, --tmpdir TMPDIR
                        Temporal directory. Default: ./audio_degrader_tmp
  -d [degradation,params [degradation,params ...]], --degradations [degradation,params [degradation,params ...]]
                        List of sequential degradations
  -o OUTPUT, --output OUTPUT
                        Output audio wav
  -l, --list-resources  List all available resources
  -v VERBOSITY_LEVEL, --verbosity_level VERBOSITY_LEVEL
                        Options: ERROR, WARNING, INFO, DEBUG. Default: WARNING

For examples of degradations see https://github.com/EliosMolina/audio_degrader
```

In addition, a set of sounds and impulse reponses are also installed along with the package:

```
$ audio_degrader -l
Available resources
Directory: /Users/emiliomolina/git/audio_degrader/audio_degrader/resources
  impulse_responses/ir_classroom_mono.wav
  impulse_responses/ir_smartphone_mic_mono.wav
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
# Mix input sound with a sound / noise
# note: sounds/applause.wav is relative path with respect to installed
# resources files. A full absolute path can be also used.

$ audio_degrader -i input.wav -d mix,sounds/applause.wav,-3 -o out.wav


# Microphone recording style

$ audio_degrader -i input.wav -d gain,-15 mix,sounds/ambience-pub.wav,18 convolution,impulse_responses/ir_smartphone_mic_mono.wav,0.8 dr_compression,2 equalize,50,100,-6 normalize -o out.wav


# Resample and normalize
$ audio_degrader -i input.wav -d resample,8000 normalize -o out.wav


# Convolution
# note: impulse_responses/ir_classroom_mono.wav is relative to the installed resources files
$ audio_degrader -i input.wav -d convolution,impulse_responses/ir_classroom_mono.wav,0.7 -o out.wav
```

## Audio format

### Input
`audio_degrader` relies on ffmpeg for audio reading, so it can read any format (even video).

### Output
`audio_degrader` output format is always wav stereo pcm_f32le (sample rate from original audio file).

In order to convert this output wav file into another format, it can be easily done with ffmpeg. e.g.:
```
$ ffmpeg -i out.wav -b:a 320k out.mp3
$ ffmpeg -i out.wav -ac 2 -ar 44100 -acodec pcm_s16le out_formatted.wav

```


[1]: https://code.soundsoftware.ac.uk/projects/audio-degradation-toolbox
