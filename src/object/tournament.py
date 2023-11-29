from typing import List, Tuple

from src.object.individual import Individual


class Tournament:
    def __init__(
        self,
        tourn_id: int,
        packets: str,
        headers: List[List[str]],
        round_scores: List[Tuple[List[str], List[str]]],
        individuals: List[Individual],
    ):
        self.id = tourn_id
        self.packets = packets
        self.headers = headers
        self.round_scores = round_scores
        self.individuals = individuals
