# True Model

# from multiprocessing.sharedctypes import Value
# import numpy as np
# from abc import ABC, abstractmethod
# import random
# import math
from teams import Teams, specificEntryImporter
from predictions import blankTemplate, simpleSeedTemplate, Predictions, \
    KagglePredictionsGenerator
from bracket import Bracket

if __name__ == "__main__":

    """
    A. Import Predictions and Teams
    -Based on sample predictions for all 64*63 games in 2021 NCAA Tournament
    """
    generator = KagglePredictionsGenerator('seedPreds2022.csv')
    predictions = Predictions(generator)
    # predictions = Predictions()
    # for game, leftTeamWinProb in predictions.predictions.items():
        # print(f"Teams involved: {game}\nProbability left team wins: {leftTeamWinProb}\n")
    
    entryImporter = specificEntryImporter()
    teams = Teams(bracketImporter = entryImporter)
    teams.setPredIds(file = 'MTeams.csv')
    
    """
    Only need to do this the one time to set up
    2022 predictions template
    -And simple model by seed
    """
    # temp1 = blankTemplate(2022, teams)
    # temp1.writeMatchups('predTemplate2022')

    # temp2 = simpleSeedTemplate(2022, teams)
    # temp2.writeMatchups('seedPreds2022')

    """
    B. Create Bracket
    - Note bracket randomly created given set of 64 teams
    - Will update for 2022 NCAA Tournament
    """

    testBracket = Bracket(predictions, teams = teams, size = 64)
    # Note that game bracket has half-filled (all first round games)
    print(testBracket.gameBracket)
    # But winner braket is unfilled
    print(testBracket.winnerBracket)

    """
    C. Simulate Tournament
    """
    testBracket.simulateTournament(reset = False)
    print(testBracket.gameBracket)
    print(testBracket.winnerBracket)