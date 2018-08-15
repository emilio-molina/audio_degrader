import os
import shutil
import librosa as lr
import numpy as np
import logging
from audio_degrader import Degradation, DegradationUsageDocGenerator
from audio_degrader import DegradationTrim, DegradedAudioFile
from audio_degrader import DegradationMp3, DegradationGain

TEST_STEREO_WAV_PATH = './tests/test_files/test30s_44100_stereo_pcm16le.wav'
TEST_MONO_WAV_PATH = './tests/test_files/test30s_44100_mono_pcm16le.wav'
TEST_MONO_8K_WAV_PATH = './tests/test_files/test30s_8000_mono_pcm16le.wav'
TMP_PATH = './tests/tmp'


class TestDegradationTrim:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = DegradedAudioFile(TEST_STEREO_WAV_PATH,
                                     TMP_PATH)

    def test_degradation_trim(self):
        samples, sample_rate = lr.core.load(self.daf.tmp_path,
                                            sr=None, mono=False)
        prev_length = samples.shape[1]
        degradation_trim = DegradationTrim()
        trim_seconds = 1
        degradation_trim.set_parameters_values({'start_time': trim_seconds})
        self.daf.apply_degradation(degradation_trim)
        samples, sample_rate = lr.core.load(self.daf.tmp_path,
                                            sr=None, mono=False)
        after_length = samples.shape[1]
        assert after_length == prev_length - int(sample_rate * trim_seconds)

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationMp3:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = DegradedAudioFile(TEST_STEREO_WAV_PATH,
                                     TMP_PATH)

    def test_degradation_mp3(self):
        degradation_mp3 = DegradationMp3()
        bitrate = '16k'
        degradation_mp3.set_parameters_values({'bitrate': bitrate})
        self.daf.apply_degradation(degradation_mp3)

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationGain:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = DegradedAudioFile(TEST_STEREO_WAV_PATH,
                                     TMP_PATH)

    def test_degradation_gain(self):
        degradation_gain = DegradationGain()
        gain = -6
        degradation_gain.set_parameters_values({'gain': gain})
        sum_before = np.sum(np.abs(self.daf.samples))
        self.daf.apply_degradation(degradation_gain)
        sum_after = np.sum(np.abs(self.daf.samples))
        assert (np.abs(sum_after / sum_before - 10**(gain/20.0)) < 0.001)

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationUsageDocGenerator:

    def test_degradation_help(self):

        class DegrTest(Degradation):
            name = "testdeg"
            description = "Degradation for this test"
            parameters_info = [("param1", 2.0, "Parameter one [dBs]"),
                               ("param2", 3.0, "Parameter two [seconds]")]
        degradation_trim_help = (
            DegradationUsageDocGenerator.get_degradation_help(DegrTest))
        target_docstring = """testdeg,param1//param2: Degradation for this test
                        parameters:
                            param1: Parameter one [dBs]
                            param2: Parameter two [seconds]
                        example:
                            testdeg,2.0//3.0"""
        logging.debug("\n" + degradation_trim_help)
        logging.debug(target_docstring)
        assert degradation_trim_help == target_docstring
