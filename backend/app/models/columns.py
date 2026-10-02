from enum import StrEnum

from sqlalchemy import Enum, Numeric

ENUM_LENGTH = 32
MONEY_PRECISION = 10
MONEY_SCALE = 4


def enum_column(enum_cls: type[StrEnum]) -> Enum:
    return Enum(
        enum_cls,
        native_enum=False,
        length=ENUM_LENGTH,
        values_callable=lambda members: [member.value for member in members],
    )


def money_column() -> Numeric[float]:
    return Numeric(MONEY_PRECISION, MONEY_SCALE, asdecimal=False)
