from ast import Pass
import sys
sys.path.insert(0, '../source/data_structures/')

import os
import requests
import re
import numpy as np
from bs4 import BeautifulSoup
from predictionBracket import predictionBracket
from fansBracket import fansBracket
from userBracket import userBracket
import time

from teams import Teams, specificEntryImporter
from predictions import Predictions, KagglePredictionsGenerator

# Get driver configuration
from configparser import ConfigParser
config = ConfigParser(os.environ)
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'driver_config.ini'))

class Simulation():
    def __init__(self, bracketTeams = None, predBracket = None, fanBracket = None, myBracketUrl = None, bracketSize = 64,
                    poolSize = 1000):
        self.teams = self.initTeams(bracketTeams)
        self.predBracket = self.initPred(predBracket)
        self.fanBracket = self.initFan(fanBracket)
        self.myBracket = self.initUser(myBracketUrl)
        
        self.size = bracketSize
        self.poolSize = poolSize

        self.fanPool = None
        self.score = None
        self.percentile = None
    
    def initTeams(self, teams):
        if teams is None:
            # A. Import Teams
            entryImporter = specificEntryImporter()
            teams = Teams(teamImporter = entryImporter)
            teams.setPredIds(file = '../Data/MTeams.csv')
        return teams

    def initPred(self, predBracket):
        if predBracket is None:
            generator = KagglePredictionsGenerator('../data/kaggle_predictions/seedPreds2022.csv')
            predictions = Predictions(generator)
            predBracket = predictionBracket(inputObject = predictions, teams = self.teams, size = 64)
        return predBracket

    def initFan(self, fanBracket):
        if fanBracket is None:
            bwUrl = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/whopickedwhom"
            fanBracket = fansBracket(teams = self.teams, size = 64, bwUrl = bwUrl)
        return fanBracket

    def initUser(self, myBracketUrl):
        if myBracketUrl is None:
            userUrl = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"
            myBracket = userBracket(teams = self.teams, size = 64, userUrl = userUrl)
        else:
            myBracket = userBracket(teams = self.teams, size = 64, userUrl = myBracketUrl)
        return myBracket
    
    def runSimulation(self):
        """
        For now, return score, percentile, 
        """
        self.myBracket.getWinnerBracket()
        self.predBracket.getWinnerBracket()
        self._simulatePool()
        self._scoreRank()
        
    def _simulatePool(self):
        """
        Creates realistic pool of "fan" competitors as simulated 
        from ESPN Who Picked Whom (see fansBracket module)
        """
        simulatedPool = [None] * self.poolSize
        for i in range (self.poolSize):
            simulatedPool[i] = self.fanBracket.getWinnerBracket()
        self.fanPool = np.array(simulatedPool)
    
    def _scoreRow(self, row, actual, ptFilter):
        return (row == actual) * ptFilter

    def _score(self, entry, actual):
        # -Entry is the winnerBracket array of the 
        #     bracket entry being scored
        # -Actual is the actual occurence that determines score
        rounds = int(np.log2(self.size))
        pointsPerRound = 320
        scoringFilter = np.zeros(self.size)
        for round in range(rounds, 0, -1):
            start = 2 ** (round - 1)
            end = 2 ** (round)
            games = end - start
            pointsPerGame = pointsPerRound / games
            scoringFilter[start:end] = pointsPerGame
        if np.ndim(entry) == 1:
            entry = entry.reshape((-1, entry.shape[0]))
        boolMat = entry == actual[None, :]
        
        boolMat = boolMat.reshape((boolMat.shape[0], -1))
        scoreMat = np.matmul(boolMat, scoringFilter.reshape((scoringFilter.shape[0], -1)))
        return np.hstack((entry, scoreMat))

    def _scoreRank(self):
        myScore = self._score(self.myBracket.winnerBracket, self.predBracket.winnerBracket)
        fanScore = self._score(self.fanPool, self.predBracket.winnerBracket)
        fanScore = fanScore[fanScore[:, -1].argsort()]
        self.score = myScore[:, -1][0]
        self.score_str = str(round(self.score))
        # print(f"The simulated fan pool of size {self.poolSize} produced the following scores: ")
        # print(fanScore)
        # print(fanScore[:, -1])
        # print((fanScore[:, -1] < self.score))
        outPerformed = (fanScore[:, -1] < self.score).sum()
        self.percentile = str(round(100 * (outPerformed / self.poolSize), 1))
        # print(f"Your bracket entry outperformed {outPerformed} simulated fan entries, better than{100 * self.percentile : .1f}"\
                # "% of entries")
    
    def viewSimulatedResult(self):
        """
        Provides view of simulated 'reality'
        """

    def viewFanBracket(self, rkIdx):
        """
        Provides view of fan bracket based on rank-based index number
        """
        pass
    
if __name__ == "__main__":
    a = Simulation()
    a.runSimulation()
    # print(a.myBracket.winnerBracket)
    # print(a.fanPool)
    # print(a.score)
    # print(a.percentile)