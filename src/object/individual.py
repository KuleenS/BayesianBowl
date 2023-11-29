from typing import List, Tuple

class Individual:
    def __init__(self, team: str, id: int, header: List[str], scores: List[Tuple[List[str], List[str]]]):
        self.team = team
        self.id = id 
        self.header = header
        self.scores = scores