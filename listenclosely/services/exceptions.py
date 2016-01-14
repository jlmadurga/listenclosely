# -*- coding: utf-8 -*-
class MessageServiceBackendError(Exception):
    pass


class UnexpectedError(MessageServiceBackendError):
    """ Raised for unknown or unexpected errors. """
    pass


class ConfigurationError(MessageServiceBackendError):
    """
    Raised when an error in configuration is found in Message Service Backend
    """
    pass


class ConnectionError(MessageServiceBackendError):
    """
    Raised when Message Service Backend is not connected and some actions requires
    """
    pass


class AuthenticationError(MessageServiceBackendError):
    """
    Raised when Message Service Backend detects some authentication issue with the provider
    """
    pass
