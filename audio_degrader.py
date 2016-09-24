#!/usr/bin/python
import warnings
warnings.filterwarnings("ignore")  # noqa
import argparse
import re
import librosa as lr
import numpy as np
import subprocess
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG)

TEST_WAV = './test_files/test.wav'

IMPULSE_RESPONSES = [
    'smartphone_mic',
    'classroom']

SOUNDS = ['white-noise',
          'brown-noise',
          'ambience-pub',
          'vinyl',
          'hum',
          'applause']

RUBBERBAND_PROCESSINGS = ['time-stretching', 'pitch-shifting']


def add_noise(x, noise_name, snr):
    """ Add noise to x

    Args:
        x (numpy array): Input signal
        noise_name (str): Name of noise
        snr (float): SNR of output sound
    """
    noise_path = './sounds/%s.wav' % noise_name
    z, sr = lr.core.load(noise_path, sr=8000, mono=True)
    while z.shape[0] < x.shape[0]:
        z = np.concatenate((z, z), axis=0)
    z = z[0: x.shape[0]]
    rms_z = np.sqrt(np.mean(np.power(z, 2)))
    logging.debug("rms_z: %f" % rms_z)
    rms_x = np.sqrt(np.mean(np.power(x, 2)))
    logging.debug("rms_x: %f" % rms_x)
    snr_linear = 10 ** (snr / 20.0)
    logging.debug("snr , snr_linear: %f, %f" % (snr, snr_linear))
    noise_factor = rms_x / rms_z / snr_linear
    logging.debug("y = x  + z * %f" % noise_factor)
    y = x + z * noise_factor
    rms_y = np.sqrt(np.mean(np.power(y, 2)))
    y = y * rms_x / rms_y
    return y


def test_add_noise():
    x, sr = lr.core.load(TEST_WAV, sr=8000, mono=True)
    y = add_noise(x, 'white-noise', -6)
    lr.output.write_wav(
        TEST_WAV.replace('.wav', '_wnoise-6.wav'),
        y, 8000, norm=False)
    y = add_noise(x, 'white-noise', 20)
    lr.output.write_wav(
        TEST_WAV.replace('.wav', '_wnoise20.wav'),
        y, 8000, norm=False)


def convolve(x, ir_name, level=1.0):
    """ Apply convolution to x using impulse response given
    """
    logging.info('Convolving with %s and level %f' % (ir_name, level))
    x = np.copy(x)
    ir_path = './sounds/ir_{0}.wav'.format(ir_name)
    ir, sr = lr.core.load(ir_path, sr=8000, mono=True)
    return np.convolve(x, ir, 'full')[0:x.shape[0]] * level + x * (1 - level)


def test_convolve():
    x, sr = lr.core.load(TEST_WAV, sr=8000, mono=True)
    y = convolve(x, 'classroom', 0.6)
    lr.output.write_wav(
        TEST_WAV.replace('.wav', '_classroom.wav'),
        y, 8000, norm=False)
    y = convolve(x, 'smartphone_mic')
    lr.output.write_wav(
        TEST_WAV.replace('.wav', '_smartphone_mic.wav'),
        y, 8000, norm=False)


def tmp_path(ext=''):
    tf = tempfile.NamedTemporaryFile()
    return tf.name + ext


def test_tmp_path():
    print tmp_path()
    print tmp_path()


def ffmpeg(in_wav, out_wav):
    cmd = ("ffmpeg -y -i {0} -ac 1 -ar 8000 " +
           "-acodec pcm_s16le -async 1 {1}").format(
        in_wav, out_wav)
    logging.debug(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"


def test_ffmpeg():
    ffmpeg(TEST_WAV, TEST_WAV.replace('.wav', '_ffmpeg.wav'))


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


def test_lame():
    lame(TEST_WAV, TEST_WAV.replace('.wav', '_1.mp3'), 1)
    lame(TEST_WAV, TEST_WAV.replace('.wav', '_2.mp3'), 2)
    lame(TEST_WAV, TEST_WAV.replace('.wav', '_3.mp3'), 3)
    lame(TEST_WAV, TEST_WAV.replace('.wav', '_4.mp3'), 4)
    lame(TEST_WAV, TEST_WAV.replace('.wav', '_5.mp3'), 5)


def apply_mp3(x, degree):
    logging.info("MP3 compression. Degree %d" % degree)
    tmp_file_0 = tmp_path('.wav')
    tmp_file_1 = tmp_path('.wav')
    tmp_file_2 = tmp_path('.mp3')
    tmp_file_3 = tmp_path('.wav')
    lr.output.write_wav(tmp_file_0, x, 8000, norm=False)
    ffmpeg(tmp_file_0, tmp_file_1)
    lame(tmp_file_1, tmp_file_2, degree)
    ffmpeg(tmp_file_2, tmp_file_3)
    y, sr = lr.core.load(tmp_file_3, sr=8000, mono=True)
    return y


def apply_gain(x, gain):
    """ Apply gain to x
    """
    logging.info("Apply gain %f dB" % gain)
    x = np.copy(x)
    x *= np.minimum(np.maximum(-1.0, 10 ** (gain / 20.0)), 1.0)
    return x


def test_apply_gain():
    print "Testing apply_gain()"
    # Test file reading
    x, sr = lr.core.load(TEST_WAV, sr=8000, mono=True)
    print "Length of file: %d samples" % len(x)
    print "Mean amplitude before: %f" % np.mean(np.abs(x))

    y = apply_gain(x, -6)
    print "Mean amplitude after -6dB: %f" % np.mean(np.abs(y))
    gain_test_wav = TEST_WAV.replace('.wav', '_gain-6.wav')
    lr.output.write_wav(gain_test_wav, y, 8000, norm=False)

    y = apply_gain(x, 6)
    print "Mean amplitude after +6dB: %f" % np.mean(np.abs(y))
    gain_test_wav = TEST_WAV.replace('.wav', '_gain+6.wav')
    lr.output.write_wav(gain_test_wav, y, 8000, norm=False)


def apply_rubberband(x, time_stretching_ratio=1.0, pitch_shifting_ratio=1.0):
    """ Use rubberband tool to apply time stretching and pitch shifting

    Args:
        x (numpy array): Samples of input signal
        time_stretching_ratio (float): Ratio of time stretching
        pitch_shifting_ratio (float): Ratio of pitch shifting
    Returns:
        (numpy array): Processed audio
    """
    logging.info("Applying rubberband. ts_ratio={0}, ps_ratio={1}".format(
        time_stretching_ratio,
        pitch_shifting_ratio))
    tmp_file_1 = tmp_path()
    tmp_file_2 = tmp_path()
    lr.output.write_wav(tmp_file_1, x, 8000, norm=False)
    cmd = "rubberband -c 1 -t {0} -f {1} {2} {3}".format(
        time_stretching_ratio,
        pitch_shifting_ratio,
        tmp_file_1,
        tmp_file_2)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"
    y, sr = lr.core.load(tmp_file_2, sr=8000, mono=True)
    return y


def test_apply_rubberband():
    x, sr = lr.core.load(TEST_WAV, sr=8000, mono=True)
    t_x = apply_rubberband(x, time_stretching_ratio=0.5)
    p_x = apply_rubberband(x, pitch_shifting_ratio=1.2)
    lr.output.write_wav(TEST_WAV.replace('.wav', '_timestr.wav'),
                        t_x, 8000, norm=False)
    lr.output.write_wav(TEST_WAV.replace('.wav', '_pitchshift.wav'),
                        p_x, 8000, norm=False)


def compress(x, CT, CS):
    # CT: Threshold
    # CS: Slope (1 / ratio)
    logging.info("Applying compression: CT={0}, CS={1}".format(CT, CS))
    # Dynamic range compressor :)
    # see DAFX book, second edition, page 112 (compexp.m file)
    # http://ant-s4.unibw-hamburg.de/dafx/DAFX_Book_Page_2nd_edition/chapter4.html  # noqa
    ES = 1.0
    ET = CT
    y = np.copy(x)
    tav = 0.01
    at = 0.03
    rt = 0.003
    delay = 150
    xrms = 0
    g = 1
    delay = 150
    _buffer = np.zeros(delay)
    for i in range(0, x.shape[0]):
        xrms = (1 - tav) * xrms + tav * x[i] * x[i]
        X = 10 * np.log10(xrms)
        G = np.min([0, CS * (CT - X), ES * (ET - X)])
        f = 10 ** (G / 20.0)
        if f < g:
            coeff = at
        else:
            coeff = rt
        g = (1 - coeff) * g + coeff * f
        y[i] = g * _buffer[-1]
        _buffer = np.insert(_buffer[:-1], 0, x[i])
    return y


def test_compress():
    x, sr = lr.core.load(TEST_WAV, sr=8000, mono=True)
    y = apply_gain(compress(x, -30, 0.25), 3)
    tmpfile = tmp_path()
    lr.output.write_wav(tmpfile,
                        y, 8000, norm=False)
    ffmpeg(tmpfile, TEST_WAV.replace('.wav', '_dr.wav'))


def apply_slow_dr_compression(x, degree):
    # It uses the sample-by-sample compressor function, which is slow...
    parameters = []
    parameters.append({
        'x': x,
        'CT': -30,
        'CS': 0.25
    })
    parameters.append({
        'x': x,
        'CT': -40,
        'CS': 0.2
    })
    parameters.append({
        'x': x,
        'CT': -50,
        'CS': 0.15
    })
    return compress(**parameters[int(degree) - 1])


def apply_dr_compression(x, degree):
    tmpfile_1 = tmp_path('.wav')
    tmpfile_2 = tmp_path('.wav')
    lr.output.write_wav(tmpfile_1,
                        x, 8000, norm=False)
    if degree == 1:
        cmd = "sox {0} {1} compand 0.1,0.20 -40,-10,-30 5"
    elif degree == 2:
        cmd = "sox {0} {1} compand 0.01,0.20 -50,-50,-40,-30,-40,-10,-30 12"
    elif degree == 3:
        cmd = "sox {0} {1} compand 0.01,0.1 -70,-60,-70,-30,-70,0,-70 45"
    cmd = cmd.format(tmpfile_1, tmpfile_2)
    logging.info(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"
    y, sr = lr.core.load(tmpfile_2, sr=8000, mono=True)
    return y


def normalize(x, percentage=1.0):
    max_peak = np.max(np.abs(x))
    return x / max_peak * percentage


def test_apply_dr_compression():
    x, sr = lr.core.load(TEST_WAV, sr=8000, mono=True)
    for degree in [1, 2, 3]:
        y = apply_dr_compression(x, degree)
        tmpfile = tmp_path()
        lr.output.write_wav(tmpfile,
                            y, 8000, norm=False)
        ffmpeg(tmpfile, TEST_WAV.replace('.wav', '_dr_%d.wav' % degree))


def degradation_value(string):
    """ True if it is a degradation,value string
    """
    m = None
    if string.split(',')[0] == 'mp3':
        m = re.match('mp3(,[1-5])?$', string)
    if string.split(',')[0] == 'eq':
        m = re.match(
            'eq,[0-9]*\.?[0-9]+/[0-9]*\.?[0-9]+/[-+]?[0-9]*\.?[0-9]+$', string)
    if string.split(',')[0] == 'gain':
        m = re.match('gain,[-+]?[0-9]*\.?[0-9]+$', string)
    if string.split(',')[0] == 'normalize':
        m = re.match('normalize,[0-9]*\.?[0-9]+$', string)
    if string.split(',')[0] in SOUNDS:
        m = re.match(
            '({0}),[-+]?[0-9]*\.?[0-9]+$'.format('|'.join(SOUNDS)),
            string)
    if string.split(',')[0] == 'ambience-pub':
        m = re.match('ambience-pub,[-+]?[0-9]*\.?[0-9]+$', string)
    if string.split(',')[0] == 'dr-compression':
        m = re.match('dr-compression,[1-5]$', string)
    if string.split(',')[0] in IMPULSE_RESPONSES:
        m = re.match(
            '({0}),[-+]?[0-9]*\.?[0-9]+$'.format('|'.join(IMPULSE_RESPONSES)),
            string)
    if string.split(',')[0] in RUBBERBAND_PROCESSINGS:
        m = re.match(
            '({0}),[-+]?[0-9]*\.?[0-9]+$'.format(
                '|'.join(RUBBERBAND_PROCESSINGS)),
            string)
    if m is None:
        msg = "%r has not right format. See help." % string
        raise argparse.ArgumentTypeError(msg)
    return string


def apply_eq(x, value):
    freq, bw, gain = map(int, value.split('/'))
    logging.info("Equalizing. f=%f, bw=%f, gain=%f" % (freq, bw, gain))
    tmpfile_1 = tmp_path('.wav')
    tmpfile_2 = tmp_path('.wav')
    lr.output.write_wav(tmpfile_1,
                        x, 8000, norm=False)
    cmd = "sox {0} {1} equalizer {2} {3} {4}".format(
        tmpfile_1,
        tmpfile_2,
        freq,
        bw,
        gain)
    logging.info(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR!"
    y, sr = lr.core.load(tmpfile_2, sr=8000, mono=True)
    return y


def test_apply_eq():
    x, sr = lr.core.load(TEST_WAV, sr=8000, mono=True)
    y = apply_eq(x, '500;50;30')
    tmpfile = tmp_path()
    lr.output.write_wav(tmpfile,
                        y, 8000, norm=False)
    ffmpeg(tmpfile, TEST_WAV.replace('.wav', '_eq.wav'))


def test_all():
    test_apply_eq()
    test_apply_dr_compression()
    test_compress()
    test_add_noise()
    test_apply_rubberband()
    test_convolve()
    test_tmp_path()
    test_lame()
    test_ffmpeg()
    test_apply_gain()


def main(input_wav, degradations_list, output_wav, testing=False):
    """ Apply degradations to input wav

    Args:
        input_wav (str): Path of input wav
        degradations_list (list): List of degradations (e.g. ['mp3,1'])
        output_wav (str): Path of outpu wav
        testing (bool): True for testing mode
    """
    if testing:
        test_all()
        return
    x, sr = lr.core.load(input_wav, sr=8000, mono=True)
    for degradation in degradations_list:
        degradation_name, value = degradation.split(',')
        if degradation_name == 'mp3':
            x = apply_mp3(x, float(value))
        if degradation_name == 'gain':
            x = apply_gain(x, float(value))
        if degradation_name == 'normalize':
            x = normalize(x, float(value))
        if degradation_name in SOUNDS:
            x = add_noise(x, degradation_name, float(value))
        if degradation_name in IMPULSE_RESPONSES:
            x = convolve(x, degradation_name, float(value))
        if degradation_name == 'time-stretching':
            x = apply_rubberband(x, time_stretching_ratio=float(value))
        if degradation_name == 'pitch-shifting':
            x = apply_rubberband(x, pitch_shifting_ratio=float(value))
        if degradation_name == 'dr-compression':
            x = apply_dr_compression(x, degree=float(value))
        if degradation_name == 'eq':
            x = apply_eq(x, value)
    tmp_file = tmp_path()
    lr.output.write_wav(tmp_file, x, 8000, norm=False)
    ffmpeg(tmp_file, output_wav)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Process audio with a sequence of degradations
    Accepted degradadations:
        mp3,quality: Mp3 compression. Value is quality (1-5)
        gain,db: Gain. Value is dB (e.g. gain,-20.3).
        normalize,percentage: Normalize. Percentage in 0.0-1.0 (1.0=full range)
        white-noise,snr: Add white noise. SNR in dB.
        brown-noise,snr: Add brown noise. SNR in dB.
        ambience-pub,snr: Add pub ambience. SNR in dB.
        vinyl,snr: Add vinyl noise. SNR in dB.
        hum,snr: Add hum noise. SNR in dB.
        applause,snd: Add applause noise. SNR in dB.
        smartphone_mic,level: Smartphone_mic-like sonority. Level 0.0-1.0
        classroom,level: Classroom-like reverb. Level 0.0-1.0
        dr-compression,degree: Dynamic range compression. Degree in (1-3).
        time-stretching,ratio: Apply time streting. Ratio in from -9.99 to 9.99
        pitch-shifting,ratio: Apply time streting. Ratio in -9.99 to 9.99
        eq,freq_hz/bw_hz/gain_db: Apply equalization with sox.
        """,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Note: all audios are transcoded to mono, 8KHz, pcm_s16le")

    parser.add_argument('input_wav', metavar='input_wav',
                        type=str,
                        help='Input audio wav')
    parser.add_argument('degradation', metavar='degradation,value',
                        type=degradation_value,
                        nargs='*',
                        help='List of sequential degradations')
    parser.add_argument('output_wav', metavar='output_wav',
                        type=str,
                        help='Output audio wav')
    parser.add_argument('--testing', action='store_true',
                        dest='testing',
                        help='Output audio wav')

    args = vars(parser.parse_args())
    main(args['input_wav'],
         args['degradation'],
         args['output_wav'],
         args['testing'])
