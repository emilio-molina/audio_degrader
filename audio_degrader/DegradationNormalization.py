import logging
import numpy as np
from BaseDegradation import Degradation


class DegradationNormalization(Degradation):

    name = "normalize"
    description = "Normalize amplitude of audio to range [-1.0, 1.0]"
    parameters_info = []

    def apply(self, audio_file):
        x = audio_file.samples
        x = x - np.mean(x)
        max_amp = np.max(np.abs(x))
        logging.debug("Max abs(amplitude): {0:.3f}".format(max_amp))
        x /= max_amp
        x = np.minimum(np.maximum(-1.0, x), 1.0)
        audio_file.samples = x
