from collections import namedtuple
from dataclasses import dataclass

Point = namedtuple("Point", ["x", "y"])


@dataclass
class GamePoint:
    owner: int = None
    captured: list = None
    border: bool = False


@dataclass
class GameField:
    field: [[GamePoint]]
    players: list = None
    loops: dict = None
    empty_loops: dict = None
    score: dict = None
