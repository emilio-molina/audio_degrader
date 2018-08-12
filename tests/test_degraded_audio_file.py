import os
import librosa as lr
import numpy as np
from audio_degrader import DegradedAudioFile
from audio_degrader import Degradation, DegradationTrim
from audio_degrader.utils import run

TEST_STEREO_WAV_PATH = './tests/test_files/test30s_44100_stereo_pcm16le.wav'
TEST_MONO_WAV_PATH = './tests/test_files/test30s_44100_mono_pcm16le.wav'
TEST_MONO_8K_WAV_PATH = './tests/test_files/test30s_8000_mono_pcm16le.wav'
TMP_PATH = './tests/tmp'

class TestDegradedAudioFile:

    def setup_class(self):
        os.makedirs(TMP_PATH)               

    def test_stereo(self):
        daf_stereo = DegradedAudioFile(TEST_STEREO_WAV_PATH,
                                       TMP_PATH)
        assert os.path.isfile(daf_stereo.tmp_path), \
                'Tmp path not found'
        daf_stereo.delete_tmp_mirror_file()

    def test_mono(self):
        daf_mono = DegradedAudioFile(TEST_STEREO_WAV_PATH,
                                     TMP_PATH)
        assert os.path.isfile(daf_mono.tmp_path), \
                'Tmp path not found'
        daf_mono.delete_tmp_mirror_file()

    def test_mono_8k(self):
        daf_mono_8k = DegradedAudioFile(TEST_STEREO_WAV_PATH,
                                        TMP_PATH)
        assert os.path.isfile(daf_mono_8k.tmp_path), \
                'Tmp path not found'
        daf_mono_8k.delete_tmp_mirror_file()

    def teardown_class(self):
        os.removedirs(TMP_PATH)