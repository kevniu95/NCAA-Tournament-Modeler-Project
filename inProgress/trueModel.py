# True Model

from multiprocessing.sharedctypes import Value
import numpy as np
from abc import ABC, abstractmethod
import random
import math

class PredictionsGenerator():
    # << Predictions Generator >>
    def __init__(self, fileName):
        self.file = fileName
        self.probabilities = self.generateProbabilities()
        
    @abstractmethod
    def generateProbabilities(self):
        pass

class KagglePredictionsGenerator(PredictionsGenerator):
    # Concrete for <<PredictionsGenerator>>
    # KNOW: Kaggle Input Data
    # Do: Produce dictionary to be passed to be GamePredictions class
        # key              :   value
        # (teamid, teamid) :   0.5
    def __init__(self, fileName):
        super().__init__(fileName)
        
    def generateProbabilities(self):
        probDictionary = {}
        with open(self.file, 'r') as file:
            for num, row in enumerate(file):
                if num > 0:
                    team1 = row[5:9]
                    team2 = row[10:14]
                    prob = row[15:]
                    probDictionary[(team1, team2)] = float(prob)
        return probDictionary    

class Predictions():
    def __init__(self):
        self._predictions = self.initializePredictions()
    
    def initializePredictions(self):
        generator = KagglePredictionsGenerator('testPredictions.csv')
        return generator.probabilities

    @property
    def predictions(self):
        return self._predictions
    
    @predictions.setter
    def predictions(self, value):
        print("Sorry, can't reset the predictions!")
        return
    
class Game():
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

        if self.team1 > self.team2:
            self.team1, self.team2 = self.team2, self.team1
        
    def _getPredictions(self, predictionsObject):
        return predictionsObject.predictions
    
    def _getTeamOneWinPctWith(self, predictionsObject):
        predictions = self._getPredictions(predictionsObject)
        return predictions[(self.team1, self.team2)]

    def simulateWith(self, predictionsObject):
        team1wins = self._getTeamOneWinPctWith(predictionsObject)
        val = np.random.uniform(0, 1)
        #print(val)
        if val < team1wins:
            return self.team1
        else:
            return self.team2
    
    def __str__(self):
        return f"{self.team1} vs. {self.team2}"

    def __repr__(self):
        return f"{self.team1} vs. {self.team2}"
        
class BracketEntry():
    def __init__(self, index):
        self.index = index
        self.team1 = None
        self.team2 = None
        self._game = None

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

    def getWinner(self, predictionsObject):
        return self.game.simulateWith(predictionsObject)
    
    def getNextGameIndex(self):
        return self.index // 2

    def __str__(self):
        return f"{self.index}: {self.game}"
    
    def __repr__(self):
        return f"{self.index}: {self.game}"

class Bracket():
    def __init__(self, size, predictions):
        self.size = size
        self.gameBracket = [None] * size
        self.winnerBracket = [None] * size
        self.randomlyFillFirstRound()
        self.predictions = predictions
    
    def assignFirstRound(self, someBracketTemplate):
        self.randomlyFillFirstRound()
        #TODO: Implement this and eventually replace randomlyFillFirstRound

    def randomlyFillFirstRound(self):
        # TODO: Update with deterministic bracket once it's set
        # i.e., shouldn't be doing any shuffling to determine first round
        preds = Predictions().predictions
        listOfTeams = list(set([i[0] for i in preds.keys()]))[:64]
        random.shuffle(listOfTeams)
        for num, i in enumerate(range(32, 64)):
            idx = i - 32
            teamA = listOfTeams[2 * idx]
            teamB = listOfTeams[2 * idx + 1]
            bracketEntry = BracketEntry(i)
            bracketEntry.addTeam(teamA)
            bracketEntry.addTeam(teamB)
            self.gameBracket[i] = bracketEntry
        
    @property
    def round(self):
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
        thisRoundSize = self.size / (2 ** self.round) 
        
        if (thisRoundSize == int(thisRoundSize) and (thisRoundSize % 2 == 0)) or (thisRoundSize == 1):
            thisRoundSize = int(thisRoundSize)
        else:
            print("Hmmm, the size of this round should be an even integer!")
            raise ValueError
                
        for gameIndex in range(thisRoundSize, thisRoundSize * 2):
            bracketEntry = self.gameBracket[gameIndex]
            
            bracketEntryWinner = bracketEntry.getWinner(self.predictions)
            bracketEntryNextIndex = bracketEntry.getNextGameIndex()
            self.winnerBracket[gameIndex] = bracketEntryWinner 
            
            if thisRoundSize > 1:
                self._insertBracketEntry(bracketEntryNextIndex)
                nextEntry = self.gameBracket[bracketEntryNextIndex]
                nextEntry.addTeam(bracketEntryWinner)
            
    def _insertBracketEntry(self, index):
        if self.gameBracket[index] is None:
            self.gameBracket[index] = BracketEntry(index)

    def simulateTournament(self, reset = True):
        while self.winnerBracket[1] is None:
            self._simulateRound()
        if reset:
            self.bracketReset()
    
    def bracketReset(self):
        self.gameBracket = [None] * self.size
        self.winnerBracket = [None] * self.size
        self.randomlyFillFirstRound()
    
'''
2.19 TODO
Fill out bracket as a separate class so you're delegating that out
    -Then you can switch in different years' brackets
'''
preds = Predictions()
test = Bracket(64, preds)
test.randomlyFillFirstRound()
test.simulateTournament(reset = False)
print(test.winnerBracket)
