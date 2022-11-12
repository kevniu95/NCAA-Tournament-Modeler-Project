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

def readDynamoData(app : Flask, tableName : str, **kwargs):
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
    saveHistPlots = {}
    for k, v in entry_results['entryAtSize'].items():
        saveHistPlots[k] = entry_results['entryAtSize'][k]['histPlot']
        del entry_results['entryAtSize'][k]['histPlot']
    
    # 2. Edit data and write to DDB
    write_data = json.loads(json.dumps(entry_results))
    write_data = {k : v for k, v in write_data.items() if k != 'visualization'}
    writeToDynamo(app, DYNAMO_DB_META, write_data)

    # 3. Re-attach histogram plots
    for k,v in entry_results['entryAtSize'].items():
        entry_results['entryAtSize'][k]['histPlot'] = saveHistPlots[k]
        
def writeToDynamoData(app : Flask, entry_results) -> None:
    # 1. Write data
    write_data = {k : v for k,v in entry_results.items() if k in ['entry_id', 'simulation_id', 'visualization']}
    write_data = json.loads(json.dumps(write_data))
    writeToDynamo(app, DYNAMO_DB_DATA, write_data)

def readDynamoDataMeta(app, **read_kwargs):
    return readDynamoData(app, DYNAMO_DB_META, **read_kwargs)