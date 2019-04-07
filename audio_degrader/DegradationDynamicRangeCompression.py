import librosa as lr
import logging
import os
from utils import run
from BaseDegradation import Degradation


class DegradationDynamicRangeCompression(Degradation):

    name = "dr_compression"
    description = "Apply dynamic range compression"
    parameters_info = [
        ("degree",
         "0",
         "Degree of compression. Presets from 0 (soft) to 3 (hard)")]

    def apply(self, audio_file):
        extra_tmp_path = audio_file.tmp_path + '.extra.wav'
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
        cmd = cmd.format(audio_file.tmp_path,
                         extra_tmp_path)
        logging.info(cmd)
        out, err, returncode = run(cmd)
        if returncode != 0:
            logging.debug(out)
            logging.debug(err)
            logging.error("Error running sox!")
        y, sr = lr.core.load(extra_tmp_path, sr=None, mono=False)
        os.remove(extra_tmp_path)
        assert audio_file.sample_rate == sr
        audio_file.samples = y
