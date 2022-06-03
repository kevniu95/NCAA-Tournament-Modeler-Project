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

from teams import Teams, specificEntryImporter
from predictions import Predictions, KagglePredictionsGenerator


# Get driver configuration
from configparser import ConfigParser
config = ConfigParser(os.environ)
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'driver_config.ini'))


class Simulation():
    def __init__(self, bracketTeams = None, predBracket = None, fanBracket = None, myBracket = None, bracketSize = 64):
        self.teams = self.initTeams(bracketTeams)
        self.predBracket = self.initPred(predBracket)
        self.fanBracket = self.initFan(fanBracket)
        self.myBracket = self.initUser(myBracket)
        self.size = bracketSize
    
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

# def main():
#     a = Simulation()
    
if __name__ == "__main__":
    a = Simulation()
    # print(a.fanBracket.getWinnerBracket())
    print(a.predBracket.getWinnerBracket())
    # print(a.myBracket.getWinnerBracket())
