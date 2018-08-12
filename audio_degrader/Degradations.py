from abc import ABCMeta, abstractmethod
from utils import run
import librosa as lr
import logging
import numpy as np
import os


class Degradation(object):
    """ Abstract class to implement degradations
    """
    __metaclass__ = ABCMeta

    def set_documentation_info(self,
                               name,
                               description,
                               parameters_info=[]):
        """ Set information to create a help string about degradation

        Args:
            name (str): Name of degradation
            description (str): Short description of degradation
            parameters_info (list): Information about each parameter. The list
                                    contains tuples with the following info:
                                    [(param_name, example_value, unit),...]
        """
        self.name = name
        self.description = description
        self.parameters_info = parameters_info

    def __str__(self):
        return self.name

    def set_parameters_values(self, parameters_values={}):
        """ Set all parameters before calling apply method
        """
        self.parameters_values = parameters_values

    @abstractmethod
    def apply(self, degraded_audio_file):
        """ Process degraded_audio_file.samples field

        Args:
            degraded_audio_file (DegradedAudioFile): Audio file to be processed
        """
        pass


class DegradationTrim(Degradation):

    def __init__(self):
        name = "trim_from"
        description = "Trim audio from start"
        parameters_info = [("start_time", 0.1, "seconds")]
        self.set_documentation_info(name, description, parameters_info)

    def apply(self, degraded_audio_file):
        start_time = self.parameters_values["start_time"]
        start_sample = int(start_time * degraded_audio_file.sample_rate)
        degraded_audio_file.samples = degraded_audio_file.samples[
            :, start_sample:]


class DegradationMp3(Degradation):

    def __init__(self):
        name = "transcode_to_mp3"
        description = "Emulate mp3 transcoding"
        parameters_info = [("bitrate", "320k", "bps")]
        self.set_documentation_info(name, description, parameters_info)

    def apply(self, degraded_audio_file):
        bitrate = self.parameters_values["bitrate"]
        tmp_mp3_path = degraded_audio_file.tmp_path + ".mp3"
        tmp_wav_path = degraded_audio_file.tmp_path + ".mp3.wav"
        out, err = run("ffmpeg -y -i {0} -b:a {1} {2}".format(
            degraded_audio_file.tmp_path, bitrate, tmp_mp3_path))
        logging.debug(out)
        logging.debug(err)
        out, err = run("ffmpeg -y -i {0} -ac 2 -acodec pcm_s32le {1}".format(
            tmp_mp3_path, tmp_wav_path))
        logging.debug(out)
        logging.debug(err)
        samples, _ = lr.core.load(tmp_wav_path,
                                  sr=None, mono=False)
        degraded_audio_file.samples = samples
        os.remove(tmp_mp3_path)
        os.remove(tmp_wav_path)


class DegradationGain(Degradation):

    def __init__(self):
        name = "gain"
        description = "Apply gain expressed in dBs"
        parameters_info = [("gain", "6", "dB")]
        self.set_documentation_info(name, description, parameters_info)

    def apply(self, degraded_audio_file):
        gain = self.parameters_values["gain"]
        logging.info("Apply gain %f dB" % gain)
        x = degraded_audio_file.samples
        x = x * (10 ** (gain / 20.0))
        x = np.minimum(np.maximum(-1.0, x), 1.0)
        degraded_audio_file.samples = x


class DegradationNormalization(Degradation):

    def apply(self, degraded_audio_file):
        pass


class DegradationMix(Degradation):

    def apply(self, degraded_audio_file):
        pass


class DegradationConvolution(Degradation):

    def apply(self, degraded_audio_file):
        pass


class DegradationDynamicRangeCompression(Degradation):

    def apply(self, degraded_audio_file):
        pass


class DegradationSpeed(Degradation):

    def apply(self, degraded_audio_file):
        pass


class DegradationTimeStretching(Degradation):

    def apply(self, degraded_audio_file):
        pass


class DegradationPitchShifting(Degradation):

    def apply(self, degraded_audio_file):
        pass


class DegradationEqualization(Degradation):

    def apply(self, degraded_audio_file):
        pass
