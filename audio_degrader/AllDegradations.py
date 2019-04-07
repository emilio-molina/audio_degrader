from DegradationConvolution import DegradationConvolution
from DegradationDynamicRangeCompression import \
        DegradationDynamicRangeCompression
from DegradationGain import DegradationGain
from DegradationMix import DegradationMix
from DegradationMp3 import DegradationMp3
from DegradationNormalization import DegradationNormalization
from DegradationPitchShifting import DegradationPitchShifting
from DegradationResample import DegradationResample
from DegradationSpeed import DegradationSpeed
from DegradationTimeStretching import DegradationTimeStretching
from DegradationTrim import DegradationTrim
from DegradationEqualization import DegradationEqualization


ALL_DEGRADATIONS = {
    DegradationTrim.name: DegradationTrim,
    DegradationMp3.name: DegradationMp3,
    DegradationGain.name: DegradationGain,
    DegradationNormalization.name: DegradationNormalization,
    DegradationMix.name: DegradationMix,
    DegradationResample.name: DegradationResample,
    DegradationConvolution.name: DegradationConvolution,
    DegradationSpeed.name: DegradationSpeed,
    DegradationPitchShifting.name: DegradationPitchShifting,
    DegradationTimeStretching.name: DegradationTimeStretching,
    DegradationEqualization.name: DegradationEqualization,
    DegradationDynamicRangeCompression.name: DegradationDynamicRangeCompression
}
