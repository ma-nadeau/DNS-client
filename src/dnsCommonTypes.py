from enum import Enum
from typing import NamedTuple

class recordType(Enum):
    A = 1
    MX = 2
    CNAME = 5
    NS = 15

class IPV4(NamedTuple):
    a : int
    b : int
    c : int
    d : int
