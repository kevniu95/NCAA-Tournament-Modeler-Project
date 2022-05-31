import csv
from abc import ABC, abstractmethod

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

def main():
    pass

if __name__ == '__main__':
    main()