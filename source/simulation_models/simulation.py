import sys
sys.path.insert(0, '../source/data_structures/')
sys.path.insert(0, '../data_structures/')

import os
import numpy as np
import base64
from io import BytesIO
from matplotlib.figure import Figure
from typing import List, Dict

from predictionBracket import PredictionBracket
from fansBracket import FansBracket
from userBracket import UserBracket

from bracket import Bracket
from teams import Teams, SpecificEntryImporter, Team
from predictions import Predictions, KagglePredictionsGenerator

# Get driver configuration
from configparser import ConfigParser
config = ConfigParser(os.environ)
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'driver_config.ini'))

class ScoringNeighbors():
    def __init__(self, inputMat : np.ndarray, start : int, end : int, teams : List[Team]):
        self.mat = inputMat
        self.start = start
        self.end = end
        self.teams = teams

    def makeEntries(self) -> List[Dict[str, str]]:
        mid = (self.start + self.end) // 2
        entryNames = [i for i in range(self.start, mid)] + ['User Bracket'] + [i for i in range(mid, self.end)]
        finalScores = self.mat[:, -1]
        winners = [self.teams[int(i)].name for i in self.mat[:, 1]]
        winnerLinks = [self.teams[int(i)].imgLink for i in self.mat[:, 1]]
        fields = ['entryName', 'score', 'winner', 'winnerLink']
        return [dict(zip(fields,i)) for i in list(zip(entryNames, finalScores, winners, winnerLinks))]

# class ScoreVisualizer():
#     def __init__(self):


class VisualTable():
    def __init__(self, myScoreVis : np.ndarray, teams : List[Team]):
        """
        myScoreVis is a numpy.ndarray with three columns
            - First column is user selection
            - Second column is 'actual' winner in simulation
            - Third column is boolean indicating correctness
        """
        self.teams = teams
        self.vis_arr : List[VisualTableEntry] = self._process_score_arr(myScoreVis)
        
    def _process_score_arr(self, myScoreVis):
        vis_arr = []
        for num, i in enumerate(myScoreVis):
            if num > 0:
                pts = 320 / (2**(int(np.log2(num) // 1)))
                userSel = self.teams[i[0]]
                corrSel = self.teams[i[1]]
                vis_arr.append(VisualTableEntry(userSel, corrSel, pts))
        return vis_arr
    
    def return_vis_arr(self):
        return self.vis_arr

            
class VisualTableEntry():
    roundLabels = dict(zip([320, 160, 80, 40, 20, 10], ['NCG', 'F4', 'E8', 'S16', 'R32', 'R64']))
    def __init__(self, userTeam : Team, correctTeam : Team, pts : int):
        self.u_team = userTeam
        self.c_team = correctTeam
        self.pts = pts
        self.correct = self.u_team.bracketId == self.c_team.bracketId
        self.score = int(self.correct) * self.pts
        self.label = self.roundLabels[pts]
        self.printScore = str(self.score)[:-2] + ' / ' + str(self.pts)[:-2] 
    
    def getResults(self):
        data = {'uTeam' : self.u_team.name, 
                'uTeamImg' : self.u_team.imgLink,
                'cTeam' : self.c_team.name,
                'cTeamImg' : self.c_team.imgLink,
                'pts' : self.pts,
                'correct' : self.correct,
                'score' : self.score,
                'label' : self.label}
        return data

    def __str__(self):
        return (f"{self.label}: {self.pts} points\nChose: {self.u_team.name}\nWinner: {self.c_team.name}\nStatus:{self.correct}")

    def __repr__(self):
        return (f"{self.label}: {self.pts} points\nChose: {self.u_team.name}\nWinner: {self.c_team.name}\nStatus:{self.correct}")

class Simulation():
    def __init__(self, 
                    bracketTeams : Teams = None, 
                    predBracket : PredictionBracket = None, 
                    fanBracket : FansBracket = None, 
                    myBracketUrl : UserBracket = None, 
                    bracketSize : int = 64):
        self.dirPath = os.path.dirname(os.path.realpath(__file__))
        self.teams = self._initTeams(bracketTeams)
        self.predBracket = self._initPred(predBracket)
        self.fanBracket = self._initFan(fanBracket)
        self.myBracket = self._initUser(myBracketUrl)
        
        self.size = bracketSize
        self.POINTS_PER_ROUND = 320
        
        # These are set with each call to runSimulation() method
        self.poolSize = None
        self.fanPool : np.ndarray = None
        
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
    
    def runSimulation(self, poolSize : int, resetPreds : bool):
        """
        Gets and saves winner bracket for 
         - My Bracket
         - Prediction Bracket
         - Fan Brackets
        
        Sets poolSize and fanPool for this prediction as well

        Returns Prediction Bracket
        """
        self.myBracket.getWinnerBracket()
        self.predBracket.getWinnerBracket(reset = resetPreds)
        self.poolSize : int = poolSize
        self.fanPool : np.ndarray = self._simulatePool(poolSize)
        return self.predBracket.winnerBracket
    
    def _simulatePool(self, poolSize : int) -> np.ndarray:
        """
        Creates realistic pool of "fan" competitors as simulated 
        from ESPN Who Picked Whom 
            -see FansBracket module for more info
        """
        simulatedPool : List[np.ndarray] = [None] * poolSize
        for i in range (poolSize):
            simulatedPool[i] : np.ndarray = self.fanBracket.getWinnerBracket()
        fanPool : np.ndarray = np.array(simulatedPool)
        return fanPool
    
    def scoreSimulation(self):
        """
        To be called after runSimulation() function
        -Returns:
        - string rep of user score
        - string rep of user score percentile
        - histogram of user performance vs fanPool
        - neighbors around user
        """
        myScoreArr, myScoreVis, fanScores = self._rankScore(self.fanPool)
        
        score = myScoreArr[:, -1][0]
        outPerformed = (fanScores[:, -1] < score).sum()
        percentile = str(round(100 * (outPerformed / self.poolSize), 1))
        print(f"Your bracket entry outperformed {outPerformed} simulated fan entries, better than {percentile}% of entries")

        histNums = self._collapseFanScores(fanScores)
        hist = self._plotHistogram(histNums, score)
        neighbors = self._getNeighborTeams(fanScores, myScoreArr, n= 24)
        scoreVis = VisualTable(myScoreVis, self.teams.teams).return_vis_arr()
        return str(score)[:-2], percentile, hist, neighbors, scoreVis
    
    def _rankScore(self, fanPool : np.ndarray):
        myScore, my_score_vis = self._score(self.myBracket.winnerBracket, self.predBracket.winnerBracket)
        fanScores, _ = self._score(fanPool, self.predBracket.winnerBracket)
        fanScores = fanScores[fanScores[:, -1].argsort()][::-1][:fanScores.shape[0]]
        return myScore, my_score_vis, fanScores

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
        scoringUser = False
        # Re-shape both entry andn actual to (1, 64) np.ndarrays
        if np.ndim(entry) == 1:
            scoringUser = True
            entry = entry.reshape((-1, entry.shape[0]))
        
        # Create 1 x 64 boolean matrix, comparing entry to actual
        boolMat = entry == actual[None, :]
        boolMat = boolMat.reshape((boolMat.shape[0], -1))
        
        # Matrix multiplication to get score
        scoreMat = np.matmul(boolMat, scoringFilter.reshape((scoringFilter.shape[0], -1)))
        
        # If it is the user array (not fanPool), will return extra
        #  np.ndarray to help with visualization of results
        vis_arr = None
        if scoringUser:
            new_shape = (entry.shape[1], entry.shape[0])
            vis_arr = np.hstack((entry.reshape(new_shape), actual[None, :].reshape(new_shape), 
                                (boolMat + [0] * boolMat.shape[0]).reshape(new_shape)))
            
        # Append score to end of entry ndarray and return
        # To preserve individual brackets of fan pool
        return np.hstack((entry, scoreMat)), vis_arr

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
    
    def _collapseFanScores(self, fanScores : np.ndarray) -> Dict[int : int]:
        """
        Collapses fan scores into histogram-like dictionary
        with unique scores and #of fans with those scores
            e.g., {300 : # brackets w. 300 pts}
        """
        test = fanScores[:, -1] 
        valDict = {}
        for i in test:
            valDict[i] = valDict.get(i, 0) + 1
        return valDict

    def _plotHistogram(self, fanHist : Dict[int : int], score : int):
        """
        Converts dictionary histogram into real matplotlib 
        histogram, encoded for sending to web app
        """
        ans = []
        for k, v in fanHist.items():
            ans += [k] * v

        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.hist(ans, bins = 20)
        axis.axvline(score, color='k', linestyle='dashed', linewidth=1)

        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer())
        return data
     
    def _getNeighborTeams(self, fanScores : np.ndarray, myScoreArr : np.ndarray,  n : int = 10) -> List[Teams]:
        """
        Input:
            n  - number of neighbors to view, will view n/2 above and n/2 below
        """
        score = myScoreArr[:, -1][0]
        outPerformed = (fanScores[:, -1] < score).sum()
        poolSize = fanScores[:, -1].shape[0]
        start = (poolSize - (outPerformed)) - n // 2
        end = (poolSize - (outPerformed)) + n // 2
        mid = (start + end) // 2
        int1 = np.vstack((fanScores[start : mid], myScoreArr, fanScores[mid : end + 1]))
        neighbs = ScoringNeighbors(int1, start, end, self.teams.teams)
        return neighbs.makeEntries()


if __name__ == "__main__":
    generator = KagglePredictionsGenerator('../data/kaggle_predictions/xgb_preds2022.csv')
    predictions = Predictions(generator)

    teams = Teams()
    dirPath = os.path.dirname(os.path.realpath(__file__))
    teams.setPredIds(file = f'{dirPath}/../data/MTeams_.csv')
    testBracket = PredictionBracket(inputObject = predictions, teams = teams, size = 64)
    
    a = Simulation(predBracket = testBracket)
    predBracket = a.runSimulation(poolSize = 1000, resetPreds = True)
    res = a.scoreSimulation()