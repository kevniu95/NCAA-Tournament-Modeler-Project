import sys
sys.path.insert(0, '../data_structures/')

import requests
import re
import numpy as np
from bs4 import BeautifulSoup
from bracket import Bracket, BracketEntry
from teams import Teams, specificEntryImporter

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
            currVal += self.teamList[i].pickPct[self.rd]
            i += 1
        self.winner = self.teamList[i - 1]
        return self.winner

class backwardBracket(Bracket):
    def __init__(self, teams = None, size = 64, bwUrl = None):
        super().__init__(size = size)
        self.teams = teams
        # bwUrl is the url link to where the ESPN Who Picked Whom information is located
        if bwUrl is None:
            self.url = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/whopickedwhom"
        else:
            self.url = bwUrl

    def getPickInfo(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        for i in range(6):
            # Pull Round Data in
            teams = soup.find_all('td', class_= re.compile('_round' + str(i) +'$'))
            for team in teams:
                # Save this tuple in a list (BracketID, teamName, teamPct)
                teamName = team.find_all('span', class_ = 'teamName')[0].text
                teamPct = team.find_all('span', class_ = 'percentage')[0].text
                teamObject = self.teams.nameTeamDict[teamName]
                teamObject.setPick(round = i, pct = teamPct)
    
    def getWinnerBracket(self):
        # Sort teams (of object Teams) by bracket ID
        self.teams.teams.sort(key = lambda x: x.bracketId)
        teams = self.teams.teams
        
        # Loop through each round
        for i in range(int(np.log2(self.size)) -1, -1, -1):
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

                    winnerBracketIdx = winner.bracketId + 64
                    while winnerBracketIdx > gameIdx:
                        winnerBracketIdx = winnerBracketIdx // 2
                        self.winnerBracket[winnerBracketIdx] = winner
        return self.winnerBracket

        
if __name__ == '__main__':
    entryImporter = specificEntryImporter()
    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../Data/MTeams.csv')
    
    test = backwardBracket(teams = teams, size = 64, bwUrl = None)
    test.getPickInfo()
    print(test.getWinnerBracket())
    