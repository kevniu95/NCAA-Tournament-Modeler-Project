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

def invalidRoute(entryId):
    try:
        entryId = int(entryId)
        return False
    except:
        return True

@app.route("/", methods = ['GET'])
def simulate():
    thisId = str(uuid.uuid4())
    return render_template('simulate.html')

@app.route('/results', methods = ['POST'])
def results():
    start = time.time()
    
    # 1. Use link to get bracket entry id
    link = request.form['espnLink']
    req_addr = request.remote_addr
    if len(link) == 0:
        link = "https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry?entryID=53350427"    
    espnId = int(link[link.rfind('=') + 1:])
    
    # 2. Read Dynamo DB Data to see if bracket entry 
    #    already in table, get sim_id
    read_kwargs = {'KeyConditionExpression' : Key('entry_id').eq(espnId),
                    'Limit' : 1,
                    'ScanIndexForward' : False,
                    'ReturnConsumedCapacity' : 'TOTAL'}
    response = ddb_funcs.queryDynamoMeta(app, **read_kwargs)
    sim_id = 1
    if (response and response['ResponseMetadata']['HTTPStatusCode'] == 200 and
        response['Count'] > 0):
        sim_id = int(response['Items'][0]['simulation_id']) + 1
    
    # 3. Create dictionary to be shipped to HTML
    #    and Dynamo DB
    entry_results = {'entry_id' : espnId,
                    'simulation_id' : sim_id,
                    'req_addr' : req_addr,
                    'score' : None,
                    'visualization' : None,
                    'entryAtSize' : {}}
    
    # 4. Run simulations
    sizes = [100, 1000, 10000, 25000]
    first = True
    sim = Simulation(myBracketUrl = link)
    for size in sizes:
        sim.runSimulation(poolSize = size, resetPreds = first)
        res = sim.scoreSimulation() #: Tuple[str, str, bytes, List[Dict]] 
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
    entry_results['entryAtSize']
    
    # 5. Write to Dynamo DB
    ddb_funcs.writeToDynamoMeta(app, entry_results)
    ddb_funcs.writeToDynamoData(app, entry_results)
        
    return render_template('results.html', results = entry_results, espnId = espnId, espnLink = link)

@app.route('/<entryId>')
def entrySummary(entryId):
    if invalidRoute(entryId):
        return "Invalid entry id!"
    read_kwargs = {'KeyConditionExpression' : Key('entry_id').eq(int(entryId)),
                    'Limit' : 25,
                    'ScanIndexForward' : False,
                    'ReturnConsumedCapacity' : 'TOTAL'}
    response_meta = ddb_funcs.queryDynamoMeta(app, **read_kwargs)
    if ddb_funcs.handleEmptyQuery(response_meta):
        return ddb_funcs.handleEmptyQuery(response_meta)

    scoreSumm = []
    metadata  = response_meta['Items'] # List(Dict)
    entryAtSizeSumm = {'100' : [], '1000' : [], '10000' : [], '25000' : []}
    for i in metadata:
        scoreSumm.append(int(i['score']))
        for k in entryAtSizeSumm.keys():
            if str(k) in i['entryAtSize'].keys():
                entryAtSizeSumm[str(k)].append(float(i['entryAtSize'][str(k)]['percentile']))
            else:
                i['entryAtSize'][str(k)] = {}
                i['entryAtSize'][str(k)]['percentile'] = -1
    
    scoreSumm = round(sum(scoreSumm) / len(scoreSumm),1)
    entryAtSizeSumm = {k : (round(sum(v) / len(v),1) if len(v) > 0 else -1) for k, v in entryAtSizeSumm.items()}
    return render_template('entrySummary.html', 
                            metadata = metadata, 
                            scoreSumm = scoreSumm, 
                            entryAtSizeSumm = entryAtSizeSumm)

@app.route('/<entryId>/<simulationId>')
def simulationResult(entryId, simulationId):
    if invalidRoute(entryId):
        return "Invalid entry id!"
    print(entryId)
    print(simulationId)
    # Need both meta data and response data read from tables
    read_kwargs = {'KeyConditionExpression' : "entry_id = :entryId and simulation_id = :simId",
                    'ExpressionAttributeValues' : {':entryId' :  int(entryId),
                                                    ':simId' : int(simulationId)},
                    'Limit' : 1,
                    'ReturnConsumedCapacity' : 'TOTAL'}
    meta_response = ddb_funcs.queryDynamoMeta(app, **read_kwargs)    
    data_response = ddb_funcs.queryDynamoData(app, **read_kwargs)
    
    if ddb_funcs.handleEmptyQuery(meta_response):
        return ddb_funcs.handleEmptyQuery(meta_response)

    if (meta_response and data_response and meta_response['Count'] > 0 
        and data_response['Count'] > 0):
        # Get response items
        entry_results = meta_response['Items'][0] # Dict
        data_item = data_response['Items'][0] # Dict
        
        # Create new entry_results item to send to HTML template
        entry_results['visualization'] = data_item['visualization']
        for size in entry_results['entryAtSize'].keys():
            entry_results['entryAtSize'][size]['histPlot'] = 'Ooops, no histogram'.encode('utf-8')
        score = entry_results['score']
        
        if 'entryAtSize' in data_response['Items'][0].keys():
            entry_results['entryAtSize'] = data_item['entryAtSize']

            for size in entry_results['entryAtSize'].keys():
                histNums = entry_results['entryAtSize'][size]['histNums']
                histPlot = Simulation.plotHistogram(histNums, int(score)) # bytes
                entry_results['entryAtSize'][size]['histPlot'] = histPlot
    entry_results['entryAtSize'] = dict(sorted(entry_results['entryAtSize'].items()))
    return render_template('results.html', results = entry_results, espnId = entryId)

app.run(host='0.0.0.0', debug=True)
