import sys
sys.path.insert(0, '../data_structures/')

import requests
import re
from bs4 import BeautifulSoup
import numpy as np
from bracket import Bracket
from teams import Teams, specificEntryImporter

class userBracket(Bracket):
    def __init__(self, teams = None, size = 64, userUrl = None):
        """
        bwUrl is the url link to where the ESPN Who Picked Whom information is located
        """
        super().__init__(size = size)
        self.teams = teams
        # userUrl is the url link to where the specific ESPN bracket entry is located
        if userUrl is None:
            self.url = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"
        else:
            self.url = userUrl

    def getWinnerBracket(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        picks = soup.find_all('div', class_ = re.compile('slot s_'))
        nonChampWinners = [pick for pick in picks if int(pick['data-slotindex']) > 63]
        winners = []
        # A. Get everyone except for winner of Championship game
        for entry in nonChampWinners:
            spans = entry.find_all('span')
            teamName = spans[7].text
            winner = self.teams.nameTeamDict[teamName]
            winners.append(winner.bracketId)
        
        # B. Get winner of Championship game
        champ = soup.find_all('div', class_ = re.compile('center'))[0]
        winnerName = champ.find_all('span', class_ = 'name')[1].text
        winner = self.teams.nameTeamDict[winnerName]
        winners.append(winner.bracketId)
        self._assignWinners(winners)
        return self.winnerBracket

    def _assignWinners(self, winners):
        self.winnerBracket[32:] = winners[:32]
        self.winnerBracket[16:32] = winners[32:48]
        self.winnerBracket[8:16] = winners[48:56]
        self.winnerBracket[4:8] = winners[56:60]
        self.winnerBracket[2:4] = winners[60:62]
        self.winnerBracket[1:2] = winners[62:63]
        self.winnerBracket[0] = -1
        self.winnerBracket = np.array(self.winnerBracket)

def main():
    entryImporter = specificEntryImporter()
    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../data/MTeams.csv')
    
    kevUrl = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"
    test = userBracket(teams = teams, size = 64, userUrl = kevUrl)
    print(test.getWinnerBracket())
    print(len(test.winnerBracket))

    
if __name__ == '__main__':
    main()
