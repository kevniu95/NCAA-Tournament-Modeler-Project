# True Model

import numpy as np
import random
import math
from teams import Teams, specificEntryImporter
from bracket import BracketEntry, Bracket
from predictions import Predictions, KagglePredictionsGenerator
    
class Game():
    """
    Describes a general game between two basketball teams
    - Contains information on two teams by ID
    - Retrieves predictions from object of Predictions class and simulates an outcome
    """
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

        if self.team1 > self.team2:
            self.team1, self.team2 = self.team2, self.team1
        
    def _getPredictions(self, inputObject):
        return inputObject.predictions
    
    def _getTeamOneWinPctWith(self, inputObject):
        predictions = self._getPredictions(inputObject)
        id1 = self.team1.predId
        id2 = self.team2.predId
        return predictions[(id1, id2)]

    def simulateWith(self, inputObject):
        team1wins = self._getTeamOneWinPctWith(inputObject)
        val = np.random.uniform(0, 1)
        if val < team1wins:
            return self.team1
        else:
            return self.team2
    
    def __str__(self):
        return f"{self.team1} vs. {self.team2}"

    def __repr__(self):
        return f"{self.team1} vs. {self.team2}"
        
class predictionBracketEntry(BracketEntry):
    def __init__(self, index):
        super().__init__(index)
        self.team1 = None
        self.team2 = None
        self._game = None
    
    def getWinner(self, predictionsObject):
        self.winner = self.game.simulateWith(predictionsObject)
        return self.winner

    def addTeam(self, team):
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
    def game(self):
        if self._game is not None:
            return self._game
        elif self.team1 is not None and self.team2 is not None:
            self._game = Game(self.team1, self.team2)
            return self._game
        else:
            return
            
    @game.setter
    def game(self):
        print("The BracketEntry's game property cannot be reset! Please add teams to entry to instantiate a game!")
        return

class predictionBracket(Bracket):
    def __init__(self, inputObject, teams = None, size = 64):
        super().__init__(size = size)
        
        self.teams = teams
        # Game bracket, predictionObject
        self.gameBracket = [None] * size # Ordered list of bracketEntries
        self.inputObject = inputObject
        # Assign first round
        self.assignFirstRound()
    
    def assignFirstRound(self, random = False):
        if random or self.teams is None:
            self.randomlyFillFirstRound()
        else:
            self.assignByTeamList()
    
    def assignByTeamList(self):
        for num, i in enumerate(range(32, 64)):
            bracketEntry = predictionBracketEntry(i)
            team1 = self.teams.teams[2 * num]
            team2 = self.teams.teams[2 * num + 1]
            bracketEntry.addTeam(team1)
            bracketEntry.addTeam(team2)
            self.gameBracket[i] = bracketEntry
    
    def randomlyFillFirstRound(self):
        '''
        Randomly fills first round based on distinct teams available in
        the Predictions dataset
        '''
        preds = self.inputObject.predictions
        listOfTeams = list(set([i[0] for i in preds.keys()]))[:64]
        random.shuffle(listOfTeams)
        for num, i in enumerate(range(32, 64)):
            idx = i - 32
            teamA = listOfTeams[2 * idx]
            teamB = listOfTeams[2 * idx + 1]
            bracketEntry = predictionBracketEntry(i)
            bracketEntry.addTeam(teamA)
            bracketEntry.addTeam(teamB)
            self.gameBracket[i] = bracketEntry

    @property
    def round(self):
        """
        Maintains state indicating which round is currently being processed
        -Gets first non-null value at start of each round, which is last-processed round
            -Which basically gives number of games yet to be processed
            -64 / Games-to-Be-processed incerases linearly with each round so can use
                -To get the round number
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
            self.winnerBracket[gameIndex] = bracketEntryWinner 
            
            if thisRoundSize > 1:
                self._insertBracketEntry(bracketEntryNextIndex)
                nextEntry = self.gameBracket[bracketEntryNextIndex]
                nextEntry.addTeam(bracketEntryWinner)
    
    def _insertBracketEntry(self, index):
        if self.gameBracket[index] is None:
            self.gameBracket[index] = predictionBracketEntry(index)
    
    def getWinnerBracket(self, reset = True):
        while self.winnerBracket[1] is None:
            self._simulateRound()
        if reset:
            self.bracketReset()
        return self.winnerBracket
    
    def bracketReset(self):
        self.gameBracket = [None] * self.size
        self.winnerBracket = [None] * self.size
        self.randomlyFillFirstRound()

if __name__ == "__main__":
    # A. Import Predictions
    generator = KagglePredictionsGenerator('seedPreds2022.csv')
    predictions = Predictions(generator)
    # print(predictions.predictions)
    
    # B. Import Teams
    entryImporter = specificEntryImporter()
    teams = Teams(bracketImporter = entryImporter)
    teams.setPredIds(file = 'MTeams.csv')
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
    