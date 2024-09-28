from enum import Enum
from typing import NamedTuple


class recordType(Enum):
    A = 1
    NS = 2
    CNAME = 5
    MX = 15

    @classmethod
    def from_value(cls, value: int):
        return cls(value)


class IPV4(NamedTuple):
    a: int
    b: int
    c: int
    d: int
