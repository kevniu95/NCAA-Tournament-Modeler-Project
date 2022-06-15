import sys
import os
sys.path.append('../')

import unittest
from teams import *

class CheckEntryImporter(unittest.TestCase):
    """
    Also checks Team class objects as they become instantiated in this class (EntryImporter)
    """
    def setUp(self):
        testUrl = 'https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=71036256'
        self.entryImporter = SpecificEntryImporter(url = testUrl)
    
    def test_initiateTeams(self):
        """
        Checks list of teams that is initialized
        - See specific by-team checks below
        """
        self.assertEqual(len(self.entryImporter.teams), 64)
        ctr = 0
        for team in self.entryImporter.teams: 
            # Check each entry is a Team
            self.assertTrue(self.checkTeam(team, ctr))
            ctr += 1
            
    def checkTeam(self, team, ctr):
        """
        Specific checks for each Team object instantiated
        """
        self.assertTrue(isinstance(team, Team))
    
        self.assertGreater(int(team.seed), 0)
        self.assertLess(int(team.seed), 17)

        self.assertTrue(isinstance(team.name, str))
        self.assertEqual(team.bracketId, ctr)
        
        self.assertIsNone(team.predId)
        self.assertTrue(isinstance(team.pickPct, dict))
        return True
            
class CheckTeams(unittest.TestCase):
    def setUp(self):
        testUrl = 'https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=71036256'
        self.entryImporter = SpecificEntryImporter(url = testUrl)
        self.teams = Teams(teams = None, teamImporter = self.entryImporter)
        self.teams.setPredIds(file = '../../data/MTeams.csv')
    
    def test_setPredIds(self):
        """
        Check each Team object in teams.teams list
        - This time extra check on validity of prediction id
           , which is assigned in setPredIds() method of Teams class
        """
        self.assertEqual(len(self.teams.teams), 64)
        ctr = 0
        for team in self.teams.teams: 
            # Check each entry is a Team
            self.assertTrue(self.checkTeam(team, ctr))
            ctr += 1
            
    def checkTeam(self, team, ctr):
        self.assertTrue(isinstance(team, Team))
        self.assertGreater(int(team.seed), 0)
        self.assertLess(int(team.seed), 17)

        self.assertTrue(isinstance(team.name, str))
        self.assertEqual(team.bracketId, ctr)
        
        self.assertTrue(isinstance(team.pickPct, dict))

        # Add extra check that prediction ID is updated and valid
        self.assertGreater(int(team.predId), 1000)
        self.assertLess(int(team.predId), 1600)
        return True
    
    def test_setPredIdsDict(self):
        """
        Check that team name : predId dict seems legitimate
        """
        lastV = 0
        self.assertEqual(len(self.teams._predIdDict), 64)
        for k,v in self.teams._predIdDict.items():
            self.assertIsInstance(k, str)
            self.assertGreater(int(v), 1000)
            self.assertLess(int(v), 1600)
            self.assertGreater(int(v), lastV)
            lastV = int(v)

    def test_nameTeamDict(self):
        """
        Check that team name : Team object dict seems legitimate
        """
        lastBracketId = -1
        self.assertEqual(len(self.teams.nameTeamDict), 64)
        for k,v in self.teams.nameTeamDict.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, Team)

            self.assertGreater(int(v.bracketId), lastBracketId)
            lastBracketId = int(v.bracketId)

def run_some_tests():
    # Run only the tests in the specified classes
    test_classes_to_run = [
                            CheckEntryImporter,
                            CheckTeams
                            ]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)
        
    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

if __name__ == '__main__':
    run_some_tests()