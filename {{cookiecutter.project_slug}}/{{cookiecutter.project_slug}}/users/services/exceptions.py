class TokenExpiredError(Exception):
    def __init__(self, message=None):

        if message is None:
            message = "Token expired."

        super().__init__(message)

class TokenAlreadyUsedError(Exception):
    def __init__(self, message=None):

        if message is None:
            message = "Token already used"

        super().__init__(message)

class InvalidTokenTypeError(Exception):
    def __init__(self, message=None):

        if message is None:
            message = "Wrong token type."
        super().__init__(message)
