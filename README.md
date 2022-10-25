# NCAA-Tournament-Modeler-Project

**I. Project Description**

The purpose of this project is to help basketball fans "test" their brackets by (1) simulating the NCAA tournament and (2) comparing users' brackets against simulated competitors’ data. This should help fans determine what brackets might score well after accounting for:
1.	What models say the “true” probabilities are for all possible games in the tournament.
2.	What the general public has chosen, and 

Put another way, this is not so much an exercise in forecasting or estimation - even the most casual fan can get their hands on a set of reasonable projections fairly easily (see [FiveThirtyEight](https://projects.fivethirtyeight.com/2021-march-madness-predictions/)). Instead, this is more of an exercise in arbitrage. If we trust some expert-generated model as our source of truth, can we still identify any discrepancies with the general public's picks and take advantage?

**II. Overview of Repositories**

0. */app* and */AWS_setup*

- Help stand up rudimentary web app hosted on AWS EC2 instance. Still in progress at the moment...

1. */source/data*
- Contains raw Kaggle data used for predictions and bracket set-up, as well as intermediary datasets

2. */source/data_structures*
- Contains core, custom data structures that carry out project. Abstract BracketEntry and Bracket classes in module bracket.py are templates underlying project.

3. */source/simulation_models*
- Contains specific instantiations of abstract Bracket class defined above
	- 1. **userBracket** creates a scorable, Bracket structure based on bracket entry (filled out from ESPN competition)
	- 2. **fansBracket** uses ESPN's Who Picked Whom to create realistic simulations of competing entries in an ESPN bracket pool competition
	- 3. **predictionBracket** uses game-by-game predictions generated from ML model to simulate realistic outcomes of the NCAA tournament
- **simulation.py** is final program called by Flask that allows user to test their bracket entry against *n* simulated competitor entries and a realistic outcome supplied by ML model.

4. */source/prediction_models*
- Contains actual ML task of choosing classification model to predict winners of each NCAA tournament game
