# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# app = Flask(__name__)

import sys 
import uuid
# print(sys.path)
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
    link = request.form['espnLink']
    simRes = Simulation(myBracketUrl = link)
    simRes.runSimulation()
    return render_template('results.html', simRes =simRes)