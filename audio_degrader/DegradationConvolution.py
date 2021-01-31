import soundfile as sf
import logging
import sox
import numpy as np
from scipy import signal
import os
from .BaseDegradation import Degradation


class DegradationConvolution(Degradation):

    name = "convolution"
    description = "Convolve input with specified impulse response"
    parameters_info = [
        ("impulse_response",
         "impulse_responses/ir_classroom.wav",
         "Full path, URL (requires wget), or relative path (see -l option)"),
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
        tfm = sox.Transformer()
        tfm.rate(audio_file.sample_rate)
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(ir_path, extra_tmp_path)

        ir_x, _ = sf.read(extra_tmp_path)
        ir_x = ir_x.T
        os.remove(extra_tmp_path)
        y_wet = np.zeros(x.shape)
        for channel in [0, 1]:
            y_wet[channel, :] = signal.fftconvolve(
                x[channel, :], ir_x[channel, :], mode='full')[0:x.shape[1]]
        y = y_wet * level + x * (1 - level)
        audio_file.samples = y
