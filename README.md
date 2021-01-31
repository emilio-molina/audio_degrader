[![Build Status](https://travis-ci.com/emilio-molina/audio_degrader.svg?branch=master)](https://travis-ci.com/emilio-molina/audio_degrader)
[![PyPI version](https://badge.fury.io/py/audio-degrader.svg)](https://badge.fury.io/py/audio-degrader)
# audio_degrader

Latest version: `1.3.1`

Audio degradation toolbox in python, with a command-line tool. It is useful to apply controlled degradations to audio.


## Installation

`pip install audio-degrader`

The program depends on `pysox`, so you might need to install `sox` (and `libsox-fmt-mp3` for mp3 encoding). Go to https://github.com/rabitt/pysox to have more details about it.

## Available degradations

```
    convolution,impulse_response,level: Convolve input with specified impulse response
        parameters:
            impulse_response: Full path, URL (requires wget), or relative path (see -l option)
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
    mix,noise,snr: Mix input with a specified noise. The noise can be specified with its full path, URL (requires wget installed),  or relative to the resources directory (see -l option)
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
```

## Usage of python package
```Python
import audio_degrader as ad
audio_file = ad.AudioFile('input.wav', './tmp_dir')
for d in ad.ALL_DEGRADATIONS.values():
    print ad.DegradationUsageDocGenerator.get_degradation_help(d)
degradations = ad.ParametersParser.parse_degradations_args([
    'normalize',
    'gain,6',
    'dr_compression,3',
    'equalize,500,10,30'])
for d in degradations:
    audio_file.apply_degradation(d)
audio_file.to_wav('output.wav')
audio_file.delete_tmp_files()
```

## Usage of command-line tool

The script `audio_degrader` is installed along with the python package.

```
# e.g. mix with restaurant08.wav with snr=10db, then amplifies 6db, then compress dynamic range
$ audio_degrader -i input.mp3 -d mix,https://github.com/hagenw/audio-degradation-toolbox/raw/master/AudioDegradationToolbox/degradationData/PubSounds/restaurant08.wav,10 gain,6 dr_compression,3 -o out.wav

# for more details:
$ audio_degrader --help
```

A small set of sounds and impulse responses are installed along with the script, which can be listed with:
```
$ audio_degrader -l

# these relative paths can be used directly in the script too:
$ audio_degrader -i input.mp3 -d mix,sounds/applause.wav,-3 gain,6 -o out.wav
```


## Applications
* Evaluate Music Information Retrieval systems under different degrees of degradations
* Prepare augmented data for training of machine learning systems

It is similar to the [Audio Degradation Toolbox in Matlab by Sebastian Ewert and Matthias Mauch][1] (for Matlab).


## Some examples

```
# Mix input with a sound / noise (e.g. using installed resources)
$ audio_degrader -i input.wav -d mix,sounds/applause.wav,-3 -o out.wav


# Instead of paths, we can also use URLs
$ audio_degrader -i input.wav -d mix,https://www.pacdv.com/sounds/ambience_sounds/airport-security-1.mp3,-3 -o out.wav


# Microphone recording style
$ audio_degrader -i input.wav -d gain,-15 mix,sounds/ambience-pub.wav,18 convolution,impulse_responses/ir_smartphone_mic_mono.wav,0.8 dr_compression,2 equalize,50,100,-6 normalize -o out.wav


# Resample and normalize
$ audio_degrader -i input.mp3 -d resample,8000 normalize -o out.wav


# Convolution (again impulse responses can be resources, full paths or URLs)
$ audio_degrader -i input.wav -d convolution,impulse_responses/ir_classroom_mono.wav,0.7 -o out.wav
$ audio_degrader -i input.wav -d convolution,http://www.cksde.com/sounds/month_ir/FLANGERSPACE%20E001%20M2S.wav,0.7 -o out.wav
```

## Audio formats

### Input
`audio_degrader` relies on ffmpeg for audio reading, so it can read any format (even video).

### Output
`audio_degrader` output format is always wav stereo `pcm_f32le` (sample rate from original audio file).

This output wav file can be easily coverted into another format with ffmpeg, e.g.:
```
$ ffmpeg -i out.wav -b:a 320k out.mp3
$ ffmpeg -i out.wav -ac 2 -ar 44100 -acodec pcm_s16le out_formatted.wav
```


[1]: https://code.soundsoftware.ac.uk/projects/audio-degradation-toolbox
