from ast import Pass
import sys
sys.path.insert(0, '../source/data_structures/')
sys.path.insert(0, '../data_structures/')

import os
import requests
import re
import numpy as np
from bs4 import BeautifulSoup
from predictionBracket import PredictionBracket
from fansBracket import FansBracket
from userBracket import UserBracket
import time

from bracket import Bracket
from teams import Teams, SpecificEntryImporter, Team
from predictions import Predictions, KagglePredictionsGenerator

# Get driver configuration
from configparser import ConfigParser
config = ConfigParser(os.environ)
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'driver_config.ini'))

class ScoringNeighbors():
    def __init__(self, inputMat : np.ndarray, start : int, end : int, teams : list[Team]):
        self.mat = inputMat
        self.start = start
        self.end = end
        self.teams = teams

    def makeEntries(self):
        mid = (self.start + self.end) // 2
        entryNames = [i for i in range(self.start, mid)] + ['User Bracket'] + [i for i in range(mid, self.end)]
        finalScores = self.mat[:, -1]
        winners = [self.teams[int(i)].name for i in self.mat[:, 1]]
        winnerLinks = [self.teams[int(i)].imgLink for i in self.mat[:, 1]]
        fields = ['entryName', 'score', 'winner', 'winnerLink']
        return [dict(zip(fields,i)) for i in list(zip(entryNames, finalScores, winners, winnerLinks))]
        
class Simulation():
    def __init__(self, 
                    bracketTeams : Teams = None, 
                    predBracket : PredictionBracket = None, 
                    fanBracket : FansBracket = None, 
                    myBracketUrl : UserBracket = None, 
                    bracketSize : int = 64,
                    poolSize : int = 1000):
        self.dirPath = os.path.dirname(os.path.realpath(__file__))
        self.teams = self._initTeams(bracketTeams)
        self.predBracket = self._initPred(predBracket)
        self.fanBracket = self._initFan(fanBracket)
        self.myBracket = self._initUser(myBracketUrl)
        
        self.size = bracketSize
        self.poolSize = poolSize
        self.POINTS_PER_ROUND = 320

        self.fanPool : np.ndarray = None
        self.myScoreArr : np.ndarray = None
        self.score = None
        self.score_str = None
        self.outPerformed = None
        self.percentile = None
    
    def _initTeams(self, teams : Teams) -> Teams:
        if teams is None:
            # A. Import Teams
            entryImporter = SpecificEntryImporter()
            teams = Teams(teamImporter = entryImporter)
            teams.setPredIds(file = f'{self.dirPath}/../data/MTeams_.csv')
        return teams

    def _initPred(self, predBracket : PredictionBracket) -> PredictionBracket:
        if predBracket is None:
            generator = KagglePredictionsGenerator(f'{self.dirPath}/../data/kaggle_predictions/seedPreds2022.csv')
            predictions = Predictions(generator)
            predBracket = PredictionBracket(inputObject = predictions, teams = self.teams, size = 64)
        return predBracket

    def _initFan(self, fanBracket : FansBracket) -> FansBracket:
        if fanBracket is None:
            fanBracket = FansBracket(teams = self.teams, size = 64)
        return fanBracket

    def _initUser(self, myBracketUrl : UserBracket) -> UserBracket:
        if myBracketUrl is None:
            myBracketUrl =  "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"
        myBracket = UserBracket(teams = self.teams, size = 64, userUrl = myBracketUrl)
        return myBracket
    
    def runSimulation(self):
        """
        For now, return score, percentile, 
        """
        self.myBracket.getWinnerBracket()
        self.predBracket.getWinnerBracket()
        self._simulatePool()
        self._rankScore()
        
    def _simulatePool(self):
        """
        Creates realistic pool of "fan" competitors as simulated 
        from ESPN Who Picked Whom 
            -see FansBracket module for more info
        """
        simulatedPool : list[np.ndarray] = [None] * self.poolSize
        for i in range (self.poolSize):
            simulatedPool[i] : np.ndarray = self.fanBracket.getWinnerBracket()
        self.fanPool = np.array(simulatedPool)
    
    def _createScoringFilter(self) -> np.ndarray:
        rounds = int(np.log2(self.size))
        scoringFilter = np.zeros(self.size)
        for round in range(rounds, 0, -1):
            start = 2 ** (round - 1)
            end = 2 ** (round)
            games = end - start
            pointsPerGame = self.POINTS_PER_ROUND / games
            scoringFilter[start:end] = pointsPerGame
        return scoringFilter

    def _score(self, entry : np.ndarray, actual : np.ndarray) -> np.ndarray:
        """
        Inputs
            - entry : np.ndarray  - winnerBracket array of bracket entry being
                                    scored (always of shape (n x 64))
            - actual : np.ndarray - winnerBracket array of the "actual occurence"
                                    i.e., instantiation of PredicitonBracket
        Returns
            - np.ndarray - Updated version of entry that is now (n x 65), where entry (i, 65)
                represents score of bracketEntry represented in row i
        """        
        scoringFilter : np.ndarray = self._createScoringFilter()
        
        # Re-shape both entry andn actual to (1, 64) np.ndarrays
        if np.ndim(entry) == 1:
            entry = entry.reshape((-1, entry.shape[0]))
        
        # Create 1 x 64 boolean matrix, comparing entry to actual
        boolMat = entry == actual[None, :]
        boolMat = boolMat.reshape((boolMat.shape[0], -1))
        
        # Matrix multiplication to get score
        scoreMat = np.matmul(boolMat, scoringFilter.reshape((scoringFilter.shape[0], -1)))
        
        # Append score to end of entry ndarray and return
        # Why? In case of fan pool, which is (1000 x 64),
        #     want to preserve the individual brackets, not
        #     just get the final scores 
        return np.hstack((entry, scoreMat))

    def _rankScore(self):
        myScore = self._score(self.myBracket.winnerBracket, self.predBracket.winnerBracket)
        fanScores = self._score(self.fanPool, self.predBracket.winnerBracket)
        fanScores = fanScores[fanScores[:, -1].argsort()][::-1][:fanScores.shape[0]]
        self.myScoreArr = myScore
        self.score = myScore[:, -1][0]
        self.score_str = str(self.score)[:-2]
        print(self.score_str)
        
        self.fanPool = fanScores
        outPerformed = (fanScores[:, -1] < self.score).sum()
        self.outPerformed = outPerformed
        self.percentile = str(round(100 * (outPerformed / self.poolSize), 1))
        print(f"Your bracket entry outperformed {outPerformed} simulated fan entries, better than {self.percentile}% of entries")
    
    def getNeighborTeams(self, n : int = 10) -> list[Teams]:
        """
        Input:
            n  - number of neighbors to view, will view n/2 above and n/2 below
        """
        outPerformed = (self.fanPool[:, -1] < self.score).sum()
        start = (self.poolSize - (outPerformed)) - n // 2
        end = (self.poolSize - (outPerformed)) + n // 2
        mid = (start + end) // 2
        int1 = np.vstack((self.fanPool[start : mid], self.myScoreArr, self.fanPool[mid : end + 1]))
        neighbs = ScoringNeighbors(int1, start, end, self.teams.teams)
        return neighbs.makeEntries()
        
        
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
    generator = KagglePredictionsGenerator('../data/kaggle_predictions/xgb_preds2022.csv')
    predictions = Predictions(generator)

    teams = Teams()
    dirPath = os.path.dirname(os.path.realpath(__file__))
    teams.setPredIds(file = f'{dirPath}/../data/MTeams_.csv')
    testBracket = PredictionBracket(inputObject = predictions, teams = teams, size = 64)
    
    a = Simulation(predBracket = testBracket)
    a.runSimulation()
    a._getNeighborTeams(n = 25)
    
    # print(a.fanPool)
    
    # print(a.myBracket.winnerBracket)
    # print(a.fanPool)
    # print(a.score)
    # print(a.percentile)