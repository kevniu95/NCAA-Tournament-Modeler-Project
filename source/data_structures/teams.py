import requests
import re
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import Dict, Any

class Team():
    """
    Class representing NCAA Tournament Team
    """
    def __init__(self, bracketId : int, name : str, seed : int):
        """
        bracketId : int -  indicates the id of the team on the bracket
                            -identifies teams within context of specific bracket 
                            structure for a given year
        predId : int - indicates id of team in predictions structure
                            -NOTE: predictions are generated using separate methodology
                            -Therefore teams need identifier for where they fit in bracket 
                            structure (bracketId), but also identifier for predictions (predId)    
        """
        self.bracketId : int = bracketId
        self.name : str = name
        self.seed : int = int(seed)
        self.predId : int = None # Initialized in Teams class
        self.pickPct : Dict[int, int] = dict(zip(range(5), [None] * 5))
    
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

class TeamImporter():
    """
    Abstract TeamImporter class 
    
    Initializes list of individual Team(s) to be used in Teams class
    using some url link as the "source of truth" for creating 
    the set of teams
    """
    def __init__(self):
        self.teams : list[Team] = [None] * 64
    
    @abstractmethod
    def _initiateTeams(self):
        pass

class SpecificEntryImporter(TeamImporter):
    """
    Subclass of TeamImporter built to import a 
    specific ESPN bracket entry 
    -(e.g., kniu's 2022 bracket entry)
    """
    def __init__(self, url = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"):
        super().__init__()
        self.url : str = url
        self._initiateTeams()
    
    def _initiateTeams(self):
        """
        Updates self.teams to hold Team objects
        Fills out using ESPN bracket template
        """
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
            self.teams[teamCtr] = Team(bracketId = teamCtr, name = name, seed = int(seed))
            teamCtr += 1

class TeamImporterBracketologyESPN(TeamImporter):
    """
    Subclass of TeamImporter built to import ESPN
    bracketology web page
    -NOTE: this is most useful when the NCAA Tournament
        bracket has not actually been determined in 
        real life yet and it'd still be helpful to 
        visualize using a "mock" tournament
    """
    def __init__(self, bracketologyURL : str = "http://www.espn.com/mens-college-basketball/bracketology"):
        super().__init__()
        self.bracketologyURL : str = bracketologyURL
        self._initiateTeams()
        
    def _initiateTeams(self):
        teamCtr = 0
        page = requests.get(self.bracketologyURL)
        soup = BeautifulSoup(page.content, 'html.parser')

        bracketContainers = soup.find_all('article', class_= 'bracket__container')
        for bracketContainer in bracketContainers:
            bracketItems = bracketContainer.find_all('li', class_ = 'bracket__item')
            for bracketItem in bracketItems:
                seed, teamName = self.readBracketItem(bracketItem)
                self.teams[teamCtr] = Team(teamCtr, teamName, seed)
                teamCtr += 1
    
    def readBracketItem(self, bracketItem):
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

class Teams():
    """
    Class representing a list of NCAA Tournament Teams
    """
    def __init__(self, teams : list[Team] = None, teamImporter : TeamImporter = None):
        """
        Specify either a list of individual Team(s) or use teamImporter to initialize
        """
        self.teams : list[Team] = teams # List of teams
        self.teamImporter : TeamImporter = teamImporter
        
        self._predIdDict : Dict[str, int] = None 
        self._nameTeamDict : Dict[str, Team] = None 

        if self.teams is None:
            self._initiateTeams()
        elif self.teamImporter is None:
            raise ValueError("Please provide either a list of Team objects or a teamImporter"\
                "that can be used to initialize a list of Team objects")
            
    def _initiateTeams(self):
        self.teams : list[Team] = self.teamImporter.teams

    @property 
    def nameTeamDict(self) -> Dict[str, Team]:
        """
        Dictionary between team name and actual Team entry
        """
        if self._nameTeamDict is None:
            self._nameTeamDict = {team.name : team for team in self.teams}
        return self._nameTeamDict

    @nameTeamDict.setter
    def nameTeamDict(self, value : Any) -> None:
        print("nameTeamDict is an internally-determined property and cannot be reset!")
        return
    
    def setPredIds(self, file : str):
        """
        Creates predIdDict (more info below)
        NOTE: For each Team object in Teams list, the Team predId attribute
            is updated HERE
        """
        self._setPredLookup(file)

        for team in self.teams:
            team.predId = self._predIdDict[team.name]

    def _setPredLookup(self, file : str):
        """
        Creates dictionary between team name and prediction id
            - NOTE: Look to generalize if moving past Kaggle set-up 
                and their ids
        """
        predIdDict = {}
        with open(file, 'r') as file:
            for num, row in enumerate(file):
                if len((row[row.rfind(',') + 1:])) > 1 and num > 0:
                    name = row[row.rfind(',') + 1 :].strip()
                    predId = row[:row.find(',')].strip()
                    predIdDict[name] = int(predId)
        self._predIdDict = predIdDict
        assert len(self._predIdDict) == len(self.nameTeamDict)
        assert sorted(self._predIdDict.keys()) == sorted(self.nameTeamDict.keys())

if __name__ == "__main__":
    testImport = TeamImporterBracketologyESPN()
    entryImporter = SpecificEntryImporter()
    
    # for i in range(len(testImport.teams)):
    #     print(entryImporter.teams[i])
    #     print(testImport.teams[i])
    #     print()

    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../data/MTeams.csv')
    for team in teams.teams:
        print(team)
    