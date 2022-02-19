import numpy as np
import math
import bracketImporter
import crowdPickImporter

crowdPickerESPN = crowdPickImporter.ESPNCrowdPickGetter()
crowdPickerMock = crowdPickImporter.MockCrowdPickGetter()

class Rounds():
    def __init__(self, pickGetter):
        self._rounds = [None] * 6
        self._pickGetter = pickGetter
        self._fillRoundPicks()
    
    @property
    def round(self):
        if self._rounds[0] is None:
            self._fillRoundPicks()
        return self._rounds

    @round.setter
    def round(self, value):
        print("Rounds information should have been set upon instantiation! Can't reset!")
        return

    def _fillRoundPicks(self):
        pickGetter = self._pickGetter
        rawRoundInfo = pickGetter.getCrowdPicks()
        
        teams = rawRoundInfo[0]
        
        roundCtr = 0
        for arr in rawRoundInfo[1:]:
            roundDict = dict(zip(teams, arr))
            self._rounds[roundCtr] = (roundCtr, roundDict)
            roundCtr += 1

    def __iter__(self):
        for round in self._rounds:
            yield round

    def __getitem__(self, roundNumber):
        return self._rounds[roundNumber]
    
    def getPotentialWinners(self, roundID):
        """
        Examples of roundID :
        -Champ game is '0'
            -Stored in in rounds[0]
        -F4 is '00' and '01' 
            -Stored in rounds[1]
        """
        potentialWinnerList = []
        currentRoundNum, currentRoundTeams = self._getTeamProbsInRound(roundID)
        for team, probOfAdvance in currentRoundTeams.items():
            matchToRoundID = (currentRoundNum + 1)
            if team[:matchToRoundID] == roundID:
                potentialWinnerList.append((team, probOfAdvance))
        return potentialWinnerList

    def _getTeamProbsInRound(self, roundID):
        roundIDMapped = len(roundID) - 1
        round = self._rounds[roundIDMapped]
        return (round[0], round[1])

# testPickGetter = crowdPickerESPN
# testRounds = Rounds(testPickGetter)
# for i in testRounds._rounds:
#     print(i)
#     print()
#print(testRounds.getPotentialWinners('0'))

class crowdBracket():
    def __init__(self):
        self.bracketList = [None] * 64
        self.rounds = Rounds()
    
    def instantiateBracket(self):
        self._instantiateFirstEntry()
        for arrayIndex in range(2, 64):
            baseIndex = arrayIndex // 2 # The "last" round that preceded this one
            baseEntryGameID = self.bracketList[baseIndex].id
            if arrayIndex % 2 == 0:
                currGameID = baseEntryGameID + "0"
            else:
                currGameID = baseEntryGameID + "1" 
            self.bracketList[arrayIndex] = crowdBracketEntry(currGameID, arrayIndex, rounds)
        
    def _instantiateFirstEntry(self):
        self.bracketList[1] = crowdBracketEntry("0", self, 1)
        
    def simulateTourney(self):
        """
        Want: A function that can apply to each node no matter what

        Will apply this function on each element in the list self.bracketList

        1. Check to see if bracket entry already has a winner - if so, pass
        2. Else
            a. Pick a winner for this game using the .pickWinner() method belonging
                to the bracketEntry
            b. Separate function that tumbles down and fills out winners
        """
        for entry in self.bracketList[1:]:
            if entry.choseWinner:
                pass
            else:
                entry.pickWinner()
                self.tumbleWinnerDown(entry)
        
    def tumbleWinnerDown(self, bracketEntry):
        currGameID, winner, arrayIndex = bracketEntry.getInfo()
        tmpWinner = winner
        tmpWinner = tmpWinner.replace(currGameID, "", 1)

        while len(tmpWinner) > 1:
            currLetter = tmpWinner[0]
            arrayIndex = 2 * arrayIndex + int(currLetter)
            self.bracketList[arrayIndex]._winner = winner
            tmpWinner = tmpWinner[1:]
        
class crowdBracketEntry():
    def __init__(self, id, arrayIndex, rounds):
        self.id = id
        self.rounds = rounds
        self.arrayIndex = arrayIndex
        self._winner = None
        self._potentialWinners = []
        self._choseWinner = False

    def __repr__(self):
        return f"Game ID: {self.id}\nBracketArrayIndex: {self.arrayIndex}\nWinner: {self._winner}\nPotential Winners: {self._potentialWinners}"

    def __str__(self):
        return f"Game ID: {self.id}\nBracketArrayIndex: {self.arrayIndex}\nWinner: {self._winner}\nPotential Winners: {self._potentialWinners}"

    @property
    def potentialWinners(self):
        idLength = len(self.id)
        if len(self._potentialWinners) == 0:
            self._potentialWinners = self._rounds.getPotentialWinners(self.id)
        return self._potentialWinners
    
    @potentialWinners.setter
    def potentialWinners(self):
        print("Sorry, not allowed to set the winners, check back in implementation of crowdBracketEntry class!")
        return

    @property
    def winner(self):
        if self._winner is None:
            print("Need to pick the winner for this round first!")
        else:
            return self._winner
    
    @winner.setter
    def winner(self, value):
        if value.startswith(self.id):
            self._winner = value
            self._choseWinner = True
        else:
            print(f"Team {value} is not allowed to win game {self.id}!")
        
    @property
    def choseWinner(self):
        return self._choseWinner

    @choseWinner.setter
    def choseWinner(self):
        if self._choseWinner:
            print("Winner for this game has already been determined!")
        else:
            print("Not allowed to choose winner directly. Please run the pickWinner() method on this object.")
    
    def pickWinner(self):
        currPotentialWinners = self._potentialWinners
        currPotentialWinners.sort(key = lambda x: x[1], reverse = True)
        assert currPotentialWinners[0][1] > currPotentialWinners[1][1]
        unifDraw = np.random.uniform(0, 1)
        self._winner = self.pickWinnerGivenDraw(currPotentialWinners, unifDraw)
        self._choseWinner = True
        
    def pickWinnerGivenDraw(self, potentialWinners, draw):
        cdf = 0
        for entry in potentialWinners:
            prob = entry[0]
            team = entry[1]
            cdf += prob
            if draw < cdf:
                return team
        print("Uh-oh, no team was chosen to win in this bracket entry!")
        return None

    def getInfo(self):
        return self.id, self.winner, self.arrayIndex

# teamImport = bracketImporter.bracketImporterBracketologyESPN()
# teams = teamImport.teams
# print(teams)

# test = crowdBracket()
# test.instantiateBracket()

# print()
# test.bracketList[1].winner = '0111111'
# test.bracketList[2].winner = '0000000'
# test.tumbleWinnerDown(test.bracketList[1])
# test.tumbleWinnerDown(test.bracketList[2])

# for num, i in enumerate(test.bracketList):
#     print(i)
#     print()


'''
2.18 TODO:
Link up teams from bracketImporter to teams in Rounds information
    -Or put another way, need to know what actual team IDs are now that we have
        the "who picked whom" information from the internet
    -Should be final piece keeping us from simulating "the people" brackets
    -The Rounds information should ultimately have not just Team ID, but actual
        team object

Who controls pickgetter? Do I separately instantiate rounds each time and then pass
    it through to crowdBracket with pickGetter already set? Or should I let crowdBracket
    instantiate?

Do you want crowdBracket to reset itself or do you want many instances of it?
    -That might answer above question on pickGetter (b/c you don't want to have
    to re-instantiate it everytime you make a new crowdBracket)

Should fillRoundPicks also be offloaded? This gets back to decision made yesterday
    to collapse round instantiation and rest of functionality. Is it reasonable
    to think importing data will become tough/different enough to warrant becomig its
    own job?
-Maybe change back so initializer is contained elsewhere, maybe stored in crowdPickImporter
module. Does it really seem reasonable to have 7 random arrays, one of which represents teams
and the other six representing  be the public interface
that Rounds is leaning on?

2.18
DID:
UPSTREAM: 
-Implemented an actual subclass of CrowdPickGetter that will work on the actual ESPN web format
-Re-factored code
    -Round class removed - Round role is served in Rounds by rounds object
    -Collapsed PotentialWinner-determining class and Round class since both were tied to rounds
        -PotentialWinner was calculating what Round instantiated

2/17 
DID:
DOWNSTREAM
-In CrowdBracket class (i.e., went further downstream in terms of actually generating simulation)
    -Implemented TumbleWinnerDown() in CrowdBracket class
    -Implemented InstantiateTourney()

UPSTREAM
-Built bracketImporter module to handle generating team ID's based on actual bracket 
    -(Webscraping to get teams their proper IDs)
-Built Rounds and Round data structures 
    -Rounds holds individual Round in array
    -Round has round number, and team odds of winning in that specific round

2.17 TODO: 
Keep PotentialWinnerGetter, b/c that does something separate from just holding the rounds data

Rounds data structure that holds the rounds, where each round has:
    -Key with round number (0 is champ game, 1 is semis .... 6 is first round)
    -Value with Round dicts
        
Data structure that holds one round:
    -Each entry is {Team : pct of winning in that rd}
    -Team can be an actual Team object to make things easier

Teams data structure with
    -Team IDs that make everything happen (like structure 000000 for Duke in 2019)
    -The normal team name so humans can read and understand

Larger bracket structure that integrates many BracketEntries
    -This is where, at very least, need to connect all bracket entries
    -Fill backwards once winner chosen in specific entry
    -Traverse down tree, checking to see if entires are filled
''' 