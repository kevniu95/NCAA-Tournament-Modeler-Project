# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# app = Flask(__name__)

import sys 
import uuid
import os
import time
# print(sys.path)
sys.path.insert(0, '/home/ec2-user/ncaa/source/simulation_models/')
sys.path.insert(0, '../source/simulation_models/')
# print(sys.path)


from flask import (Flask, abort, flash, redirect, render_template, 
  request, session, url_for)

from simulation import Simulation

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def simulate():
    thisId = str(uuid.uuid4())
    return render_template('simulate.html')

@app.route('/results', methods = ['POST'])
def results():
    start = time.time()
    link = request.form['espnLink']
    sim = Simulation(myBracketUrl = link)
    first = True
    sizes = [100, 1000, 10000, 25000]
    results = {}
    for i in sizes:
        predBracket = sim.runSimulation(poolSize = i, resetPreds = first)
        res = sim.scoreSimulation()
        if first:
            first = False        
        results[i] = dict(zip(['pred_arr', 'score', 'percentile', 'fanHist', 'neighbors','visualization'], [predBracket] + list(res)))
    vis_list = res[-1]
    return render_template('results.html', results = results, vis_list = vis_list)

# @app.route('/specific_results/<competitors>/<neighbors>')
# def specific_results(competitors, neighbors):
#     print(neighbors)
#     return f"You have {competitors} total competitors!"

app.run(host='0.0.0.0', debug=True)
