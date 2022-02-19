from abc import ABC, abstractmethod
from string import digits
import requests
from bs4 import BeautifulSoup
import pandas as pd


class CrowdPickGetter():
    def __init__(self):
        pass

    @abstractmethod
    def getRounds(self):
        pass

# Per Open-Closed / Liskov:
# This needs same output style as ESPNCrowdPickGetter if you want to use it

# class MockCrowdPickGetter(CrowdPickGetter):
#     def __init__(self, input = 'WhoPickedWhom - Mock.xlsx'):
#         self.input = input
#     def getCrowdPicks(self):
#         allCols = []
#         df = pd.read_excel(self.input,sheet_name = 'Sheet2', header = None)
#         for col in df.columns:
#             newCol = df[col].to_numpy()
#             allCols.append(newCol)
#         return allCols

class ESPNCrowdPickGetter(CrowdPickGetter):
    def __init__(self, url = "https://fantasy.espn.com/tournament-challenge-bracket/2021/en/whopickedwhom#"):
        self.url = url
        
    def _scrapePicks(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        allCols = [None] * 6
        for body in soup.find_all('tbody'):
            for row in body.find_all('tr'):
                for num2, cell in enumerate(row.find_all('td')):
                    if allCols[num2] is None:
                        allCols[num2] = [cell.text]
                    else:
                        allCols[num2].append(cell.text)   
        return allCols

    def getCrowdPicks(self): 
        finalArr = [None] * 6
        scrapedOutput = self._scrapePicks()
        for num, arr in enumerate(scrapedOutput):
            finalCol = self._processColumn(arr)
            finalArr[num] = finalCol
        
        teams = [i[0] for i in finalArr[1]]
        for num, arr in enumerate(finalArr):
            finalArr[num] = [i[1] for i in arr]
        finalArr.insert(0, teams)
        return finalArr 

    def _processColumn(self, arr):
        finalArr = []
        for teamEntry in arr:
            teamEntry = teamEntry.lstrip(digits)
            teamName, teamProb = teamEntry.split('-')
            teamProb = int(float(teamProb[:-1])) / 100.0
            finalArr.append((teamName, teamProb))
        finalArr.sort()
        return finalArr


crowdPickerESPN = ESPNCrowdPickGetter()
# crowdPickerMock = MockCrowdPickGetter()

print(crowdPickerESPN.getCrowdPicks())
# print(crowdPickerMock.getCrowdPicks())