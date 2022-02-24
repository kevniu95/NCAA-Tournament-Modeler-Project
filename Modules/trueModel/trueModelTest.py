import unittest
import trueModel

class checkClasses(unittest.TestCase):
    def setUp(self):
        self.preds = trueModel.Predictions()
        self.bracket = trueModel.Bracket(64, self.preds)

        self.bracketEntry0 = trueModel.BracketEntry(1)
        self.bracketEntry1 = trueModel.BracketEntry(1)
        self.bracketEntry1.addTeam('1451')

        self.bracketEntry2 = trueModel.BracketEntry(1)
        self.bracketEntry2.addTeam('1451')
        self.bracketEntry2.addTeam('1452')

        self.game = self.bracketEntry2.game

    def test_completePredictions(self):
        # Make k, v pair for all teams in data
        predictions = self.preds
        uniqueTeams = list(set([i[0] for i in predictions.predictions.keys()]))
        uniqueTeams.sort()
        predIDs = []
        for i in range(len(uniqueTeams)):
            for j in range(i + 1, len(uniqueTeams)):
                predIDs.append((str(uniqueTeams[i]), str(uniqueTeams[j])))
            
        # And check to see an entry is available in predictions.predictions
        unaccountedForMatchups = len([i for i in predIDs if i not in predictions.predictions.keys()])
        self.assertEqual(unaccountedForMatchups, 0)

    def test_predictionsAreProbs(self):
        predictions = self.preds.predictions
        ctr = 0
        outOfBoundsProbs = len([prob for prob in predictions.values() if (prob < 0) or (prob > 1)])
        self.assertEqual(outOfBoundsProbs, 0)

    def test_initialBracketGood(self):
        # Checks that back half of bracket is filled
        filled = int(self.bracket.size / 2)
        self.assertIsNone(self.bracket.gameBracket[filled - 1])
        
        # Checks back half of bracket is a power of 2
        tmp = filled
        while tmp > 1:
            self.assertEqual(tmp % 2, 0)
            tmp /= 2

    def test_probsAreProper(self):
        self.bracket.simulateTournament(reset = False)
        for bracketEntry in self.bracket.gameBracket[1:]:
            # Checks tm1 < tm2 in all games in bracket
            tm1 = bracketEntry.game.team1
            tm2 = bracketEntry.game.team2
            self.assertLess(tm1, tm2)

            # Checks game probs are properly defined
            tm1Wpct = bracketEntry.game._getTeamOneWinPctWith(self.preds)
            self.assertGreater(tm1Wpct, 0)
            self.assertLess(tm1Wpct, 1)
        
    def test_BracketEntryBehavior(self):
        self.assertIsNone(self.bracketEntry0.game)
        self.assertIsNone(self.bracketEntry1.game)
        self.assertIsNotNone(self.bracketEntry2.game)
        
    def test_SimulateTournament(self):
        self.bracket.simulateTournament(reset = False)
        zeroIsNone = True
        allOtherGamesFilled = True
        for i in [self.bracket.gameBracket, self.bracket.winnerBracket]:
            if i[0] is not None:
                zeroIsNone = False
            if len([entry for entry in i if entry is not None]) < self.bracket.size - 1:
                allOtherGamesFilled = False
        
        self.assertTrue(zeroIsNone and allOtherGamesFilled)

    def test_TournamentReset(self):
        self.bracket.simulateTournament(reset = False)
        self.bracket.bracketReset()

        noWinners = True
        halfOfEntriesAreGames = True
        
        if len([i for i in self.bracket.winnerBracket if i is not None]) > 0:
            noWinners = False
        
        if len([i for i in self.bracket.gameBracket if i is not None]) * 2 != self.bracket.size:
            halfOfEntriesAreGames = False

        self.assertTrue(noWinners and halfOfEntriesAreGames)
                

if __name__ == "__main__":
    unittest.main()

    # test = checkClasses()
    # test.setUp()
    # test.test_TournamentReset()