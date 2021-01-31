from .utils import run
import soundfile as sf
import logging
import os
import sox
from .BaseDegradation import Degradation


class DegradationMp3(Degradation):

    name = "mp3"
    description = "Emulate mp3 transcoding"
    parameters_info = [("bitrate", "320k", "Quality [bps]")]

    def apply(self, audio_file):
        bitrate = str(self.parameters_values["bitrate"])
        bitrate = bitrate.replace('k', '')
        tmp_mp3_path = audio_file.tmp_path + ".mp3"
        tmp_wav_path = audio_file.tmp_path + ".mp3.wav"
        out, err, returncode = run("sox {0} -C {1}.01 {2}".format(
            audio_file.tmp_path, bitrate, tmp_mp3_path))
        logging.debug(out)
        logging.debug(err)
        tfm = sox.Transformer()
        tfm.convert(n_channels=2, bitdepth=32)
        tfm.build(tmp_mp3_path, tmp_wav_path)
        samples, _ = sf.read(tmp_wav_path)
        samples = samples.T
        audio_file.samples = samples
        os.remove(tmp_mp3_path)
        os.remove(tmp_wav_path)
