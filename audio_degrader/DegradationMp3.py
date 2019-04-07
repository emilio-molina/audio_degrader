from utils import run
import librosa as lr
import logging
import os
from BaseDegradation import Degradation


class DegradationMp3(Degradation):

    name = "mp3"
    description = "Emulate mp3 transcoding"
    parameters_info = [("bitrate", "320k", "Quality [bps]")]

    def apply(self, audio_file):
        bitrate = str(self.parameters_values["bitrate"])
        tmp_mp3_path = audio_file.tmp_path + ".mp3"
        tmp_wav_path = audio_file.tmp_path + ".mp3.wav"
        out, err, returncode = run("ffmpeg -y -i {0} -b:a {1} {2}".format(
            audio_file.tmp_path, bitrate, tmp_mp3_path))
        logging.debug(out)
        logging.debug(err)
        out, err, returncode = run(
                "ffmpeg -y -i {0} -ac 2 -acodec pcm_f32le {1}".format(
                    tmp_mp3_path, tmp_wav_path))
        logging.debug(out)
        logging.debug(err)
        samples, _ = lr.core.load(tmp_wav_path,
                                  sr=None, mono=False)
        audio_file.samples = samples
        os.remove(tmp_mp3_path)
        os.remove(tmp_wav_path)
