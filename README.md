# NCAA-Tournament-Modeler-Project

**I. Project Description**

The purpose of this project is to help basketball fans ‘test’ their brackets by simulating the NCAA tournament (using pre-determined prediction inputs) and comparing their results against simulated competitors’ data. This should help fans determine what brackets might score well after accounting for:
1.	What the general public has chosen, and 
2.	What models think the “true” probabilities are for all possible games in the tournament.

Put another way, this is not so much an exercise in forecasting or estimation, but an exercise in arbitrage. If we trust some expert-generated model as our source of truth, perhaps we can compare that to the typical selections of the general public and take advantage of any discrepancies.


**II. Modules Description**
1. “True” Model – for each possible game in the tournament, have a probability associated with team A beating team B. This is the “true” model that is used to simulate the tournament and will be based off of some widely-accepted input like FiveThirtyEight’s projections, or perhaps by a model I create myself
	- KNOW: 63 x 64 “true” game probabilities (i.e. predictions)
	- DO: Simulation of NCAA tournament 
  - Existing Python Modules:
	  -trueModel.py
		-trueModelTest.py

2. Crowd Simulator – this takes as input, ESPN’s Who Picked Whom numbers that list how many people pick each team to move to the next round. The idea here is to back out an underlying model/distribution that represents how the “people” are picking their brackets. Once the distribution has been determined, this can simulate people’s brackets
	- KNOW: Percentage of teams picked to move to next round by ESPN
	- DO: Simulation of a random ESPN bracket entry

3. My Bracket – this will make it easy to upload your own bracket of decisions from, say, ESPN
	- KNOW: Some web page or other input with bracket input
  - DO: Produce a data structure representing the user’s NCAA tournament bracket selection
  - Existing Python Modules:
  	-bracketImporter.py

4. Bracket Scorer- this will score filled-out bracket predictions (be they simulated or input by the user) and score them against the “True” model simulations that will be run
	-KNOW: Underlying “true” model, some filled-out bracket
  -DO: Score the filled-out bracket against the occurrence represented by a simulated instance of the “true” model
