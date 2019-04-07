import librosa as lr
import logging
import numpy as np
from scipy import signal
import os
from BaseDegradation import Degradation


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
