import sys
sys.path.insert(0, '../source/data_structures/')
sys.path.insert(0, '../data_structures/')

import requests
import re
from bs4 import BeautifulSoup
import numpy as np
from typing import List

from bracket import Bracket
from teams import Team, Teams, SpecificEntryImporter

class UserBracket(Bracket):
    def __init__(self, teams : Teams = None, size : int = 64, userUrl : str = None):
        super().__init__(size = size)
        self.teams = teams
        # userUrl is the url link to where the specific ESPN bracket entry is located
        self.url = userUrl
        if self.url is None:
            self.url = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"

    def getWinnerBracket(self, realWinners = False) -> np.ndarray:
        if realWinners:
            spansInd = 3
            getChampFx = self._getRealWinner
            selected = False
        else:
            spansInd = 7
            getChampFx = self._getSelectedWinner
            selected = True
        
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        picks = soup.find_all('div', class_ = re.compile('slot s_'))
        nonChampWinners = [pick for pick in picks if int(pick['data-slotindex']) > 63]
        winners : List[int] = []
        # A. Get everyone except for winner of Championship game
        for entry in nonChampWinners:
            spans = entry.find_all('span')
            teamName : str = spans[spansInd].text
            winner : Team = self.teams.nameTeamDict[teamName]
            winners.append(winner.bracketId)
        
        # B. Get winner of Championship game
        winner = getChampFx(soup)
        winners.append(winner.bracketId)

        winnerBracket = self._assignWinners(winners)
        if selected:
            self.winnerBracket = winnerBracket
        return winnerBracket
    
    def _getSelectedWinner(self, soup):
        champ = soup.find_all('div', class_ = re.compile('center'))[0]
        
        names = champ.find_all('span', class_ = 'name')
        if len(names) > 1:
            winnerName = champ.find_all('span', class_ = 'name')[1].text
        else:
            winnerName = champ.find_all('span', class_ = 'name')[0].text
        winner : Team = self.teams.nameTeamDict[winnerName]
        return winner
    
    def _getRealWinner(self, soup):
        champ = soup.find_all('div', class_ = re.compile('center'))[0]
        
        name = champ.find('span', class_ = 'actual winner').find('span', class_ = 'name')
        winnerName = name.text
        winner : Team = self.teams.nameTeamDict[winnerName]
        return winner

    def _assignWinners(self, winners : List[int]) -> np.ndarray:
        bracket : List[int] = [None] * self.size
        bracket[32:] = winners[:32]
        bracket[16:32] = winners[32:48]
        bracket[8:16] = winners[48:56]
        bracket[4:8] = winners[56:60]
        bracket[2:4] = winners[60:62]
        bracket[1:2] = winners[62:63]
        bracket[0] = -1
        return np.array(bracket)

def main():
    entryImporter = SpecificEntryImporter()
    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../data/MTeams_.csv')
    
    kevUrl = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"
    test = UserBracket(teams = teams, size = 64, userUrl = kevUrl)
    test.getWinnerBracket()
    print(test.winnerBracket)
    print(test.getWinnerBracket(realWinners = True))
    # print(len(test.winnerBracket))

    
if __name__ == '__main__':
    main()
