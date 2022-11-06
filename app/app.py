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
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import random

app = Flask(__name__)

def plotHistogram(fanHist : dict[int : int], score : int):
    ans = []
    for k, v in fanHist.items():
        ans += [k] * v

    fig = Figure()

    axis = fig.add_subplot(1, 1, 1)
    axis.hist(ans, bins = 20)
    axis.axvline(score, color='k', linestyle='dashed', linewidth=1)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer())
    return data

# def plotHistogram(fanHist : dict[int : int], score : int):
#     plt.hist(ans, bins = 20)
#     plt.axvline(score, color='k', linestyle='dashed', linewidth=1)
#     buf = BytesIO()
#     plt.savefig(buf, format="png")
#     # Embed the result in the html output.
#     data = base64.b64encode(buf.getbuffer()).decode("ascii")
#     # print(data)
#     return data

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
    sizes = [100, 500, 1000, 10000]
    results = {}
    for i in sizes:
        simRes = sim.runSimulation(poolSize = i, resetPreds = first)
        if first:
            first = False
        hist = plotHistogram(simRes[3], int(simRes[1]))
        
        results[i] = dict(zip(['pred_arr', 'score', 'percentile', 'fanHist'], ([i for i in simRes[:-1]] + [hist])))
        print(results)
    print(time.time() - start)
    return render_template('results.html', results = results)

app.run(host='127.0.0.1', debug=True)
