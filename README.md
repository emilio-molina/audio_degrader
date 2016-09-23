# audio_degrader.py

This tool allows to introduce controlled degradations to audio.

Applications:
* evaluate Music Information Systems under different degrees of degradations
* prepare augmented data for training of machine learning systems

It is similar to the [Audio Degradation Toolbox in Matlab by Sebastian Ewert and Matthias Mauch][1], but simpler, and in python. I'm using it for creating my own synthetic datasets.

### Temporary limitation:
For the moment, it only works with .WAV files with codec `pcm_s16le` (16 bits .WAV) and sample rate of 8KHz. I don't need more for myself, but I will try to extended for any sample rate in the short-term.

## Degradations available
* mp3 compression
* gain
* normalization
* add background noise: [white-noise,
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
usage: python audio_degrader.py [-h] [--testing]
                      input_wav [degradation,value [degradation,value ...]]
                      output_wav

Process audio with a sequence of degradations
    Accepted degradadations:
        mp3,quality: Mp3 compression. Value is quality (1-5)
        gain,db: Gain. Value is dB (e.g. gain,-20.3).
        normalize,percentage: Normalize. Percentage in 0.0-1.0 (1.0=full range)
        white-noise,snr: Add white noise. SNR in dB.
        brown-noise,snr: Add brown noise. SNR in dB.
        ambience-pub,snr: Add pub ambience. SNR in dB.
        vinyl,snr: Add vinyl noise. SNR in dB.
        hum,snr: Add hum noise. SNR in dB.
        applause,snd: Add applause noise. SNR in dB.
        smartphone_mic,level: Smartphone_mic-like sonority. Level 0.0-1.0
        classroom,level: Classroom-like reverb. Level 0.0-1.0
        dr-compression,degree: Dynamic range compression. Degree in (1-3).
        time-stretching,ratio: Apply time streting. Ratio in from -9.99 to 9.99
        pitch-shifting,ratio: Apply time streting. Ratio in -9.99 to 9.99
        eq,freq_hz/bw_hz/gain_db: Apply equalization with sox.
        

positional arguments:
  input_wav          Input audio wav
  degradation,value  List of sequential degradations
  output_wav         Output audio wav

optional arguments:
  -h, --help         show this help message and exit
  --testing          Output audio wav

Note: all audios are transcoded to mono, 8KHz, pcm_s16le
```

### Examples
```
$ python audio_degrader.py test.wav gain,-15 ambience-pub,6 dr-compression,3 mp3,1 gain,15 out.wav
```

### Dependencies

* [`librosa`][2] for audio processing in python. Just install it with `pip install librosa`
* [`sox`][3] for audio processing via command line. Just install it with `apt-get install sox` in Linux or `brew install sox` in OSX.
* [`rubberband`][4] for time stretchign and pitch shifting. Install it with `apt-get install rubberband-cli` or `brew install rubberband`.
* [`ffmpeg`][5] for transcoding. Install it `apt-get install ffmpeg` in Linux or `brew install ffmpeg` in OSX.
[1]: https://code.soundsoftware.ac.uk/projects/audio-degradation-toolbox
[2]: https://github.com/librosa/librosa
[3]: http://sox.sourceforge.net/sox.html
[4]: http://breakfastquay.com/rubberband/
[5]: https://www.ffmpeg.org/
