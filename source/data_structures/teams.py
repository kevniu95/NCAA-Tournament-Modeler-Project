import requests
import re
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

class Teams():
    """
    Class representing a list of NCAA Tournament Teams
    """
    def __init__(self, teams = None, teamImporter = None):
        """
        Specify either a list of individual Team(s) or use teamImporter to initialize
        """
        # Public attrs
        self.teams = teams # List of teams
        self.teamImporter = teamImporter
        
        # Private attrs
        self._predIdDict = None
        self._nameTeamDict = None
        # Initialization f(x)
        if self.teams is None:
            self.initiateTeams()
        elif self.teamImporter is None:
            print("Please provide either a list of Team objects or a teamImporter"\
                "that can be used to initialize a list of Team objects")
    
    def initiateTeams(self):
        self.teams = self.teamImporter.teams

    @property 
    def nameTeamDict(self):
        """
        Creates Dictionary between team name and actual Team entry
        """
        if self._nameTeamDict is None:
            self._nameTeamDict = {}
            for team in self.teams:
                self._nameTeamDict[team.name]  = team
        return self._nameTeamDict

    @nameTeamDict.setter
    def round(self, value):
        print("nameTeamDict is an internally-determined property and cannot be reset!")
        return
    
    def setPredIds(self, file):
        """
        Establishes prediction - lookup IDs for each team in Teams list
        """
        # Set self.teamDict
        self._setPredLookup(file)

        # Then use that to assign predIds to each team in list
        for team in self.teams:
            team.predId = self._predIdDict[team.name]

    def _setPredLookup(self, file):
        """
        Creates lookup to use in setting up Prediction Ids (function below)
        Input:
        # NOTE: Look to make more general in future if necessary
            -file: For now, a CSV file containing lookup between team names and Kaggle competition IDs
            - i.e., this version is specific to input used in Kaggle competition
        Returns:
            -Dictionary with proper ID for each team in team List
        """
        predIdDict = {}
        with open(file, 'r') as file:
            for num, row in enumerate(file):
                if len((row[row.rfind(',') + 1:])) > 1 and num > 0:
                    name = row[row.rfind(',') + 1 :].strip()
                    predId = row[:row.find(',')].strip()
                    predIdDict[name] = predId
        self._predIdDict = predIdDict
        
class Team():
    """
    Class representing NCAA Tournament Team
    """
    def __init__(self, bracketId, name, seed):
        self.bracketId = bracketId
        self.name = name
        self.seed = seed
        self.predId = None # Initialized in Teams class
        self.pickPct = dict(zip(range(5), [None] * 5))
    
    def setPick(self, round, pct):
        if isinstance(pct, str) and '.' in pct and '%' in pct:
            self.pickPct[round] =  float(pct.strip('%'))/100
        elif isinstance(pct, str):
            print("Unable to set pick percentage for this team - unworkable string format")
        else:
            self.pickPct[round] = pct
    
    def __str__(self):
        return f"{self.seed} {self.name} {self.predId}"

    def __repr__(self):
        return f"{self.seed} {self.name} {self.predId}"

    def __eq__(self, other):
        return self.predId == other.predId
    
    def __geq__(self, other):
        return self.predId >= other.predId
    
    def __leq__(self, other):
        return self.predId <= other.predId
    
    def __gt__(self, other):
        return self.predId > other.predId
    
    def __lt__(self, other):
        return self.predId < other.predId
    
    def __ne__(self, other):
        return self.predId != other.predId

class teamImporter():
    """
    Abstract teamImporter class 
    
    Initializes list of individual Team(s) to be used in Teams class
    """
    def __init__(self):
        self.teams = [None] * 64
    
    @abstractmethod
    def initiateTeams(self):
        pass

class SpecificEntryImporter(teamImporter):
    """
    Subclass of teamImporter built to import ESPN
    national web page (i.e., "People's Bracket")
    """
    def __init__(self, url = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"):
        super().__init__()
        self.url = url
        self.initiateTeams()
    
    def initiateTeams(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        slots = soup.find_all('div', class_= re.compile('slot s_[0-9]*$'))
        
        teamCtr = 0 #Forms bracketID for each individual team
        for slot in slots:
            # Get Seed
            seed_tag = slot.find_all('span', class_ = 'seed')
            seed = seed_tag[0].text
            # Get Name
            team_tag = slot.find_all('span', class_ = 'name')
            name = team_tag[0].text
            # Create Team
            self.teams[teamCtr] = Team(bracketId = teamCtr, name = name, seed = seed)
            teamCtr += 1

class teamImporterBracketologyESPN(teamImporter):
    """
    Subclass of teamImporter built to import ESPN
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
        return Teams(self.teams)
    
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
    # testImport = teamImporterBracketologyESPN()
    # for teamEntry in testImport.teams:
    #     print(teamEntry)

    entryImporter = SpecificEntryImporter()
    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../data/MTeams.csv')
    # for team in teams.teams:
        # print(team)
    