import os
import csv
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any
from teams import Team, Teams, SpecificEntryImporter


"""
A. Classes to build files containing 
    matchup (Team vs Team) predictions in 
    Kaggle-acceptable *.csv format
"""
class PredictionTemplate():
    """
    "Abstract" template class
    -Template to be filled with prediction for each possible game in this
      iteration of NCAA tournament
    -Instantiate with specific set of predictions
        -Or if no set of predictions, will just create blank template wih team Ids
        -Like file you need for Kaggle submission
    """
    def __init__(self, year : int, teams : Teams):
        self.year : int = year
        self.teams : Teams = teams # Ideally something of Teams class from team.py
    
    @abstractmethod
    def getPrediction(self, tm1 : Team, tm2 : Team) -> str:
        """
        Determines how to get prediction for a specific matchup 
            (i.e., combination of two Teams)
        Returns:
            String representing the prediction for this matchup
        """
        pass

    def writeMatchups(self, file_name : str) -> None:
        """
        Writes matchups and predictions to .csv file
        """
        predIds : tuple[int, Team] = [(team.predId, team) for team in self.teams.teams]
        predIds.sort()

        matchups = []
        for i in range(len(predIds)):
            for j in range(i + 1, len(predIds)):
                id1, tm1 = predIds[i][0], predIds[i][1]
                id2, tm2 =  predIds[j][0], predIds[j][1]
                gameid = str(self.year) + '_' + id1 + '_' + id2
                prob = self.getPrediction(tm1, tm2)
                matchups.append((gameid, prob))
        
        with open(file_name + '.csv', 'w') as out:
            csv_out=csv.writer(out)
            csv_out.writerow(['Id','Pred'])
            for matchup in matchups:
                csv_out.writerow(matchup)
                
class blankTemplate(PredictionTemplate):
    def __init__(self, year, teams):
        super().__init__(year, teams)
        
    def getPrediction(self, tm1 : Team, tm2 : Team) -> str:
        return ""

class simpleSeedTemplate(PredictionTemplate):
    def __init__(self, year, teams):
        super().__init__(year, teams)
        
    def getPrediction(self, tm1 : Team, tm2 : Team) -> str:
        seed1, seed2 = tm1.seed, tm2.seed
        diff = seed2 - seed1
        prob = 0.0315 * diff + 0.5
        return prob 


"""
B. Classes to instantiate an actual Predictions object
    from Kaggle acceptable *.csv format (written out 
    by PredictionTemplate above)
"""
class PredictionsGenerator():
    """
    << Predictions Generator >>
    Generate Predictions object using .csv file generated
    from PredictionTemplate object
    """
    def __init__(self, fileName : str):
        self.file : str = fileName
        self._probabilities = None
        self._generateProbabilities()
        
    @abstractmethod
    def _generateProbabilities(self):
        pass

class KagglePredictionsGenerator(PredictionsGenerator):
    """
    Concrete subclass for <<PredictionsGenerator>>
    KNOW: Any Kaggle Input Data
    DO: Produce dictionary to be passed to be GamePredictions class
            {key              :   value}
        Ex. {(teamid, teamid) :   0.5}
    """
    def __init__(self, fileName):
        super().__init__(fileName)
        
    def _generateProbabilities(self) -> Dict[tuple[int, int], float]:
        if self._probabilities:
            return self._probabilities
        else:
            probDictionary = {}
            with open(self.file, 'r') as file:
                for num, row in enumerate(file):
                    if num > 0:
                        id1 = row[5:9]
                        id2 = row[10:14]
                        prob = row[15:]
                        probDictionary[(int(id1), int(id2))] = round(float(prob),5)
            self._probabilities = probDictionary

    @property
    def probabilities(self) -> Dict[tuple[int, int], float]:
        return self._probabilities
    
    @probabilities.setter
    def predictions(self, *args, **kwargs) -> None:
        print("Sorry, can't change probabilities!")
        return

class Predictions():
    """
    Class that encapsulates choosing a concrete set of predictions
    (Separated from KagglePredictionsGenerator in case predictions come in another form)
    """
    def __init__(self, predictionsGenerator : PredictionsGenerator):
        self.generator = predictionsGenerator
        self._predictions = self.generator.probabilities

    @property
    def predictions(self) -> Dict[tuple[int, int], float]:
        return self._predictions
    
    @predictions.setter
    def predictions(self, value : Any) -> None:
        print("Sorry, can't reset the predictions!")
        return

def main():
    """
    Only need to do this the one time to set up
    2022 predictions template
    -And simple model by seed
    """
    entryImporter = SpecificEntryImporter()
    teams = Teams(teamImporter = entryImporter)
    teams.setPredIds(file = '../data/MTeams.csv')
    
    tmp1 = blankTemplate(2022, teams)
    tmp1.writeMatchups('../data/kaggle_predictions/predTemplate2022_')

    tmp2 = simpleSeedTemplate(2022, teams)
    tmp2.writeMatchups('../data/kaggle_predictions/seedPreds2022_')


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    main()