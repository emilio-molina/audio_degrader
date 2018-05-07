#!/usr/bin/python
import os
import librosa as lr
import numpy as np
import subprocess
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG)


def remove_tmp_files(tmp_files):
    """ Remove list of files

    Typically used for temporal files

    Args:
        tmp_files (list): List of files to be removed
    """
    for tmp_file in tmp_files:
        os.remove(tmp_file)


def mix_with_sound(x, sr, sound_path, snr):
    """ Mix x with sound from sound_path

    Args:
        x (numpy array): Input signal
        sound_path (str): Path of mixing sound. If it does not exist,
                          it checks the path as relative to resources dir
        snr (float): Signal-to-noise ratio

    Returns:
        (numpy array): Output signal
    """
    if not os.path.isfile(sound_path):
        resource_sound_path = os.path.join(os.path.dirname(__file__),
                                           'resources',
                                           sound_path)
        if os.path.isfile(resource_sound_path):
            sound_path = resource_sound_path
    z, sr = lr.core.load(sound_path, sr=sr, mono=True)
    logging.debug("Mixing with sound {0}".format(sound_path))
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
    """ Apply convolution to x using given impulse response (as wav file)

    Args:
        x (numpy array): Input signal
        sr (int): Sample rate
        ir_path (string): Path of impulse response file (wav). If it does not
                          exist, it checks the path as relative to resources
                          dir
        level (float): Level of wet/dry signals (1.0=wet)

    Returns:
        (numpy array): Output signal
    """
    if not os.path.isfile(ir_path):
        resource_ir_path = os.path.join(os.path.dirname(__file__),
                                        'resources',
                                        ir_path)
        if os.path.isfile(resource_ir_path):
            ir_path = resource_ir_path
    logging.info('Convolving with %s and level %f' % (ir_path, level))
    x = np.copy(x)
    ir, sr = lr.core.load(ir_path, sr=sr, mono=True)
    return np.convolve(x, ir, 'full')[0:x.shape[0]] * level + x * (1 - level)


def tmp_path(ext=''):
    """ Returns path of temporary file

    Args:
        ext (string): Extension of temporal file

    Returns:
        (string) Path of temporary file
    """
    tf = tempfile.NamedTemporaryFile()
    return tf.name + ext


def ffmpeg(in_wav, out_wav):
    """ Run ffmpeg to convert in_wav into out_wav with codec pcm_s16le

    It guarantees that the output has the standard codec pcm_s16le

    TODO: Support to other formats (e.g. stereo)

    Args:
        in_wav (string): Path of input wav (any codec)
        out_wav (string): Path of output wav (codec pcm_s16le)
    """
    cmd = ("ffmpeg -y -i {0} -ac 1 " +
           "-acodec pcm_s16le -async 1 {1}").format(
        in_wav, out_wav)
    logging.debug(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        logging.error("Error running ffmpeg!")


def lame(in_wav, out_mp3, degree):
    """ Run mp3 compression with lame

    Args:
        in_wav (string): Path of input wav
        out_mp3 (string): Path of output mp3
        degree (int): Degree of compression (from 1 to 5)
    """
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
        logging.error("Error running lame!")


def apply_mp3(x, sr, degree):
    """ Apply mp3 compression to signal contained in numpy array

    Args:
        x (numpy array): Input signal
        sr (int): Sample rate
        degree (int): Degree of compression (from 1 to 5)

    Returns:
        (numpy array) Output signal
    """
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

    Args:
        x (numpy array): Input signal
        gain (float): Gain

    Returns:
        (numpy array): Output signal
    """
    logging.info("Apply gain %f dB" % gain)
    x = np.copy(x)
    x = x * (10 ** (gain / 20.0))
    x = np.minimum(np.maximum(-1.0, x), 1.0)
    return x


def trim_beginning(x, nsamples):
    """ Trim beginning of file

    Args:
        x (numpy array): Input signal
        nsamples (int): Number of samples to trim from the beginning

    Returns:
        (numpy array): Output signal
    """
    return x[nsamples:]


def apply_dr_compression(x, sr, degree):
    """ Apply dynamic range compression using sox

    Args:
        x (numpy array): Input signal
        sr (int): Sample rate
        degree (int): Degree of compression (from 1 to 3)

    Returns:
        (numpy array): Output signal
    """
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
        logging.error("Error running sox!")
    y, sr = lr.core.load(tmp_file_1, sr=sr, mono=True)
    remove_tmp_files([tmp_file_0, tmp_file_1])
    return y


def normalize(x, percentage=1.0):
    """ Normalize signal

    Args:
        x (numpy array): Input signal
        percentage (float): Percentage to full-scale to normalize

    Returns:
        (numpy array): Output signal
    """
    max_peak = np.max(np.abs(x))
    return x / max_peak * percentage


def apply_eq(x, sr, parameters):
    """ Apply equalization using sox

    Args:
        x (numpy array): Input signal
        sr (int): Sample rate
        parameters (string): Eq. parameters as 'freq(hz)//bw(hz)//gain(db)'

    Returns:
        (numpy array): Output signal
    """
    freq, bw, gain = map(int, parameters.split('//'))
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
        logging.error("Error running sox!")
    y, sr = lr.core.load(tmp_file_1, sr=sr, mono=True)
    remove_tmp_files([tmp_file_0, tmp_file_1])
    return y


def main(input_wav, degradations_list, output_wav):
    """ Apply degradations to input wav

    Args:
        input_wav (str): Path of input wav
        degradations_list (list of strings): List of degradations
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
