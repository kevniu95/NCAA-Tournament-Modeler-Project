# NCAA-Tournament-Modeler-Project

**I. Project Description**

The purpose of this project is to help basketball fans ‘test’ their brackets by simulating the NCAA tournament (using pre-determined prediction inputs) and comparing users' brackets against simulated competitors’ data. This should help fans determine what brackets might score well after accounting for:
1.	What the general public has chosen, and 
2.	What models think the “true” probabilities are for all possible games in the tournament.

Put another way, this is not so much an exercise in forecasting or estimation, but an exercise in arbitrage. If we trust some expert-generated model as our source of truth, perhaps we can compare that to the selections of the general public and take advantage of any discrepancies.


**II. Modules Description**
1. Crowd Simulator – This takes as input, ESPN’s [Who Picked Whom](https://fantasy.espn.com/tournament-challenge-bracket/2022/en/whopickedwhom) numbers that list how many people pick each team to move to the next round. The idea is to work backwards from this aggregated view to realistic simulations of individual entries. This provides the user a reasonable pool to compare their own bracket against.
	- KNOW: Percentage of teams picked to move to next round by ESPN fans
	- DO: Simulation of a single ESPN bracket entry

2. “True” Model – After simulating a competitor pool, we still need to be able to score a user's bracket entry against these competitors. To do this, we take a set of predictions to be our source of truth. This "source of truth model" will have, for each possible game in the tournament, have probability associated with team A beating team B.
	- KNOW: 63 x 64 “true” game probabilities (i.e. predictions)
	- DO: Simulation of NCAA tournament 
	- Existing Python Modules:
		-trueModel.py
		-trueModelTest.py

3. My Bracket – This will make it easy to upload a user's own bracket entry from, say, ESPN
	- KNOW: Some web page or other input with bracket input
	- DO: Produce a data structure representing the user’s NCAA tournament bracket selection
	- Existing Python Modules:
	 	-bracketImporter.py

4. Bracket Scorer- this will score filled-out bracket predictions (be they simulated or input by the user) and score them against the “True” model simulations that will be run
	-KNOW: Underlying “true” model, some filled-out bracket
	-DO: Score the filled-out bracket against the occurrence represented by a simulated instance of the “true” model
  
 5. Driver - Given a user's bracket entry, generates pool of competing crowd entries. Also simulates the "true" results many times so user has a sense of how their bracket fares against the crowd
