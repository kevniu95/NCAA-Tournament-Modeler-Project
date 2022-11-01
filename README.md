# NCAA-Tournament-Modeler-Project

**I. Project Description**

The purpose of this project is to help basketball fans (1) score their brackets against realistic outcomes of the NCAA tournament and (2) assess how their scores would place against a realistic pool of simulated competitors. This should help fans determine if their bracket entries might score well after accounting for:
1. The “true” best-guess probabilities for all possible games in the tournament 
	- (As determined by a model that might score well in the March Madness Kaggle [competition](https://www.kaggle.com/competitions/mens-march-mania-2022/data/) for instance)
2. How the general public has filled out their brackets
	- [ESPN Who Picked Whom](https://fantasy.espn.com/tournament-challenge-bracket/2022/en/whopickedwhom)

Put another way, this is not just a standard machine learning exercise. Winning your bracket pool requires more than just developing and extending a good classification model because there is a significant game theoretic component as well. 

Gonzaga may objectively be the most likely team to win the tournament. But if *everyone else* picks them, your odds of winning the pool may be better if you select another winner. By ranking your bracket entry against a realistic field of competitors, this project takes the first step in translating a good game-by-game machine learning model into a real tool you can use to win your bracket pool.

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
