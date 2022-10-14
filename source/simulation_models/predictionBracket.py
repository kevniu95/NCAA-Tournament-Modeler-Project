import sys
sys.path.insert(0, '../source/data_structures/')
sys.path.insert(0, '../data_structures/')

import numpy as np
import random
import math
from teams import Team, Teams, SpecificEntryImporter
from bracket import BracketEntry, Bracket
from predictions import Predictions, KagglePredictionsGenerator
    
class Game():
    """
    Describes a general game between two basketball teams
    - Contains information on two teams by ID
    - Retrieves predictions from object of Predictions class and simulates an outcome
    """
    def __init__(self, team1 : Team, team2 : Team):
        self.team1 : Team = team1
        self.team2 : Team = team2

        if self.team1 > self.team2:
            self.team1, self.team2 = self.team2, self.team1
        
    def _getTeamOneWinPctWith(self, inputObject : Predictions) -> float:
        predictions = inputObject.predictions
        id1 = self.team1.predId
        id2 = self.team2.predId
        return predictions[(id1, id2)]

    def getWinner(self, inputObject : Predictions) -> Team:
        team1wins = self._getTeamOneWinPctWith(inputObject)
        val = np.random.uniform(0, 1)
        if val < team1wins:
            return self.team1
        else:
            return self.team2
    
    def __str__(self) -> str:
        return f"{self.team1} vs. {self.team2}"

    def __repr__(self) -> str:
        return f"{self.team1} vs. {self.team2}"
        
class PredictionBracketEntry(BracketEntry):
    # TODO: Update so that assign first round is happening once 
    # per instance of this class
    # -And each call of getWinnerBracket() returns a new instance of 
    #   winner list
    # -Therefore self.round and self.winnerbracket aren't needed 
    #   anymore
    # 
    def __init__(self, index : int):
        super().__init__(index)
        self.team1 : Team = None
        self.team2 : Team = None
        self._game : Game = None
    
    def getWinner(self, predictionsObject : Predictions) -> Team:
        self.winner = self.game.getWinner(predictionsObject)
        return self.winner

    def addTeam(self, team : Team):
        if self.team1 is None:
            self.team1 = team
        elif self.team2 is None:
            if team < self.team1:
                self.team2 = self.team1
                self.team1 = team
            else:
                self.team2 = team
        else:
            print("Woops, no more teams can be added to this game!")
    
    @property
    def game(self) -> Game:
        if self._game:
            return self._game
        elif self.team1 and self.team2:
            self._game = Game(self.team1, self.team2)
            return self._game
        else:
            return
            
    @game.setter
    def game(self) -> None:
        print("The BracketEntry's game property cannot be reset! Please add teams to entry to instantiate a game!")
        return

class predictionBracket(Bracket):
    def __init__(self, inputObject : Predictions, teams : Teams = None, size : int = 64):
        super().__init__(size = size)
        self.teams : Teams = teams
        self.gameBracket : list[PredictionBracketEntry] = [None] * size # Ordered list of bracketEntries
        self.inputObject : Predictions = inputObject
        
        self._assignFirstRound()
    
    def _assignFirstRound(self):
        for num, i in enumerate(range(self.size // 2, self.size)):
            bracketEntry = PredictionBracketEntry(index = i)
            """
            Proper ordering of teams in bracket structure is ensured if
              Teams instantiated properly - see TeamImporter in teams module
              and its specific sub-classes for more information
            """
            team1 : Team = self.teams.teams[2 * num]
            team2 : Team = self.teams.teams[2 * num + 1]
            bracketEntry.addTeam(team1)
            bracketEntry.addTeam(team2)
            self.gameBracket[i] : PredictionBracketEntry = bracketEntry
    
    @property
    def round(self) -> int:
        """
        Maintains state indicating which round (indexing from 1) is currently 
        being processed
            - Remember self.gameBracket is filled from back to front of array
                - This means at start of first round, first non-null value is index 32
                    - So round returned will be "1"
                - In second round, first non-null value is index 16
                    - So round returned will be "2"
        """
        ctr = 0
        for num, i in enumerate(self.gameBracket):
            if i is not None:
                return math.log(self.size // ctr, 2)
            ctr += 1
        
    @round.setter
    def round(self, value):
        print("Round is an internally-determined property and cannot be reset!")
        return
    
    def _simulateRound(self):
        """
        Simulates current round by finding all BracketEntries associated with round
            and simulating games
        Advances winners of games in next round
        """
        thisRoundSize = self.size / (2 ** self.round) 
        
        if (thisRoundSize == int(thisRoundSize) and (thisRoundSize % 2 == 0)) or (thisRoundSize == 1):
            thisRoundSize = int(thisRoundSize)
        else:
            print("Hmmm, the size of this round should be an even integer!")
            raise ValueError
                
        for gameIndex in range(thisRoundSize, thisRoundSize * 2):
            bracketEntry = self.gameBracket[gameIndex]
            
            bracketEntryWinner = bracketEntry.getWinner(self.inputObject)
            bracketEntryNextIndex = bracketEntry.getNextGameIndex()
            self.winnerBracket[gameIndex] = bracketEntryWinner.bracketId
            
            if thisRoundSize > 1:
                self._insertBracketEntry(bracketEntryNextIndex)
                nextEntry = self.gameBracket[bracketEntryNextIndex]
                nextEntry.addTeam(bracketEntryWinner)
        return self.winnerBracket
    
    def _insertBracketEntry(self, index):
        if self.gameBracket[index] is None:
            self.gameBracket[index] = PredictionBracketEntry(index)
    
    def getWinnerBracket(self, reset = False):
        while self.winnerBracket[1] is None:
            winnerBracket = self._simulateRound()
            self.winnerBracket[0] = -1
            self.winnerBracket = np.array(self.winnerBracket)
        if reset:
            self.bracketReset()
        return winnerBracket
    
    def bracketReset(self):
        self.gameBracket = [None] * self.size
        self.winnerBracket = [None] * self.size
        self.assignFirstRound()

if __name__ == "__main__":
    # A. Import Predictions
    generator = KagglePredictionsGenerator('../data/kaggle_predictions/seedPreds2022.csv')
    predictions = Predictions(generator)
    # print(predictions.predictions)
    
    # B. Import Teams
    entryImporter = SpecificEntryImporter()
    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../Data/MTeams.csv')
    # print(teams.teams)
    
    # C. Create Bracket
    testBracket = predictionBracket(inputObject = predictions, teams = teams, size = 64)
    # print(testBracket.gameBracket)
    # print(testBracket.winnerBracket)

    # D. Simulate Tournament
    print(testBracket.getWinnerBracket(reset = False))
    # print(testBracket.gameBracket)
    # print()
    # print(testBracket.winnerBracket)
    