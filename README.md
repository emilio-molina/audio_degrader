[![Build Status](https://travis-ci.org/EliosMolina/audio_degrader.svg?branch=master)](https://travis-ci.org/EliosMolina/audio_degrader)
# audio_degrader

Latest version: `1.2.3`

Audio degradation toolbox in python, with a command-line tool. It is useful to apply controlled degradations to audio.


## Installation

`pip install audio_degrader`

The program depends on `sox`, `ffmpeg` and `rubberband`, so you might need to install them as well. Recommended `brew` in OSX and `apt-get` in linux (for rubberband, in linux use `rubberband-cli`).


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
