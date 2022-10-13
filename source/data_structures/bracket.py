from multiprocessing.sharedctypes import Value
from abc import abstractmethod
    
class BracketEntry():
    """
    Wraps object of Game class in a BracketEntry
    -Takes teams one by one and instantiates a game 
        when two teams added to BracketEntry object
    -Identifies winner of game
    -Identifies next game in bracket (where winner advances to)
    """
    def __init__(self, index : int):
        self.index : int = index
        self.winner : str = None
        
    @abstractmethod
    def getWinner(self) -> str:
        pass
    
    def getNextGameIndex(self) -> int:
        return self.index // 2

    def __str__(self) -> str:
        return f"{self.index}: {self.game}"
    
    def __repr__(self) -> str:
        return f"{self.index}: {self.game}"


class Bracket():
    """"
    Abstract base class that contains 
        -size: number of teams participating in tournament
        -winnerBracket: An array of "winners" for each of the (size - 1) games played in th tournament
    """
    def __init__(self, size : int = 64):
        self.size : int = size
        self.winnerBracket : list[int] = [None] * size
        
    @abstractmethod
    def getWinnerBracket(self) -> list[int]:
        pass
    
    