import pytest
import os
import librosa as lr
from audio_degrader import mix_with_sound

TEST_STEREO_WAV_PATH = './tests/test_files/test30s_44100_stereo_pcm16le.wav'
TEST_MONO_WAV_PATH = './tests/test_files/test30s_44100_mono_pcm16le.wav'

class TestMixSounds:

    def setup_class(self):
        pass

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

    def teardown_class(self):
        cmd = "rm {0}.*".format(TEST_MONO_WAV_PATH)
        os.system(cmd)
