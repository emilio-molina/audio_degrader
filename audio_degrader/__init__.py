from audio_degrader import main
from audio_degrader import mix_with_sound, convolve, ffmpeg
from audio_degrader import lame, apply_gain
from audio_degrader import apply_eq, tmp_path, remove_tmp_files
from audio_degrader import apply_dr_compression
from AudioFile import AudioFile
from Degradations import DegradationTrim
from Degradations import DegradationMp3
from Degradations import DegradationGain
from Degradations import DegradationNormalization
from Degradations import DegradationMix
from Degradations import DegradationConvolution
from Degradations import DegradationDynamicRangeCompression
from Degradations import DegradationSpeed
from Degradations import DegradationTimeStretching
from Degradations import DegradationPitchShifting


__all__ = ["main",
           "mix_with_sound",
           "convolve",
           "ffmpeg",
           "lame",
           "apply_gain",
           "apply_eq",
           "tmp_path",
           "remove_tmp_files",
           "apply_dr_compression",
           "AudioFile",
           "DegradationTrim",
           "DegradationMp3",
           "DegradationGain",
           "DegradationNormalization",
           "DegradationMix",
           "DegradationConvolution",
           "DegradationDynamicRangeCompression",
           "DegradationSpeed",
           "DegradationTimeStretching",
           "DegradationPitchShifting"]
