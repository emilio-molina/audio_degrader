import logging
import numpy as np
from BaseDegradation import Degradation


class DegradationGain(Degradation):

    name = "gain"
    description = "Apply gain expressed in dBs"
    parameters_info = [("value", "6", "Gain value [dB]")]

    def apply(self, audio_file):
        value = float(self.parameters_values["value"])
        logging.debug("Apply gain %f dB" % value)
        x = audio_file.samples
        x = x * (10 ** (value / 20.0))  # linear value
        x = np.minimum(np.maximum(-1.0, x), 1.0)
        audio_file.samples = x
