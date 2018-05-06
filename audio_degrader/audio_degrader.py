#!/usr/bin/python
import os
import warnings
warnings.filterwarnings("ignore")  # noqa
import librosa as lr
import numpy as np
import subprocess
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG)

TEST_WAV = './test_files/test.wav'


def remove_tmp_files(tmp_files):
    for tmp_file in tmp_files:
        os.remove(tmp_file)


def mix_with_sound(x, sr, sound_path, snr):
    """ Mix x with sound from sound_path

    Args:
        x (numpy array): Input signal
        sound_path (str): Name of sound
        snr (float): Signal-to-noise ratio
    """
    z, sr = lr.core.load(sound_path, sr=sr, mono=True)
    while z.shape[0] < x.shape[0]:  # loop in case noise is shorter than
        z = np.concatenate((z, z), axis=0)
    z = z[0: x.shape[0]]
    rms_z = np.sqrt(np.mean(np.power(z, 2)))
    logging.debug("rms_z: %f" % rms_z)
    rms_x = np.sqrt(np.mean(np.power(x, 2)))
    logging.debug("rms_x: %f" % rms_x)
    snr_linear = 10 ** (snr / 20.0)
    logging.debug("snr , snr_linear: %f, %f" % (snr, snr_linear))
    snr_linear_factor = rms_x / rms_z / snr_linear
    logging.debug("y = x  + z * %f" % snr_linear_factor)
    y = x + z * snr_linear_factor
    rms_y = np.sqrt(np.mean(np.power(y, 2)))
    y = y * rms_x / rms_y
    return y


def convolve(x, sr, ir_path, level=1.0):
    """ Apply convolution to x using impulse response given
    """
    logging.info('Convolving with %s and level %f' % (ir_path, level))
    x = np.copy(x)
    ir, sr = lr.core.load(ir_path, sr=sr, mono=True)
    return np.convolve(x, ir, 'full')[0:x.shape[0]] * level + x * (1 - level)


def tmp_path(ext=''):
    tf = tempfile.NamedTemporaryFile()
    return tf.name + ext


def ffmpeg(in_wav, out_wav):
    cmd = ("ffmpeg -y -i {0} -ac 1 " +
           "-acodec pcm_s16le -async 1 {1}").format(
        in_wav, out_wav)
    logging.debug(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"


def lame(in_wav, out_mp3, degree):
    kbps_map = {
        1: 8,
        2: 16,
        3: 24,
        4: 32,
        5: 40
    }
    cmd = "lame -b {0} {1} {2}".format(kbps_map[degree], in_wav,
                                       out_mp3)
    logging.debug(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"


def apply_mp3(x, sr, degree):
    logging.info("MP3 compression. Degree %d" % degree)
    tmp_file_0 = tmp_path('.wav')
    tmp_file_1 = tmp_path('.wav')
    tmp_file_2 = tmp_path('.mp3')
    tmp_file_3 = tmp_path('.wav')
    lr.output.write_wav(tmp_file_0, x, sr=sr, norm=False)
    ffmpeg(tmp_file_0, tmp_file_1)
    lame(tmp_file_1, tmp_file_2, degree)
    ffmpeg(tmp_file_2, tmp_file_3)
    y, sr = lr.core.load(tmp_file_3, sr=sr, mono=True)
    remove_tmp_files([tmp_file_0, tmp_file_1, tmp_file_2, tmp_file_3])
    return y


def apply_gain(x, gain):
    """ Apply gain to x
    """
    logging.info("Apply gain %f dB" % gain)
    x = np.copy(x)
    x = x * (10 ** (gain / 20.0))
    x = np.minimum(np.maximum(-1.0, x), 1.0)
    return x


def trim_beginning(x, nsamples):
    return x[nsamples:]


def apply_dr_compression(x, sr, degree):
    tmp_file_0 = tmp_path('.wav')
    tmp_file_1 = tmp_path('.wav')
    lr.output.write_wav(tmp_file_0,
                        x, sr=sr, norm=False)
    if degree == 1:
        cmd = "sox {0} {1} compand 0.01,0.20 -40,-10,-30 5"
    elif degree == 2:
        cmd = "sox {0} {1} compand 0.01,0.20 -50,-50,-40,-30,-40,-10,-30 12"
    elif degree == 3:
        cmd = "sox {0} {1} compand 0.01,0.1 -70,-60,-70,-30,-70,0,-70 45"
    cmd = cmd.format(tmp_file_0, tmp_file_1)
    logging.info(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"
    y, sr = lr.core.load(tmp_file_1, sr=sr, mono=True)
    remove_tmp_files([tmp_file_0, tmp_file_1])
    return y


def normalize(x, percentage=1.0):
    max_peak = np.max(np.abs(x))
    return x / max_peak * percentage


def apply_eq(x, sr, value):
    freq, bw, gain = map(int, value.split('//'))
    logging.info("Equalizing. f=%f, bw=%f, gain=%f" % (freq, bw, gain))
    tmp_file_0 = tmp_path('.wav')
    tmp_file_1 = tmp_path('.wav')
    lr.output.write_wav(tmp_file_0,
                        x, sr=sr, norm=False)
    cmd = "sox {0} {1} equalizer {2} {3} {4}".format(
        tmp_file_0,
        tmp_file_1,
        freq,
        bw,
        gain)
    logging.info(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"
    y, sr = lr.core.load(tmp_file_1, sr=sr, mono=True)
    remove_tmp_files([tmp_file_0, tmp_file_1])
    return y


def main(input_wav, degradations_list, output_wav):
    """ Apply degradations to input wav

    Args:
        input_wav (str): Path of input wav
        degradations_list (list): List of degradations (e.g. ['mp3,1'])
        output_wav (str): Path of outpu wav
    """
    x, sr = lr.core.load(input_wav, mono=True)
    for degradation in degradations_list:
        degradation_name, value = degradation.split(',')
        if degradation_name == 'mp3':
            x = apply_mp3(x, sr, float(value))
        elif degradation_name == 'gain':
            x = apply_gain(x, float(value))
        elif degradation_name == 'normalize':
            x = normalize(x, float(value))
        elif degradation_name == 'mix':
            sound_path, snr = value.split('//')
            x = mix_with_sound(x, sr, sound_path, float(snr))
        elif degradation_name == 'impulse-response':
            ir_path, level = value.split('//')
            x = convolve(x, sr, ir_path, float(level))
        elif degradation_name == 'time-stretching':
            x = lr.effects.time_stretch(x, rate=float(value))
        elif degradation_name == 'pitch-shifting':
            x = lr.effects.pitch_shift(x, sr, n_steps=float(value),
                                       bins_per_octave=1200)
        elif degradation_name == 'dr-compression':
            x = apply_dr_compression(x, sr, degree=float(value))
        elif degradation_name == 'eq':
            x = apply_eq(x, sr, value)
        elif degradation_name == 'start':
            x = x[min(len(x), np.round(sr * float(value))):]
        else:
            logging.warning("Unknown degradation %s" % degradation)
    tmp_file = tmp_path()
    lr.output.write_wav(tmp_file, x, sr=sr, norm=False)
    ffmpeg(tmp_file, output_wav)
    remove_tmp_files([tmp_file])

