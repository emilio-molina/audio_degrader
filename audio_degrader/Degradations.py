from abc import ABCMeta, abstractmethod
from utils import run
import librosa as lr
import logging
import numpy as np
import os


NAME_SEP = ","
PARAMETERS_SEP = "//"
DESCRIPTION_SEP = ": "


class Degradation(object):
    """ Abstract class to implement degradations
    """
    __metaclass__ = ABCMeta
    name = "AbstractDegradation"  # Name of degradation
    description = "Abstract degradation"  # Short description of degradation
    parameters_info = [('param1', 1.0, 'Parameter one [unit1]'),
                       ('param2', 0.5, 'Parameter two [unit2]')]
    """ list: Information about each parameter.

    The list contains tuples with the following info:
        [(param_name, example_value, description),...]
    """

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


class DegradationUsageDocGenerator(object):

    @staticmethod
    def get_degradation_help_header(degradation):
        help_str = "{0}{1}".format(degradation.name, NAME_SEP)
        help_str += PARAMETERS_SEP.join(
            map(lambda x: x[0], degradation.parameters_info))
        help_str += DESCRIPTION_SEP
        base_indent = " " * len(help_str)
        return help_str, base_indent

    @staticmethod
    def get_degradation_help_params_info(degradation, base_indent):
        indent = base_indent + "    "
        help_params_info_str = "\n{0}parameters:".format(base_indent)
        for p in degradation.parameters_info:
            help_params_info_str += "\n{0}{1}{2}{3}".format(
                indent, p[0], DESCRIPTION_SEP, p[2])
        return help_params_info_str

    @staticmethod
    def get_degradation_help_example(degradation, base_indent):
        indent = base_indent + "    "
        help_example_str = "\n{0}example:".format(base_indent)
        help_example_str += "\n{0}{1}{2}".format(indent,
                                                 degradation.name,
                                                 NAME_SEP)
        help_example_str += PARAMETERS_SEP.join(
            map(lambda x: "{0}".format(x[1]), degradation.parameters_info))
        return help_example_str

    @staticmethod
    def get_degradation_help_description(degradation):
        return degradation.description

    @staticmethod
    def get_degradation_help(degradation):
        help_str, base_indent = DegradationUsageDocGenerator.\
            get_degradation_help_header(degradation)
        help_str = (
            help_str +
            DegradationUsageDocGenerator.get_degradation_help_description(
                degradation) +
            DegradationUsageDocGenerator.get_degradation_help_params_info(
                degradation, base_indent) +
            DegradationUsageDocGenerator.get_degradation_help_example(
                degradation, base_indent))
        return help_str


class DegradationTrim(Degradation):

    name = "trim_from"
    description = "Trim audio from start"
    parameters_info = [("start_time", 0.1, "Trim start [seconds]")]

    def apply(self, degraded_audio_file):
        start_time = self.parameters_values["start_time"]
        start_sample = int(start_time * degraded_audio_file.sample_rate)
        degraded_audio_file.samples = degraded_audio_file.samples[
            :, start_sample:]


class DegradationMp3(Degradation):

    name = "mp3"
    description = "Emulate mp3 transcoding"
    parameters_info = [("bitrate", "320k", "Quality [bps]")]

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

    name = "gain"
    description = "Apply gain expressed in dBs"
    parameters_info = [("gain", "6", "Gain value [dB]")]

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
