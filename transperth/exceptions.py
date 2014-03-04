class TransperthException(Exception):
    """
    Base exception for all exceptions thrown by this library
    """


class InvalidStopNumber(TransperthException):
    """
    Thrown when the provided stop number is not a five digit number
    """


class InvalidDirection(TransperthException):
    """
    Thrown when the provided direction is neither to nor from
    """


class InvalidStep(TransperthException):
    """
    Thrown when a step is not one of 'bus', 'walk', or 'train'
    """


class NoFareData(TransperthException):
    """
    Thrown when transperth does not provide data from which we
    can assertain the fare for a route
    """


class NotLoggedIn(TransperthException):
    """
    Raised when the library detects that the session has expired
    """


class LoginFailed(NotLoggedIn):
    """
    Thrown when a login attempt fails
    """
