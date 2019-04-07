import librosa as lr
import logging
import os
from utils import run
from BaseDegradation import Degradation


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

    def apply(self, audio_file):
        freq = float(self.parameters_values['central_freq'])
        bw = float(self.parameters_values['bandwidth'])
        gain = float(self.parameters_values['gain'])
        logging.info("Equalizing. f=%f, bw=%f, gain=%f" % (freq, bw, gain))
        extra_tmp_path = audio_file.tmp_path + '.extra.wav'
        cmd = "sox {0} {1} equalizer {2} {3} {4}".format(
            audio_file.tmp_path,
            extra_tmp_path,
            freq,
            bw,
            gain)
        logging.info(cmd)
        out, err, returncode = run(cmd)
        if returncode != 0:
            logging.debug(out)
            logging.debug(err)
            logging.error("Error running sox!")
        y, sr = lr.core.load(extra_tmp_path, sr=None, mono=None)
        os.remove(extra_tmp_path)
        assert audio_file.sample_rate == sr
        audio_file.samples = y
