import os
import librosa as lr
import logging
import uuid
from utils import run


class AudioFile(object):
    """ This class provides all needed methods to interact with an audio file
    """
    def __init__(self, audio_path, tmp_dir='./'):
        basename = os.path.basename(audio_path)
        self.tmp_dir = tmp_dir
        self.applied_degradations = []
        self.audio_path = audio_path
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_path = os.path.join(tmp_dir,
                                     (basename + '__tmp__' +
                                      str(uuid.uuid4()) + '.wav'))
        self.tmp_path_extra = self.tmp_path + '.extra.wav'
        self._create_tmp_mirror_file()

    def _create_tmp_mirror_file(self):
        out, err, returncode = run(
                'ffmpeg -y -i {0} -ac 2 -acodec pcm_f32le {1}'.format(
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
        out, err, returncode = run(
                "ffmpeg -y -i {0} -ac 2 -acodec pcm_f32le {1}".format(
                    self.tmp_path, output_path))
        logging.debug(out)
        logging.debug(err)

    def delete_tmp_files(self):
        logging.debug("Deleting %s" % self.tmp_path)
        os.remove(self.tmp_path)
        if os.path.isfile(self.tmp_path_extra):
            logging.debug("Deleting %s" % self.tmp_path_extra)
            os.remove(self.tmp_path_extra)
        if os.listdir(self.tmp_dir) == []:
            logging.debug("Deleting empty directory %s" % self.tmp_dir)
            os.rmdir(self.tmp_dir)

    def resample(self, new_sample_rate):
        out, err, returncode = run(
                ('ffmpeg -y -i {0} -ac 2 -acodec pcm_f32le ' +
                 '-ar {1} {2}').format(
                     self.tmp_path, new_sample_rate,
                     self.tmp_path_extra))
        logging.debug(out)
        logging.debug(err)
        self.samples, self.sample_rate = lr.core.load(
                self.tmp_path_extra,
                sr=None, mono=False)
        self._update_mirror_file()
