class TransperthException(Exception):
    pass


class InvalidStopNumber(TransperthException):
    pass


class InvalidDirection(TransperthException):
    pass


class InvalidStep(TransperthException):
    pass


class NoFareData(TransperthException):
    pass
