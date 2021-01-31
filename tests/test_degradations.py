import os
import shutil
import soundfile as sf
import numpy as np
import logging
from audio_degrader import Degradation, DegradationUsageDocGenerator
from audio_degrader import DegradationTrim, AudioFile
from audio_degrader import DegradationMp3, DegradationGain, DegradationMix
from audio_degrader import DegradationResample, DegradationConvolution
from audio_degrader import DegradationSpeed, DegradationPitchShifting
from audio_degrader import DegradationTimeStretching
from audio_degrader import DegradationDynamicRangeCompression
from audio_degrader import DegradationEqualization

TEST_STEREO_WAV_PATH = './tests/test_files/test30s_44100_stereo_pcm16le.wav'
TEST_MONO_WAV_PATH = './tests/test_files/test30s_44100_mono_pcm16le.wav'
TEST_MONO_8K_WAV_PATH = './tests/test_files/test30s_8000_mono_pcm16le.wav'
TMP_PATH = './tests/tmp'


class TestDegradationTrim:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_trim(self):
        samples, sample_rate = sf.read(self.daf.tmp_path)
        samples = samples.T
        prev_length = samples.shape[1]
        degradation_trim = DegradationTrim()
        trim_seconds = 1
        degradation_trim.set_parameters_values({'start_time': trim_seconds})
        self.daf.apply_degradation(degradation_trim)
        samples, sample_rate = sf.read(self.daf.tmp_path)
        samples = samples.T
        after_length = samples.shape[1]
        assert after_length == prev_length - int(sample_rate * trim_seconds)

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationMp3:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_mp3(self):
        degradation_mp3 = DegradationMp3()
        bitrate = '32k'
        degradation_mp3.set_parameters_values({'bitrate': bitrate})
        self.daf.apply_degradation(degradation_mp3)

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationGain:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_gain(self):
        degradation_gain = DegradationGain()
        value = -6
        degradation_gain.set_parameters_values({'value': value})
        sum_before = np.sum(np.abs(self.daf.samples))
        self.daf.apply_degradation(degradation_gain)
        sum_after = np.sum(np.abs(self.daf.samples))
        assert (np.abs(sum_after / sum_before - 10**(value/20.0)) < 0.001)

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationMix:
    """ Test DegradationMix with stereo files with different sample rates
    """

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_mix(self):
        degradation_mix = DegradationMix()
        degradation_mix.set_parameters_values(
            {'noise': 'sounds/applause.wav',
             'snr': -3})
        self.daf.apply_degradation(degradation_mix)
        target_y, _ = sf.read('./tests/test_files/target_degr_mix.wav')
        target_y = target_y.T
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationResample:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_resample(self):
        degradation_resample = DegradationResample()
        degradation_resample.set_parameters_values(
            {'sample_rate': 8000})
        self.daf.apply_degradation(degradation_resample)
        target_y, sr = sf.read('./tests/test_files/target_degr_resample.wav')
        target_y = target_y.T
        assert self.daf.sample_rate == sr
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationConvolution:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_convolution(self):
        degradation_convolution = DegradationConvolution()
        degradation_convolution.set_parameters_values(
            {'impulse_response': 'impulse_responses/ir_classroom_mono.wav',
             'level': '0.7'})
        self.daf.apply_degradation(degradation_convolution)
        target_y, sr = sf.read(
            './tests/test_files/target_degr_convolution.wav')
        target_y = target_y.T
        assert self.daf.sample_rate == sr
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationSpeed:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_speed(self):
        degradation_speed = DegradationSpeed()
        degradation_speed.set_parameters_values(
            {'speed': '0.9'})
        self.daf.apply_degradation(degradation_speed)
        target_y, _ = sf.read('./tests/test_files/target_degr_speed.wav')
        target_y = target_y.T
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationPitchShifting:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_pitch_shifting(self):
        degradation_pitch_shifting = DegradationPitchShifting()
        degradation_pitch_shifting.set_parameters_values(
            {'pitch_shift_factor': '0.9'})
        self.daf.apply_degradation(degradation_pitch_shifting)
        target_y, _ = sf.read('./tests/test_files/target_degr_pitchshift.wav')
        target_y = target_y.T
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationTimeStretching:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_time_stretching(self):
        degradation_time_stretching = DegradationTimeStretching()
        degradation_time_stretching.set_parameters_values(
            {'time_stretch_factor': '0.9'})
        self.daf.apply_degradation(degradation_time_stretching)
        target_y, _ = sf.read('./tests/test_files/target_degr_timestretch.wav')
        target_y = target_y.T
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationDynamicRangeCompression:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_dynamic_range_compression(self):
        degradation_drcompression = DegradationDynamicRangeCompression()
        degradation_drcompression.set_parameters_values(
            {'degree': '3'})
        self.daf.apply_degradation(degradation_drcompression)
        target_y, _ = sf.read(
            './tests/test_files/target_degr_drcompression.wav')
        target_y = target_y.T
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)


class TestDegradationEqualization:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.daf = AudioFile(TEST_STEREO_WAV_PATH,
                             TMP_PATH)

    def test_degradation_equalization(self):
        degradation_equalization = DegradationEqualization()
        degradation_equalization.set_parameters_values(
            {'central_freq': '800',
             'bandwidth': '10',
             'gain': '20'})
        self.daf.apply_degradation(degradation_equalization)
        target_y, _ = sf.read('./tests/test_files/target_degr_equalize.wav')
        target_y = target_y.T
        assert np.mean(np.abs(target_y - self.daf.samples)) < 0.001

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
        target_docstring = '\n'.join((
            "    testdeg,param1,param2: Degradation for this test",
            "        parameters:",
            "            param1: Parameter one [dBs]",
            "            param2: Parameter two [seconds]",
            "        example:",
            "            testdeg,2.0,3.0"))
        logging.debug("\n" + degradation_trim_help)
        logging.debug(target_docstring)
        assert degradation_trim_help == target_docstring
