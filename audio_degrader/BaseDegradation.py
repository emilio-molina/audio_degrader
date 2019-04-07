from abc import ABCMeta, abstractmethod
from utils import NAME_SEP, PARAMETERS_SEP, DESCRIPTION_SEP


class Degradation(object):
    """ Abstract class to implement degradations """

    __metaclass__ = ABCMeta
    name = "AbstractDegradation"  # Name of degradation
    description = "Abstract degradation"  # Short description of degradation
    parameters_info = [('param1', 1.0, 'Parameter one [unit1]'),
                       ('param2', 0.5, 'Parameter two [unit2]')]
    """ list: Information about each parameter.

    The list contains tuples with the following info:
        [(param_name, example_value, description),...]
    """

    def __str__(self):
        return self.name

    def set_parameters_values(self, parameters_values={}):
        """ Set all parameters before calling apply method
        """
        self.parameters_values = parameters_values

    @abstractmethod
    def apply(self, audio_file):
        """ Process audio_file.samples field

        Args:
            audio_file (g): Audio file to be processed
        """
        pass


class DegradationUsageDocGenerator(object):
    """ It generates documentation strings about a given degradation """

    base_indent = " " * 8
    indent = " " * 12

    @staticmethod
    def get_degradation_help_header(degradation):
        """ Generate help header given a degradation

        e.g. gain,value:

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Help header
        """
        help_str = "    {0}".format(degradation.name)
        has_params = len(degradation.parameters_info) > 0
        if has_params:
            help_str += "{0}".format(NAME_SEP)
        help_str += PARAMETERS_SEP.join(
            map(lambda x: x[0], degradation.parameters_info))
        help_str += DESCRIPTION_SEP
        return help_str

    @staticmethod
    def get_degradation_help_params_info(degradation):
        """ Generate parameters info given a degradation

        e.g. parameters:
                 value: Gain value [dB]

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Parameters information
        """
        base_indent = DegradationUsageDocGenerator.base_indent
        indent = DegradationUsageDocGenerator.indent
        help_params_info_str = "\n{0}parameters:".format(base_indent)
        for p in degradation.parameters_info:
            help_params_info_str += "\n{0}{1}{2}{3}".format(
                indent, p[0], DESCRIPTION_SEP, p[2])
        return help_params_info_str

    @staticmethod
    def get_degradation_help_example(degradation):
        """ Generate help example given a degradation

        e.g. example:
                 gain,6

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Help example
        """
        base_indent = DegradationUsageDocGenerator.base_indent
        indent = DegradationUsageDocGenerator.indent
        help_example_str = "\n{0}example:".format(base_indent)
        help_example_str += "\n{0}{1}".format(indent,
                                              degradation.name)
        has_params = len(degradation.parameters_info) > 0
        if has_params:
            help_example_str += "{0}".format(NAME_SEP)
        help_example_str += PARAMETERS_SEP.join(
            map(lambda x: "{0}".format(x[1]), degradation.parameters_info))
        return help_example_str

    @staticmethod
    def get_degradation_help_description(degradation):
        """ Generate help description given a degradation

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Degradation description
        """
        return degradation.description

    @staticmethod
    def get_degradation_help(degradation):
        """ Generate complete help for a given degradation

        e.g. gain,value: Apply gain expressed in dBs
             parameters:
                 value: Gain value [dB]
             example:
                 gain,6

        Args:
            degradation (Degradation): Input degradation
        Returns:
            (string): Degradation help docstring
        """
        help_str = (
            DegradationUsageDocGenerator.get_degradation_help_header(
                degradation) +
            DegradationUsageDocGenerator.get_degradation_help_description(
                degradation) +
            DegradationUsageDocGenerator.get_degradation_help_params_info(
                degradation) +
            DegradationUsageDocGenerator.get_degradation_help_example(
                degradation))
        return help_str
