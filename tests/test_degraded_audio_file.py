import os
import shutil
import librosa as lr
import numpy as np
import logging
from audio_degrader import DegradedAudioFile
from audio_degrader import Degradation

TEST_STEREO_WAV_PATH = './tests/test_files/test30s_44100_stereo_pcm16le.wav'
TEST_MONO_WAV_PATH = './tests/test_files/test30s_44100_mono_pcm16le.wav'
TEST_MONO_8K_WAV_PATH = './tests/test_files/test30s_8000_mono_pcm16le.wav'
TMP_PATH = './tests/tmp'


class TestDegradedAudioFile:

    def setup_class(self):
        logging.basicConfig(level=logging.DEBUG)
        if not os.path.isdir(TMP_PATH):
            os.makedirs(TMP_PATH)
        self.dafs = [DegradedAudioFile(TEST_STEREO_WAV_PATH,
                                       TMP_PATH),
                     DegradedAudioFile(TEST_MONO_WAV_PATH,
                                       TMP_PATH),
                     DegradedAudioFile(TEST_MONO_8K_WAV_PATH,
                                       TMP_PATH)]

    def test_creation(self):
        assert self.dafs[0].sample_rate == 44100
        assert self.dafs[1].sample_rate == 44100
        assert self.dafs[2].sample_rate == 8000

        for daf in self.dafs:
            assert os.path.isfile(daf.tmp_path)
            assert daf.samples.shape[0] == 2

    def test_apply_degradation(self):

        class DegradationInvert(Degradation):
            def apply(self, daf):
                daf.samples[0] = daf.samples[0][::-1]
                daf.samples[1] = daf.samples[1][::-1]
        for daf in self.dafs:
            old_samples = np.copy(daf.samples)
            d = DegradationInvert()
            daf.apply_degradation(d)
            samples, _ = lr.core.load(daf.tmp_path,
                                      sr=None, mono=False)
            assert np.sum(samples) != 0.0
            assert np.sum(np.abs(samples - daf.samples)) == 0.0
            assert np.sum(np.abs(old_samples[0][::-1] - samples[0])) == 0.0
            assert np.sum(np.abs(old_samples[1][::-1] - samples[1])) == 0.0

    def test_to_wav(self):
        for daf in self.dafs:
            out_path = os.path.join(TMP_PATH, 'out.wav')
            daf.to_wav(out_path)
            assert os.path.isfile(out_path)
            samples, _ = lr.core.load(out_path,
                                      sr=None, mono=False)
            assert(np.sum(np.abs(samples - daf.samples)) == 0.0)
            os.remove(out_path)

    def test_to_mp3(self):
        for daf in self.dafs:
            out_path = os.path.join(TMP_PATH, 'out.mp3')
            daf.to_mp3(out_path)
            assert os.path.isfile(out_path)
            os.remove(out_path)

    def test_deletion_tmp_file(self):
        for daf in self.dafs:
            daf.delete_tmp_mirror_file()
            assert not os.path.isfile(daf.tmp_path)

    def teardown_class(self):
        shutil.rmtree(TMP_PATH)
