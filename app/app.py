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
        simRes = sim.runSimulation(poolSize = i, resetPreds = first)
        if first:
            first = False        
        results[i] = dict(zip(['pred_arr', 'score', 'percentile', 'fanHist'], simRes))
    print(time.time() - start)
    return render_template('results.html', results = results)

app.run(host='127.0.0.1', debug=True)
