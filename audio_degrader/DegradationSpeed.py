import librosa as lr
import logging
import numpy as np
from BaseDegradation import Degradation


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
