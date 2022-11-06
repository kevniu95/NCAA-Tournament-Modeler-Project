"""
Create large FanPool:
- Create 5 million instances of FansBracket and save to
DynamoDB
- When evaluating any user entry, use some partition
of these 5 million saved instances, so don't have
to calculate on the spot
"""

import sys
import numpy as np
import os
import boto3
import time
from collections import Counter
sys.path.insert(0, '/home/ec2-user/ncaa/source/simulation_models/')
sys.path.insert(0, '../../source/data_structures/')
sys.path.insert(0, '../../source/simulation_models/')
from teams import Team, Teams, SpecificEntryImporter
from fansBracket import FansBracket
from predictionBracket import PredictionBracket
from predictions import Predictions, KagglePredictionsGenerator
from simulation import Simulation

dynamodb = boto3.resource('dynamodb')
fanPool = dynamodb.Table('fanPool')

# (fanEntry_id, time_created, winnerArray)
# (id, time_created, winnerArray)

if __name__ == '__main__':
    dirPath = os.path.dirname(os.path.realpath(__file__))
    generator = KagglePredictionsGenerator(f'{dirPath}/../../source/data/kaggle_predictions/xgb_preds2022.csv')
    predictions = Predictions(generator)

    teams = Teams()
    teams.setPredIds(file = f'{dirPath}/../../source/data/MTeams_.csv')
    testBracket = PredictionBracket(inputObject = predictions, teams = teams, size = 64)
    
    n = 1
    a = Simulation(predBracket = testBracket, poolSize = n)
    percentiles= []
    for i in range(100):
        a.runSimulation(resetPreds = False)
        percentiles.append(float(a.percentile))
    print(percentiles)
    print(np.std(percentiles, ddof = 1)) 
    print(np.sqrt(n) * np.std(percentiles, ddof = 1))
    
        # print(a.predBracket.winnerBracket)
        # print({i:(a.fanPool == i).sum() for i in a.fanPool[:, -1]})
    
    # entryImporter = SpecificEntryImporter()
    # teams = Teams(teamImporter = entryImporter)
    # teams.setPredIds(file = '../../source/Data/MTeams_.csv')
    
    # test = FansBracket(teams = teams, size = 64)
    # a = {i : 10000  for i in range(192)}
    # print(sys.getsizeof(a))
    # for i in range(1):
    #     a = test.getWinnerBracket()
    #     arr_string = a.tobytes()
    #     print(a.nbytes)
        
        # b = fanPool.put_item(Item = {'fan_entry_id' : i,
                                    # 'time' : int(time.time()),
                                    # 'array' : arr_string})
        
        


