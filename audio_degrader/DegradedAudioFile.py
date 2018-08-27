import os
import librosa as lr
import logging
import uuid
from utils import run


class DegradedAudioFile(object):
    """ This class provides all needed methods to interact with an audio file
    """
    def __init__(self, audio_path, tmp_dir='./'):
        basename = os.path.basename(audio_path)
        self.applied_degradations = []
        self.audio_path = audio_path
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_path = os.path.join(tmp_dir,
                                     (basename + '__tmp__' +
                                      str(uuid.uuid4()) + '.wav'))
        self._create_tmp_mirror_file()

    def _create_tmp_mirror_file(self):
        out, err = run(('ffmpeg -y -i {0} -af "pan=stereo|c0=c0|c1=c0" ' +
                        '-acodec pcm_f32le {1}').format(
            self.audio_path, self.tmp_path))
        self.samples, self.sample_rate = lr.core.load(self.tmp_path,
                                                      sr=None, mono=False)
        logging.debug(out)
        logging.debug(err)

    def apply_degradation(self, degradation):
        self.applied_degradations.append(degradation)
        logging.debug("Applying {0} degradation".format(degradation))
        degradation.apply(self)
        self._update_mirror_file()

    def _update_mirror_file(self):
        logging.debug("Updating mirror file")
        lr.output.write_wav(self.tmp_path, self.samples,
                            self.sample_rate, norm=False)

    def to_wav(self, output_path):
        out, err = run("ffmpeg -y -i {0} {1}".format(self.tmp_path,
                                                     output_path))
        logging.debug(out)
        logging.debug(err)

    def to_mp3(self, output_path, bitrate='320k'):
        out, err = run("ffmpeg -y -i {0} -b:a {1} {2}".format(self.tmp_path,
                                                              bitrate,
                                                              output_path))
        logging.debug(out)
        logging.debug(err)

    def delete_tmp_mirror_file(self):
        os.remove(self.tmp_path)

    def resample(self, new_sample_rate):
        self.samples = lr.core.resample(self.samples, self.sample_rate,
                                        new_sample_rate)
        self.sample_rate = new_sample_rate
        self._update_mirror_file()
        self.samples, self.sample_rate = lr.core.load(self.tmp_path,
                                                      sr=None, mono=False)
