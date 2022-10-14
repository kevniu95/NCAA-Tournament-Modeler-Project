import sys
sys.path.insert(0, '../source/data_structures/')
sys.path.insert(0, '../data_structures/')

import requests
import re
import numpy as np
from bs4 import BeautifulSoup
from bracket import Bracket, BracketEntry
from teams import Team, Teams, SpecificEntryImporter

class backwardBracketEntry(BracketEntry):
    """
    Bracket entry with following information:
    - index : int - the index of this entry in the overall Bracket structure
    - teamList : list[Team] - the subset of teams from Teams
                    that can compete in the game at this point in teh bracket
                    - e.g., Game 1, the championship can be won by all teams
                    - e.g., Game 32, the 1st round game for the #1 overall seed can be won
                            by only two teams
    - rd : int - the round that this bracketEntry occurs in 
                -so we can lookup how many people selected team i to advance in this round
    """
    def __init__(self, index : int, teamList : list[Team], rd : int):
        super().__init__(index)
        self.teamList : list[Team] = teamList
        self.rd : int = rd
        # self.sorted : bool = None
    
    def getWinner(self) -> Team:
        currVal = 0
        i = 0
        val = np.random.uniform(0, 1)
        retries = 0
        while val > currVal:
            try:
                currVal += self.teamList[i].pickPct[self.rd]
            except:
                # Sometimes randomly selected value exceeds
                #  total of individual probabilities due to
                #  rounding errors
                val = np.random.uniform(0, 1) 
                i = 0
                retries += 1
            i += 1
        if retries > 0:
            print(f"A bracket entry saw {retries} retries")
        self.winner = self.teamList[i - 1]
        return self.winner

class fansBracket(Bracket):
    def __init__(self, teams : Teams = None,
                        size : int = 64, 
                        url : str = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/whopickedwhom"):
        super().__init__(size = size)
        self.teams : Teams = teams
        # bwUrl is the url link to where the ESPN Who Picked Whom information is located
        self.url : str = url
        self._getPickInfo()

    def _getPickInfo(self):
        """
        For each Team in Teams, updates the pickPct
            -This means for each Team i, for each round j in {0 - 5}, inclusive)
                - we fill in how many ESPN contestants picked 
                   team i to win in round j
        """
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        for i in range(6):
            # Pull Round Data in
            teams = soup.find_all('td', class_= re.compile('_round' + str(i) +'$'))
            for team in teams:
                # Save this to Team information in Teams list
                teamName = team.find_all('span', class_ = 'teamName')[0].text
                teamPct = team.find_all('span', class_ = 'percentage')[0].text
                teamObject = self.teams.nameTeamDict[teamName]
                teamObject.setPick(round = i, pct = teamPct)
    
    def getWinnerBracket(self) -> np.ndarray:
        """
        This is the function that 'simulates' the tournament
        """
        # Sort teams (of object Teams) by bracket ID
        self.teams.teams.sort(key = lambda x: x.bracketId)
        teams = self.teams.teams
        
        winnerBracket = [None] * self.size
        winnerBracket[0] = -1
        # Loop through each round
        for rd in range(int(np.log2(self.size)) -1, -1, -1):
            gamesInRound = 2 ** (5 - rd)
            roundStartIdx = 2 ** (5 - rd)
            possibleTeamsInGame = int(self.size / gamesInRound)
            ctr = 0 # Tracks which set of teams to put in the next game of this round i
            for gameIdx in range(roundStartIdx, roundStartIdx + gamesInRound):
                # Subset to correct set of teams that are playing in this game
                teamList = teams[ctr : ctr + possibleTeamsInGame]
                # Move to next set of teams for next game
                ctr += possibleTeamsInGame
                # Create a backwards Bracket Entry if there isn't one already
                if winnerBracket[gameIdx] is None:
                    thisEntry = backwardBracketEntry(gameIdx, teamList, rd)
                    winner = thisEntry.getWinner()
                    winnerBracket[gameIdx] = winner

                    winnerBracketIdx = winner.bracketId + 64
                    while winnerBracketIdx > gameIdx:
                        winnerBracketIdx = winnerBracketIdx // 2
                        winnerBracket[winnerBracketIdx] = winner.bracketId
        return np.array(winnerBracket)

        
if __name__ == '__main__':
    entryImporter = SpecificEntryImporter()
    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../Data/MTeams_.csv')
    
    for i in range(1000):
        print(i)
        test = fansBracket(teams = teams, size = 64)
        test._getPickInfo()
        test.getWinnerBracket()
    