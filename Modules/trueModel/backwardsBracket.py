import requests
import re
import numpy as np
from bs4 import BeautifulSoup
from bracket import Bracket, BracketEntry
from teams import Teams, specificEntryImporter
from predictions import blankTemplate, simpleSeedTemplate, Predictions, \
    KagglePredictionsGenerator

class backwardBracketEntry(BracketEntry):
    def __init__(self, index, teamList, rd):
        super().__init__(index)
        self.teamList = teamList
        self.rd = rd
    
    def getWinner(self):
        currVal = 0
        i = 0
        self.teamList.sort(key = lambda x : x.pickPct[self.rd], reverse= True)
        val = np.random.uniform(0, 1)
        while val > currVal:
            print(val)
            print(self.teamList[i].pickPct[self.rd])
            currVal += self.teamList[i].pickPct[self.rd]
            i += 1
        return self.teamList[i - 1]

class backwardBracket(Bracket):
    def __init__(self, inputObject, teams = None, size = 64, bwUrl = None):
        """
        bwUrl is the url link to where the ESPN Who Picked Whom information is located
        """
        if bwUrl is None:
            self.url = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/whopickedwhom"
        else:
            self.url = bwUrl

        super().__init__(inputObject = inputObject, teams = teams, size = 64)
    
    def getPickInfo(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        roundDict = {}
        
        for i in range(6):
            # Pull Round Data in
            roundList = []
            teams = soup.find_all('td', class_= re.compile('_round' + str(i) +'$'))
            for team in teams:
                # Save this tuple in a list (BracketID, teamName, teamPct)
                teamName = team.find_all('span', class_ = 'teamName')[0].text
                teamPct = team.find_all('span', class_ = 'percentage')[0].text
                teamObject = self.teams.nameTeamDict[teamName]
                teamObject.setPick(round = i, pct = teamPct)
    
    def simulateRounds(self):
        # Sort teams (of object Teams) by bracket ID
        self.teams.teams.sort(key = lambda x: x.bracketId)
        teams = self.teams.teams
        
        # Loop through each round
        #int(np.log2(self.size)) -1
        for i in range(0 , -1, -1):
            gamesInRound = 2 ** (5 - i)
            roundStartIdx = 2 ** (5 - i)
            teamsInGame = int(self.size / gamesInRound)
            ctr = 0 # Tracks which set of teams to put in the next game of this round i
            for gameIdx in range(roundStartIdx, roundStartIdx + gamesInRound):
                # Subset to correct set of teams that are playing in this game
                teamList = teams[ctr : ctr + teamsInGame]
                # Move to next set of teams for next game
                ctr += teamsInGame
                # Create a backwards Bracket Entry if there isn't one already
                if self.winnerBracket[gameIdx] is None:
                    thisEntry = backwardBracketEntry(gameIdx, teamList, i)
                    winner = thisEntry.getWinner()
                    self.winnerBracket[gameIdx] = winner
        print(self.winnerBracket)
                    
                    # Back
                
                    
        


if __name__ == '__main__':

    generator = KagglePredictionsGenerator('seedPreds2022.csv')
    predictions = Predictions(generator)
    # predictions = Predictions()
    # for game, leftTeamWinProb in predictions.predictions.items():
        # print(f"Teams involved: {game}\nProbability left team wins: {leftTeamWinProb}\n")
    
    entryImporter = specificEntryImporter()
    teams = Teams(bracketImporter = entryImporter)
    teams.setPredIds(file = 'MTeams.csv')
    
    test = backwardBracket(inputObject = predictions, teams = teams, size = 64, bwUrl = None)
    test.getPickInfo()
    test.simulateRounds()
    # testBracket = Bracket(predictions, teams = teams, size = 64)
    # Note that game bracket has half-filled (all first round games)
    # print(testBracket.gameBracket)
    # But winner braket is unfilled
    # print(testBracket.winnerBracket)

    """
    C. Simulate Tournament
    """
    # testBracket.simulateTournament(reset = False)
    # print(testBracket.gameBracket)
    # print(testBracket.winnerBracket)
    # print(len(testBracket.winnerBracket))
