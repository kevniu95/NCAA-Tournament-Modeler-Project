# True Model

from multiprocessing.sharedctypes import Value
import numpy as np
from abc import ABC, abstractmethod
import random
import math
from teams import Teams, specificEntryImporter
from predictions import blankTemplate, simpleSeedTemplate, Predictions, \
    KagglePredictionsGenerator
    
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
    """
    Wraps object of Game class in a BracketEntry
    -Takes teams one by one and instantiates a game 
        when two teams added two BracketEntry object
    -Identifies winner of game
    -Identifies next game in bracket (where winner advances to)
    """
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
    """"
    Organized collection of BracketEntry objects, representing
        the NCAA Tournament bracket
    -Maintains gameBracket with matchups and winnerBracket showing
        winners of those matchups
    -For now first round is randomly determined given predictions data

    Bracket Structure (used in gameBracket and winnerBracket):
    -Bracket is represented by n-entry array where n is number of teams
        in tournament (meaning there are n-1 games)
    -Championship game is at index 1 (0 left empty)
        -Semifinal games start at index 2
        -Quarterfinal games start at index 4....
    -First round of games is "contained" in array entries 31 - 63
    """
    def __init__(self, inputObject, teams = None, size = 64):
        self.teams = teams
        self.size = size
        self.gameBracket = [None] * size
        self.winnerBracket = [None] * size
        self.inputObject = inputObject
        self.assignFirstRound()
    
    def assignFirstRound(self, random = False):
        if random or self.teams is None:
            self.randomlyFillFirstRound()
        else:
            self.assignByTeamList()
    
    def assignByTeamList(self):
        for num, i in enumerate(range(32, 64)):
            bracketEntry = BracketEntry(i)
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
            bracketEntry = BracketEntry(i)
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


if __name__ == "__main__":

    """
    A. Import Predictions and Teams
    -Based on sample predictions for all 64*63 games in 2021 NCAA Tournament
    """
    generator = KagglePredictionsGenerator('seedPreds2022.csv')
    predictions = Predictions(generator)
    # predictions = Predictions()
    # for game, leftTeamWinProb in predictions.predictions.items():
        # print(f"Teams involved: {game}\nProbability left team wins: {leftTeamWinProb}\n")
    
    entryImporter = specificEntryImporter()
    teams = Teams(bracketImporter = entryImporter)
    teams.setPredIds(file = 'MTeams.csv')
    
    """
    Only need to do this the one time to set up
    2022 predictions template
    -And simple model by seed
    """
    # temp1 = blankTemplate(2022, teams)
    # temp1.writeMatchups('predTemplate2022')

    # temp2 = simpleSeedTemplate(2022, teams)
    # temp2.writeMatchups('seedPreds2022')

    """
    B. Create Bracket
    - Note bracket randomly created given set of 64 teams
    - Will update for 2022 NCAA Tournament
    """
    testBracket = Bracket(predictions, teams = teams, size = 64)
    # Note that game bracket has half-filled (all first round games)
    print(testBracket.gameBracket)
    # But winner braket is unfilled
    print(testBracket.winnerBracket)

    """
    C. Simulate Tournament
    """
    testBracket.simulateTournament(reset = False)
    print(testBracket.gameBracket)
    print(testBracket.winnerBracket)
    print(len(testBracket.winnerBracket))