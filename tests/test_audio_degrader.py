import os
import librosa as lr
import numpy as np
from audio_degrader import mix_with_sound, convolve, ffmpeg, lame, apply_gain
from audio_degrader import apply_rubberband

TEST_STEREO_WAV_PATH = './tests/test_files/test30s_44100_stereo_pcm16le.wav'
TEST_MONO_WAV_PATH = './tests/test_files/test30s_44100_mono_pcm16le.wav'


class TestMono:

    def setup_class(self):
        pass

    def test_ffmpeg(self):
        ffmpeg(TEST_MONO_WAV_PATH,
               TEST_MONO_WAV_PATH + '.ffmpeg.wav')

    def test_mix_with_sound_mono(self):
        x, sr = lr.core.load(TEST_MONO_WAV_PATH, sr=None, mono=False)
        y = mix_with_sound(x, sr, './sounds/white-noise.wav', -6)
        lr.output.write_wav(
            TEST_MONO_WAV_PATH + '.wnoise-6.wav',
            y, sr=sr, norm=False)
        y = mix_with_sound(x, sr, './sounds/white-noise.wav', 20)
        lr.output.write_wav(
            TEST_MONO_WAV_PATH + '.wnoise20.wav',
            y, sr=sr, norm=False)

    def test_convolve_mono(self):
        x, sr = lr.core.load(TEST_MONO_WAV_PATH, mono=True)
        y = convolve(x, sr, './impulse_responses/ir_classroom.wav', 0.6)
        lr.output.write_wav(
            TEST_MONO_WAV_PATH + '.ir_classroom.wav',
            y, sr=sr, norm=False)
        y = convolve(x, sr, './impulse_responses/ir_smartphone_mic.wav')
        lr.output.write_wav(
            TEST_MONO_WAV_PATH + '.ir_smartphone_mic.wav',
            y, sr=sr, norm=False)

    def test_lame(self):
        lame(TEST_MONO_WAV_PATH,
             TEST_MONO_WAV_PATH + '.mp3_1.mp3', 1)
        lame(TEST_MONO_WAV_PATH,
             TEST_MONO_WAV_PATH + '.mp3_5.mp3', 5)

    def test_apply_gain(self):
        print "Testing apply_gain()"
        # Test file reading
        x, sr = lr.core.load(TEST_MONO_WAV_PATH, mono=True)
        print "Length of file: %d samples" % len(x)
        print "Mean amplitude before: %f" % np.mean(np.abs(x))

        y = apply_gain(x, -6)
        print "Mean amplitude after -6dB: %f" % np.mean(np.abs(y))
        gain_test_wav = TEST_MONO_WAV_PATH + '.gain-6.wav'
        lr.output.write_wav(gain_test_wav, y, 8000, norm=False)

        y = apply_gain(x, 6)
        print "Mean amplitude after +6dB: %f" % np.mean(np.abs(y))
        gain_test_wav = TEST_MONO_WAV_PATH + '.gain+6.wav'
        lr.output.write_wav(gain_test_wav, y, 8000, norm=False)

    def test_apply_rubberband(self):
        x, sr = lr.core.load(TEST_MONO_WAV_PATH, mono=True)
        t_x = apply_rubberband(x, sr, time_stretching_ratio=0.5)
        p_x = apply_rubberband(x, sr, pitch_shifting_ratio=1.2)
        lr.output.write_wav(TEST_MONO_WAV_PATH + '.timestr.wav',
                            t_x, sr=sr, norm=False)
        lr.output.write_wav(TEST_MONO_WAV_PATH + '.pitchshift.wav',
                            p_x, sr=sr, norm=False)

    def test_timestretching_pitchshifting(self):
        x, sr = lr.core.load(TEST_MONO_WAV_PATH, mono=True)
        t_x = lr.effects.time_stretch(x, rate=0.5)
        p_x = lr.effects.pitch_shift(x, sr, n_steps=3,
                                     bins_per_octave=24)
        lr.output.write_wav(TEST_MONO_WAV_PATH + '.timestr.wav',
                            t_x, sr=sr, norm=False)
        lr.output.write_wav(TEST_MONO_WAV_PATH + '.pitchshift.wav',
                            p_x, sr=sr, norm=False)

    def teardown_class(self):
        cmd = "rm {0}.*".format(TEST_MONO_WAV_PATH)
        os.system(cmd)
