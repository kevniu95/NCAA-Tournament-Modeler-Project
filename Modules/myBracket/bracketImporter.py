import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

class Team():
    """
    Class representing NCAA Tournament Team
    """
    def __init__(self, id, name, region, seed):
        self.id = id
        self.name = name
        self.seed = seed
        self.region = region
    
    def __str__(self):
        return f"Team {self.id:>07b}; {self.name}; {self.region}; {self.seed}"

    def __repr__(self):
        return f"Team {self.id:>07b}; {self.name}; {self.region}; {self.seed}"

class bracketImporter():
    """
    Abstract bracketImporter class 
    """
    def __init__(self):
        self.teams = [None] * 64
    
    @abstractmethod
    def initiateTeams(self):
        pass

class bracketImporterBracketologyESPN(bracketImporter):
    """
    Subclass of bracketImporter built to import ESPN
    bracketology web page
    """
    def __init__(self, bracketologyURL = "http://www.espn.com/mens-college-basketball/bracketology"):
        super().__init__()
        self.bracketologyURL = bracketologyURL
        self.initiateTeams()
        
    def initiateTeams(self):
        teamCtr = 0
        page = requests.get(self.bracketologyURL)
        soup = BeautifulSoup(page.content, 'html.parser')

        bracketContainers = soup.find_all('article', class_= 'bracket__container')
        for bracketContainer in bracketContainers:
            bracketRegion = bracketContainer.find_all('h4', class_ = 'bracket__subhead')
            region = bracketRegion[0].text
            
            bracketItems = bracketContainer.find_all('li', class_ = 'bracket__item')
            for bracketItem in bracketItems:
                seed, teamName = self.readBracketItem(bracketItem)
                self.teams[teamCtr] = Team(teamCtr, teamName, region, seed)
                teamCtr += 1
    
    def readBracketItem(self, bracketItem):
        """
        TODO: UPDATE THIS AS NEEDED
        """
        bracketItemList = bracketItem.text.split(' ', 1)
        seedPortion = bracketItemList[0]
        teamPortion = bracketItemList[1].strip()

        if seedPortion.endswith('aq'):
            seed = int(seedPortion[:-2])
        else:
            seed = int(seedPortion)
        
        if teamPortion[0].isalnum():
            teamName = teamPortion
        else:
            teamName = teamPortion[1:].strip()
    
        if teamName.endswith(' - aq'):
            teamName = teamName[:-5]
        return seed, teamName


if __name__ == "__main__":
    testImport = bracketImporterBracketologyESPN()
    for teamEntry in testImport.teams:
        print(teamEntry)