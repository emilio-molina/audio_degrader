from abc import ABCMeta, abstractmethod
from utils import run, NAME_SEP, PARAMETERS_SEP, DESCRIPTION_SEP
import librosa as lr
import logging
import numpy as np
from scipy import signal
import os
import subprocess


class Degradation(object):
    """ Abstract class to implement degradations """

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
    """ It generates documentation strings about a given degradation """

    base_indent = " " * 8
    indent = " " * 12

    @staticmethod
    def get_degradation_help_header(degradation):
        """ Generate help header given a degradation

        e.g. gain,value:

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Help header
        """
        help_str = "    {0}".format(degradation.name)
        has_params = len(degradation.parameters_info) > 0
        if has_params:
            help_str += "{0}".format(NAME_SEP)
        help_str += PARAMETERS_SEP.join(
            map(lambda x: x[0], degradation.parameters_info))
        help_str += DESCRIPTION_SEP
        return help_str

    @staticmethod
    def get_degradation_help_params_info(degradation):
        """ Generate parameters info given a degradation

        e.g. parameters:
                 value: Gain value [dB]

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Parameters information
        """
        base_indent = DegradationUsageDocGenerator.base_indent
        indent = DegradationUsageDocGenerator.indent
        help_params_info_str = "\n{0}parameters:".format(base_indent)
        for p in degradation.parameters_info:
            help_params_info_str += "\n{0}{1}{2}{3}".format(
                indent, p[0], DESCRIPTION_SEP, p[2])
        return help_params_info_str

    @staticmethod
    def get_degradation_help_example(degradation):
        """ Generate help example given a degradation

        e.g. example:
                 gain,6

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Help example
        """
        base_indent = DegradationUsageDocGenerator.base_indent
        indent = DegradationUsageDocGenerator.indent
        help_example_str = "\n{0}example:".format(base_indent)
        help_example_str += "\n{0}{1}".format(indent,
                                              degradation.name)
        has_params = len(degradation.parameters_info) > 0
        if has_params:
            help_example_str += "{0}".format(NAME_SEP)
        help_example_str += PARAMETERS_SEP.join(
            map(lambda x: "{0}".format(x[1]), degradation.parameters_info))
        return help_example_str

    @staticmethod
    def get_degradation_help_description(degradation):
        """ Generate help description given a degradation

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Degradation description
        """
        return degradation.description

    @staticmethod
    def get_degradation_help(degradation):
        """ Generate complete help for a given degradation

        e.g. gain,value: Apply gain expressed in dBs
             parameters:
                 value: Gain value [dB]
             example:
                 gain,6

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Degradation help docstring
        """
        help_str = (
            DegradationUsageDocGenerator.get_degradation_help_header(
                degradation) +
            DegradationUsageDocGenerator.get_degradation_help_description(
                degradation) +
            DegradationUsageDocGenerator.get_degradation_help_params_info(
                degradation) +
            DegradationUsageDocGenerator.get_degradation_help_example(
                degradation))
        return help_str


class DegradationTrim(Degradation):

    name = "trim_from"
    description = "Trim audio from a given start time"
    parameters_info = [("start_time", 0.1, "Trim start [seconds]")]

    def apply(self, degraded_audio_file):
        start_time = float(self.parameters_values["start_time"])
        start_sample = int(start_time * degraded_audio_file.sample_rate)
        degraded_audio_file.samples = degraded_audio_file.samples[
            :, start_sample:]


class DegradationMp3(Degradation):

    name = "mp3"
    description = "Emulate mp3 transcoding"
    parameters_info = [("bitrate", "320k", "Quality [bps]")]

    def apply(self, degraded_audio_file):
        bitrate = str(self.parameters_values["bitrate"])
        tmp_mp3_path = degraded_audio_file.tmp_path + ".mp3"
        tmp_wav_path = degraded_audio_file.tmp_path + ".mp3.wav"
        out, err = run("ffmpeg -y -i {0} -b:a {1} {2}".format(
            degraded_audio_file.tmp_path, bitrate, tmp_mp3_path))
        logging.debug(out)
        logging.debug(err)
        out, err = run("ffmpeg -y -i {0} -ac 2 -acodec pcm_f32le {1}".format(
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
    parameters_info = [("value", "6", "Gain value [dB]")]

    def apply(self, degraded_audio_file):
        value = float(self.parameters_values["value"])
        logging.debug("Apply gain %f dB" % value)
        x = degraded_audio_file.samples
        x = x * (10 ** (value / 20.0))  # linear value
        x = np.minimum(np.maximum(-1.0, x), 1.0)
        degraded_audio_file.samples = x


class DegradationNormalization(Degradation):

    name = "normalization"
    description = "Normalize amplitude of audio to range [-1.0, 1.0]"
    parameters_info = []

    def apply(self, degraded_audio_file):
        x = degraded_audio_file.samples
        x = x - np.mean(x)
        max_amp = np.max(np.abs(x))
        logging.debug("Max abs(amplitude): {0:.3f}".format(max_amp))
        x /= max_amp
        x = np.minimum(np.maximum(-1.0, x), 1.0)
        degraded_audio_file.samples = x


class DegradationMix(Degradation):

    name = "mix"
    description = ("Mix input with a specified noise. " +
                   "The noise can be specified with its full path or "
                   "relative to the resources directory (see -l option)")
    parameters_info = [("noise",
                        "sounds/ambience-pub.wav",
                        "Full or relative path (to resources dir) of noise"),
                       ("snr",
                        "6",
                        "Desired Signal-to-Noise-Ratio [dB]")]

    def read_noise(self, noise_path, degraded_audio_file):
        """ Read samples of noise resampled at specified sample_rate

        Args:
            degraded_audio_file (DegradedAudioFile): Input DegradedAudioFile
        Returns:
            (np.array): Samples of noise with shape (2, nsamples)
        """
        sample_rate = degraded_audio_file.sample_rate
        aux_x_noise, _ = lr.core.load(noise_path, sr=sample_rate, mono=False)
        if len(aux_x_noise.shape) == 1:
            noise_samples = np.zeros((2, len(aux_x_noise)))
            noise_samples[0, :] = aux_x_noise
            noise_samples[1, :] = aux_x_noise
        else:
            noise_samples = aux_x_noise
        return noise_samples

    def adjust_noise_duration(self, noise_samples, degraded_audio_file):
        """ Adjust the duration of noise_samples to fit degraded_audio_file

        In case it is shorter, it repeats the noise.

        Args:
            noise_samples (np.array): Samples of noise with shape (2, nsamples)
            degraded_audio_file (DegradedAudioFile): Input audio
        Returns:
            (np.array): Samples of noise with shape (2, new_nsamples)
        """
        input_num_samples = degraded_audio_file.samples.shape[1]
        while noise_samples.shape[1] < input_num_samples:
            noise_samples = np.concatenate((noise_samples, noise_samples),
                                           axis=1)
        noise_samples = noise_samples[:, :input_num_samples]
        return noise_samples

    def get_actual_noise_path(self):
        """ Resolve full path of noise

        The specified noise path could be a relative path
        """
        import audio_degrader
        resources_dir = os.path.join(audio_degrader.__path__[0],
                                     'resources')
        noise_path = self.parameters_values['noise']
        if not os.path.isfile(noise_path):
            noise_path = os.path.join(resources_dir, noise_path)
        return noise_path

    def get_noise_gain_factor(self, snr_dbs, rms_noise, rms_input):
        """ Get gain factor that should be applied to noise

        Args:
            snr_dbs (float): Desired SNR in dBs
            rms_noise (float): RMS value of noise
            rms_input (float): RMS value of input
        Returns:
            (float): Noise gain factor
        """
        logging.debug("RMS noise: %f" % rms_noise)
        logging.debug("RMS input: %f" % rms_input)
        snr_linear = 10 ** (snr_dbs / 20.0)
        logging.debug("SNR , SNR linear: %f , %f" % (snr_dbs, snr_linear))
        noise_gain_factor = rms_input / rms_noise / snr_linear
        logging.debug("noise_gain_factor: %f" % noise_gain_factor)
        return noise_gain_factor

    def apply(self, degraded_audio_file):
        noise_path = self.get_actual_noise_path()
        noise_samples = self.adjust_noise_duration(
            self.read_noise(noise_path, degraded_audio_file),
            degraded_audio_file)
        rms_noise = np.sqrt(np.mean(np.power(noise_samples, 2)))
        rms_input = np.sqrt(np.mean(np.power(degraded_audio_file.samples, 2)))
        noise_gain_factor = self.get_noise_gain_factor(
            float(self.parameters_values['snr']),
            rms_noise,
            rms_input)
        y = degraded_audio_file.samples + noise_samples * noise_gain_factor
        # Normalize output RMS to fit input RMS
        rms_y = np.sqrt(np.mean(np.power(y, 2)))
        y = y * rms_input / rms_y
        degraded_audio_file.samples = y


class DegradationResample(Degradation):

    name = "resample"
    description = "Resample to given sample rate"
    parameters_info = [("sample_rate", "8000", "Desired sample rate [Hz]")]

    def apply(self, degraded_audio_file):
        degraded_audio_file.resample(
            int(self.parameters_values['sample_rate']))


class DegradationConvolution(Degradation):

    name = "convolution"
    description = "Convolve input with specified impulse response"
    parameters_info = [
        ("impulse_response",
         "impulse_responses/ir_classroom.wav",
         "Full or relative path (to resources dir) of impulse response"),
        ("level",
         "1.0",
         "Wet level (0.0=dry, 1.0=wet)")]

    def get_actual_impulse_response_path(self):
        """ Resolve full path of impulse response

        The specified impulse response path could be a relative path
        """
        import audio_degrader
        resources_dir = os.path.join(audio_degrader.__path__[0],
                                     'resources')
        ir_path = self.parameters_values['impulse_response']
        if not os.path.isfile(ir_path):
            ir_path = os.path.join(resources_dir, ir_path)
        return ir_path

    def apply(self, degraded_audio_file):
        ir_path = self.get_actual_impulse_response_path()
        level = float(self.parameters_values['level'])
        logging.info('Convolving with %s and level %f' % (ir_path, level))
        x = degraded_audio_file.samples
        ir_x, sr_x = lr.core.load(ir_path, sr=None, mono=False)
        logging.info('Converting IR sample rate from {0}Hz to {1}Hz'.format(
            sr_x, degraded_audio_file.sample_rate))
        y_wet = np.zeros(x.shape)
        for channel in [0, 1]:
            sampled_ir_x = lr.core.resample(ir_x[channel, :],
                                            sr_x,
                                            degraded_audio_file.sample_rate)
            y_wet[channel, :] = signal.fftconvolve(
                x[channel, :], sampled_ir_x, mode='full')[0:x.shape[1]]
        y = y_wet * level + x * (1 - level)
        degraded_audio_file.samples = y


class DegradationDynamicRangeCompression(Degradation):

    name = "dr_compression"
    description = "Apply dynamic range compression"
    parameters_info = [
        ("degree",
         "0",
         "Degree of compression. Presets from 0 (soft) to 3 (hard)")]

    def apply(self, degraded_audio_file):
        extra_tmp_path = degraded_audio_file.tmp_path + '.extra.wav'
        degree = int(self.parameters_values['degree'])
        if degree == 1:
            cmd = ("sox {0} {1} compand " +
                   "0.01,0.20 -40,-10,-30 5")
        elif degree == 2:
            cmd = ("sox {0} {1} compand " +
                   "0.01,0.20 -50,-50,-40,-30,-40,-10,-30 12")
        elif degree == 3:
            cmd = ("sox {0} {1} compand " +
                   "0.01,0.1 -70,-60,-70,-30,-70,0,-70 45")
        cmd = cmd.format(degraded_audio_file.tmp_path,
                         extra_tmp_path)
        logging.info(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            logging.debug(out)
            logging.debug(err)
            logging.error("Error running sox!")
        y, sr = lr.core.load(extra_tmp_path, sr=None, mono=False)
        os.remove(extra_tmp_path)
        assert degraded_audio_file.sample_rate == sr
        degraded_audio_file.samples = y


class DegradationSpeed(Degradation):

    name = "speed"
    description = "Change playback speed"
    parameters_info = [
        ("speed",
         "0.9",
         "Playback speed factor")]

    def apply(self, degraded_audio_file):
        speed_factor = float(self.parameters_values['speed'])
        logging.info('Modifying speed with factor %f' % speed_factor)
        x = degraded_audio_file.samples
        y0 = lr.core.resample(x[0, :], degraded_audio_file.sample_rate,
                              degraded_audio_file.sample_rate / speed_factor)
        y1 = lr.core.resample(x[1, :], degraded_audio_file.sample_rate,
                              degraded_audio_file.sample_rate / speed_factor)
        y = np.zeros((2, len(y0)))
        y[0, :] = y0
        y[1, :] = y1
        degraded_audio_file.samples = y


class DegradationTimeStretching(Degradation):

    name = "time_stretch"
    description = "Apply time stretching"
    parameters_info = [
        ("time_stretch_factor",
         "0.9",
         "Time stretch factor")]

    def apply(self, degraded_audio_file):
        x = degraded_audio_file.samples
        time_stretch_factor = float(
            self.parameters_values["time_stretch_factor"])
        logging.info(('Time stretching with factor %f' %
                      (time_stretch_factor)))
        y0 = lr.effects.time_stretch(x[0, :], time_stretch_factor)
        y1 = lr.effects.time_stretch(x[1, :], time_stretch_factor)
        y = np.zeros((2, len(y0)))
        y[0, :] = y0
        y[1, :] = y1
        degraded_audio_file.samples = y


class DegradationPitchShifting(Degradation):

    name = "pitch_shift"
    description = "Apply pitch shifting"
    parameters_info = [
        ("pitch_shift_factor",
         "0.9",
         "Pitch shift factor")]

    def apply(self, degraded_audio_file):
        x = degraded_audio_file.samples
        sr = degraded_audio_file.sample_rate
        pitch_shift_factor = float(
            self.parameters_values["pitch_shift_factor"])
        n_semitones = 12 * np.log2(pitch_shift_factor)
        logging.info(('Shifting pitch with factor %f, i.e. %f semitones' %
                      (pitch_shift_factor, n_semitones)))
        y0 = lr.effects.pitch_shift(x[0, :], sr, n_semitones,
                                    bins_per_octave=12)
        y1 = lr.effects.pitch_shift(x[1, :], sr, n_semitones,
                                    bins_per_octave=12)
        y = np.zeros((2, len(y0)))
        y[0, :] = y0
        y[1, :] = y1
        degraded_audio_file.samples = y


class DegradationEqualization(Degradation):

    name = "equalize"
    description = "Apply a two-pole peaking equalisation (EQ) filter"
    parameters_info = [
        ("central_freq",
         "100",
         "Central frequency of filter in Hz"),
        ("bandwidth",
         "50",
         "Bandwith of filter in Hz"),
        ("gain",
         "-10",
         "Gain of filter in dBs")]

    def apply(self, degraded_audio_file):
        freq = float(self.parameters_values['central_freq'])
        bw = float(self.parameters_values['bandwidth'])
        gain = float(self.parameters_values['gain'])
        logging.info("Equalizing. f=%f, bw=%f, gain=%f" % (freq, bw, gain))
        extra_tmp_path = degraded_audio_file.tmp_path + '.extra.wav'
        cmd = "sox {0} {1} equalizer {2} {3} {4}".format(
            degraded_audio_file.tmp_path,
            extra_tmp_path,
            freq,
            bw,
            gain)
        logging.info(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            logging.debug(out)
            logging.debug(err)
            logging.error("Error running sox!")
        y, sr = lr.core.load(extra_tmp_path, sr=None, mono=None)
        os.remove(extra_tmp_path)
        assert degraded_audio_file.sample_rate == sr
        degraded_audio_file.samples = y


ALL_DEGRADATIONS = {
    DegradationTrim.name: DegradationTrim,
    DegradationMp3.name: DegradationMp3,
    DegradationGain.name: DegradationGain,
    DegradationNormalization.name: DegradationNormalization,
    DegradationMix.name: DegradationMix,
    DegradationResample.name: DegradationResample,
    DegradationConvolution.name: DegradationConvolution,
    DegradationSpeed.name: DegradationSpeed,
    DegradationPitchShifting.name: DegradationPitchShifting,
    DegradationTimeStretching.name: DegradationTimeStretching,
    DegradationEqualization.name: DegradationEqualization,
    DegradationDynamicRangeCompression.name: DegradationDynamicRangeCompression
}
