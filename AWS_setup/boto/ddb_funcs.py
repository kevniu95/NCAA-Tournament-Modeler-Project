import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.conditions import Key
from typing import Dict

from flask import (Flask, abort, flash, redirect, render_template, 
  request, session, url_for, jsonify)

MY_REGION = 'us-east-1'
DYNAMO_DB_META = 'entrySimulationMeta'
DYNAMO_DB_DATA = 'entrySimulationData'

# ==================
# Generalized Boto functions
# ==================
def writeToDynamo(app : Flask, tableName : str, write_data : Dict) -> None:
    dynamodb = boto3.resource('dynamodb', region_name = MY_REGION)
    table = dynamodb.Table(tableName)
    try:
        table.put_item(Item = write_data)
    except ClientError as e:
        app.logger.error(f'ClientError while uploading to Dynamo DB: {e}')
        return abort(500)
    except Exception as e:
        app.logger.error(f'Unspecified error while uploading to Dynamo DB: {e}')
        return abort(500)

def queryDynamo(app : Flask, tableName : str, **kwargs) -> Dict:
    dynamodb = boto3.resource('dynamodb', region_name = MY_REGION)
    table = dynamodb.Table(tableName)
    try:
        response = table.query(**kwargs)
        return response
    except ClientError as e:
        app.logger.error(f'ClientError while uploading to Dynamo DB: {e}')
        return abort(500)
    except Exception as e:
        app.logger.error(f'Unspecified error while uploading to Dynamo DB: {e}')
        return abort(500)

# ==================
# Used by App   
# ==================
def writeToDynamoMeta(app : Flask, entry_results : Dict) -> None:
    # 1. Remove the histogram plots before saving to DDB
    saveHist = {'plots' : {},
                'nums' : {}}
    for k, v in entry_results['entryAtSize'].items():
        saveHist['plots'][k] = entry_results['entryAtSize'][k]['histPlot']
        saveHist['nums'][k] = entry_results['entryAtSize'][k]['histNums']
        del entry_results['entryAtSize'][k]['histPlot']
        del entry_results['entryAtSize'][k]['histNums']
        
    # 2. Edit data and write to DDB
    write_data = json.loads(json.dumps(entry_results))
    for k, v in write_data.items():
        write_data[k] = v
        if k == 'visualization':
            write_data[k] = v[:7]
    writeToDynamo(app, DYNAMO_DB_META, write_data)

    # 3. Re-attach histogram plots
    for k,v in entry_results['entryAtSize'].items():
        entry_results['entryAtSize'][k]['histPlot'] = saveHist['plots'][k]
        entry_results['entryAtSize'][k]['histNums'] = saveHist['nums'][k]
        
def writeToDynamoData(app : Flask, entry_results : Dict) -> None:
    saveHist = {'plots' : {}}
    # 1. Write data
    entry_results = {k : v for k,v in entry_results.items() if k in ['entry_id', 'simulation_id', 'visualization', 'entryAtSize']}
    for k, v in entry_results['entryAtSize'].items():
        saveHist['plots'][k] = entry_results['entryAtSize'][k]['histPlot']
        del entry_results['entryAtSize'][k]['histPlot']
        
    write_data = json.loads(json.dumps(entry_results))
    writeToDynamo(app, DYNAMO_DB_DATA, write_data)

    # 3. Re-attach histogram plots
    for k,v in entry_results['entryAtSize'].items():
        entry_results['entryAtSize'][k]['histPlot'] = saveHist['plots'][k]

def queryDynamoMeta(app : Flask, **read_kwargs) -> Dict:
    return queryDynamo(app, DYNAMO_DB_META, **read_kwargs)

def queryDynamoData(app : Flask, **read_kwargs) -> Dict:
    return queryDynamo(app, DYNAMO_DB_DATA, **read_kwargs)

def handleEmptyQuery(resp : Dict):
    """
    resp is DynamoDB response to a query
    """
    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        return "Uh-oh, no information on this bracket entry yet!"
    elif resp['Count'] == 0:
        return "Uh-oh, no information on this bracket entry yet!"
    