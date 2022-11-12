import sys 
import uuid
import time

from flask import (Flask, abort, flash, redirect, render_template, 
  request, session, url_for, jsonify)
from typing import Tuple, Dict, List

sys.path.insert(0, '/home/ec2-user/ncaa/source/simulation_models/')
sys.path.insert(0, '../source/simulation_models/')
sys.path.insert(0, '../AWS_setup/boto/')

import ddb_funcs
from simulation import Simulation

from boto3.dynamodb.conditions import Key

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def simulate():
    thisId = str(uuid.uuid4())
    return render_template('simulate.html')

@app.route('/results', methods = ['POST'])
def results():
    start = time.time()
    
    # 1. Use link to get bracket entry id
    link = request.form['espnLink']
    if len(link) == 0:
        link = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"    
    espnId = int(link[link.rfind('=') + 1:])
    
    # 2. Read Dynamo DB Data to see if bracket entry 
    #    already in table, get sim_id
    read_kwargs = {'KeyConditionExpression' : Key('entry_id').eq(espnId),
                    'Limit' : 1,
                    'ScanIndexForward' : False,
                    'ReturnConsumedCapacity' : 'TOTAL'}
    response = ddb_funcs.readDynamoDataMeta(app, **read_kwargs)
    sim_id = 1
    if (response and response['ResponseMetadata']['HTTPStatusCode'] == 200 and
        response['Count'] > 0):
        sim_id = int(response['Items'][0]['simulation_id']) + 1
    
    # 3. Create dictionary to be shipped to HTML
    #    and Dynamo DB
    entry_results = {'entry_id' : espnId,
                    'simulation_id' : sim_id,
                    'score' : None,
                    'visualization' : None,
                    'entryAtSize' : {}}
    
    # 4. Run simulations
    sizes = [100, 1000, 10000, 25000]
    first = True
    sim = Simulation(myBracketUrl = link)
    for size in sizes:
        sim.runSimulation(poolSize = size, resetPreds = first)
        res : Tuple[str, str, bytes, List[Dict]] = sim.scoreSimulation()
        score, percentile, histNums, visualization = res
        if first:
            entry_results['score'] = score
            entry_results['visualization'] = visualization
        
        histPlot = Simulation.plotHistogram(histNums, int(score))
        entry_results['entryAtSize'][size] = {'pool_size' : size,
                                            'percentile' : percentile,
                                            'histNums' : histNums,
                                            'histPlot' : histPlot}
        first = False
    
    # 5. Write to Dynamo DB
    ddb_funcs.writeToDynamoMeta(app, entry_results)
    ddb_funcs.writeToDynamoData(app, entry_results)
        
    return render_template('results.html', results = entry_results, espnId = espnId)

# @app.route('/specific_results/<competitors>/<neighbors>')
# def specific_results(competitors, neighbors):
#     print(neighbors)
#     return f"You have {competitors} total competitors!"

app.run(host='0.0.0.0', debug=True)
