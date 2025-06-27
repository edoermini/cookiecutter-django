from rest_framework.serializers import ValidationError


class UserDoesNotExistError(ValidationError):
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = "User with this email does not exist."
        super().__init__(detail, code)

class UserNotActiveError(ValidationError):
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = "User is not active."
        super().__init__(detail, code)

class InvalidTokenError(ValidationError):
    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = "Invalid Token."
        super().__init__(detail, code)
