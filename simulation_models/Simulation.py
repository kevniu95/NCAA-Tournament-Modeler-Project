from ast import Pass
import sys
sys.path.insert(0, '../data_structures/')

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
    def __init__(self, bracketTeams = None, predBracket = None, fanBracket = None, myBracket = None, bracketSize = 64,
                    poolSize = 1000):
        self.teams = self.initTeams(bracketTeams)
        self.predBracket = self.initPred(predBracket)
        self.fanBracket = self.initFan(fanBracket)
        self.myBracket = self.initUser(myBracket)
        
        self.size = bracketSize
        self.poolSize = poolSize

        self.fanPool = None
        self.myScore = None
        self.myRights = None
    
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

    def initUser(self, myBracket):
        if myBracket is None:
            userUrl = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"
            myBracket = userBracket(teams = self.teams, size = 64, userUrl = userUrl)
        return myBracket
    
    def runSimulation(self):
        self.myBracket.getWinnerBracket()
        self.predBracket.getWinnerBracket()
        self._simulatePool()
        # print(self.fanPool)
        
    def _simulatePool(self):
        """
        Creates realistic pool of "fan" competitors as simulated 
        from ESPN Who Picked Whom (see fansBracket module)
        """
        simulatedPool = [None] * self.poolSize
        for i in range (self.poolSize):
            simulatedPool[i] = self.fanBracket.getWinnerBracket()
        self.fanPool = simulatedPool
    
    def _score(self, entry, actual):
        # -Entry is the winnerBracket array of the 
        #     bracket entry being scored
        # -Actual is the actual occurence that determines score
        noCorrect = []
        totalPts = []
        pointsPerRound = 320
        rounds = int(np.log2(self.size))
        for round in range(rounds, 0, -1):
            start = 2 ** (round - 1)
            end = 2 ** (round)
            games = end - start
            pointsPerGame = pointsPerRound / games

            entryTms = [i.name for i in entry[start:end]]
            actualTms = [i.name for i in actual[start:end]]
            matches = [i for i in list(zip(entryTms, actualTms)) if i[0] == i[1]]
            
            noCorrect.append(len(matches))
            totalPts.append(len(matches) * pointsPerGame)
        return noCorrect, totalPts

    def _scoreRank(self):
        # NOTE
        # Idea: save winnerBracket results as numpy arrays to keep results more
        # condensed and to do operations quicker
        #   - Idea came from sorting of fanPool, if it was n x (63  + 1) matrix,
        #      we can preserve all info we need and sort fanPool, and keep it in 
        #      condensed np.array format (instead) of creaing a separate new Object
        #      for each fanPool Entry
        if self.myBracket.winnerBracket is None:
            self.myBracket.getWinnerBracket()
        myRights, myScores = self._score(self.myBracket.winnerBracket, self.predBracket.winnerBracket)
        self.myScore = sum(myScores)
        self.myRights = sum(myRights)

        for entry in self.fanPool:

        return
        


# def main():
#     a = Simulation()
    
if __name__ == "__main__":
    a = Simulation()
    # test = a.simulatePool()
    a.runSimulation()
    
    # print(a.predBracket.winnerBracket)
    # score = a._score(a.myBracket.winnerBracket, a.predBracket.winnerBracket)
    # print(score)
    
    # print(a.fanBracket.getWinnerBracket())
    # print(a.predBracket.getWinnerBracket())
    # print(a.myBracket.getWinnerBracket())
