PARAMETER_SEP = "//"


class ParametersParser:
    def __init__(self, degradations):
        self.degradations = degradations

    def get_help(self):
        print self.degradations[0]
        return self.degradations[0].get_help()
