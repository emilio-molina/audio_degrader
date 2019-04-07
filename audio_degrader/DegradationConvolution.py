import librosa as lr
import logging
import numpy as np
from scipy import signal
import os
from utils import run
from BaseDegradation import Degradation


class DegradationConvolution(Degradation):

    name = "convolution"
    description = "Convolve input with specified impulse response"
    parameters_info = [
        ("impulse_response",
         "impulse_responses/ir_classroom.wav",
         "Full path, URL, or relative path (see -l option)"),
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
        ir_path_resource = os.path.join(resources_dir, ir_path)
        if not os.path.isfile(ir_path) and os.path.isfile(ir_path_resource):
            return ir_path_resource
        else:
            return ir_path

    def apply(self, audio_file):
        ir_path = self.get_actual_impulse_response_path()
        level = float(self.parameters_values['level'])
        logging.info('Convolving with %s and level %f' % (ir_path, level))
        x = audio_file.samples
        extra_tmp_path = audio_file.tmp_path + '.extra.wav'
        cmd = "ffmpeg -y -i {0} -ar {1} -ac 2 -acodec pcm_f32le {2}".format(
                ir_path,
                audio_file.sample_rate,
                extra_tmp_path)
        out, err, returncode = run(cmd)
        logging.debug(out)
        logging.debug(err)
        ir_x, sr_x = lr.core.load(extra_tmp_path, sr=None, mono=False)
        os.remove(extra_tmp_path)
        logging.info('Converting IR sample rate from {0}Hz to {1}Hz'.format(
            sr_x, audio_file.sample_rate))
        y_wet = np.zeros(x.shape)
        for channel in [0, 1]:
            sampled_ir_x = lr.core.resample(ir_x[channel, :],
                                            sr_x,
                                            audio_file.sample_rate)
            y_wet[channel, :] = signal.fftconvolve(
                x[channel, :], sampled_ir_x, mode='full')[0:x.shape[1]]
        y = y_wet * level + x * (1 - level)
        audio_file.samples = y
