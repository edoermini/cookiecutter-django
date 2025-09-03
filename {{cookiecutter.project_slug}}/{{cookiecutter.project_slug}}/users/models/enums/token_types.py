from enum import IntEnum


class TokenTypes(IntEnum):
    ACTIVATION = 0
    PASSWORD_RESET = 1

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
