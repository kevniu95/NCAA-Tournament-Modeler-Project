import csv
from abc import ABC, abstractmethod


"""
A. Classes to build predictions
"""
class predictionTemplate():
    """
    "Abstract" template class
    -Template to be filled with prediction for eac possible game in this
      iteration of NCAA tournament
    -Instantiate with specific set of predictions
        -Or if no set of predictions, will just create blank template wih team Ids
        -Like file you need for Kaggle submission
    """
    def __init__(self, year, teams):
        self.year = year
        self.teams = teams # Ideally something of Teams class from team.py
    
    @abstractmethod
    def writeMatchups(self, file_name):
        pass
                
class blankTemplate(predictionTemplate):
    def __init__(self, year, teams):
        super().__init__(year, teams)
        self.fx = lambda x : ""
        self.inputs = ""
    
    def writeMatchups(self, file_name):
        predIds = [(team.predId, team.seed) for team in self.teams.teams]
        predIds.sort()

        matchups = []
        for i in range(len(predIds)):
            for j in range(i + 1, len(predIds)):
                gameid = str(self.year) + '_' + predIds[i][0] + '_' + predIds[j][0]
                prob = ""
                tup = gameid, prob
                matchups.append(tup)
        
        with open(file_name + '.csv', 'w') as out:
            csv_out=csv.writer(out)
            csv_out.writerow(['Id','Pred'])
            for matchup in matchups:
                csv_out.writerow(matchup)


class simpleSeedTemplate(predictionTemplate):
    def __init__(self, year, teams):
        super().__init__(year, teams)
        self.fx = self.simpleSeedModel
    
    def writeMatchups(self, file_name):
        predIds = [(team.predId, team.seed) for team in self.teams.teams]
        predIds.sort()

        matchups = []
        for i in range(len(predIds)):
            for j in range(i + 1, len(predIds)):
                gameid = str(self.year) + '_' + predIds[i][0] + '_' + predIds[j][0]
                prob = self.simpleSeedModel(int(predIds[i][1]), int(predIds[j][1]))
                tup = gameid, prob
                matchups.append(tup)
        
        with open(file_name + '.csv', 'w') as out:
            csv_out=csv.writer(out)
            csv_out.writerow(['Id','Pred'])
            for matchup in matchups:
                csv_out.writerow(matchup)
    
    def simpleSeedModel(self, seed1, seed2):
        diff = seed2 - seed1
        prob = 0.0315 * diff + 0.5
        return prob 



"""
B. Classes to use predictions
"""
class PredictionsGenerator():
    """
    << Predictions Generator >>
    """
    def __init__(self, fileName):
        self.file = fileName
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
        
    def _generateProbabilities(self):
        if self._probabilities is not None:
            return self._probabilities
        else:
            probDictionary = {}
            with open(self.file, 'r') as file:
                for num, row in enumerate(file):
                    if num > 0:
                        team1 = row[5:9]
                        team2 = row[10:14]
                        prob = row[15:]
                        probDictionary[(team1, team2)] = float(prob)
            self._probabilities = probDictionary

    @property
    def probabilities(self):
        return self._probabilities
    
    @probabilities.setter
    def predictions(self, *args, **kwargs):
        print("Sorry, can't change probabilities!")
        return

class Predictions():
    """
    Class that encapsulates choosing a concrete set of predictions
    (Separated from KagglePredictionsGenerator in case predictions come in another form)
    """
    def __init__(self, generator):
        self.generator = generator
        self._predictions = self.generator.probabilities

    @property
    def predictions(self):
        return self._predictions
    
    @predictions.setter
    def predictions(self, value):
        print("Sorry, can't reset the predictions!")
        return

def main():
    """
    Only need to do this the one time to set up
    2022 predictions template
    -And simple model by seed
    """
    # temp1 = blankTemplate(2022, teams)
    # temp1.writeMatchups('predTemplate2022')

    # temp2 = simpleSeedTemplate(2022, teams)
    # temp2.writeMatchups('seedPreds2022')


if __name__ == '__main__':
    main()