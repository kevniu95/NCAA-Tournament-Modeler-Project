import pandas as pd
from abc import ABC, abstractmethod
import numpy as np

from sklearn.preprocessing import OneHotEncoder

class PredictionModel():
    def __init__(self):
        pass
    
    @abstractmethod
    def import_data(self):
        pass

class RaddarModel(PredictionModel):
    def __init__(self):
        self._import_data()

    def _import_data(self):
        self.reg_results = pd.read_csv("../data/kaggle_data/MRegularSeasonDetailedResults.csv")
        self.results = pd.read_csv("../data/kaggle_data/MNCAATourneyDetailedResults.csv")
        self.seeds = pd.read_csv("../data/kaggle_data/MNCAATourneySeeds.csv")

    def _prep_reg_tourney(self):
        r1 = self.reg_results.loc[:, ["Season", "DayNum", "WTeamID", "WScore", "LTeamID", "LScore", "NumOT", "WFGA", "WAst", "WBlk", "LFGA", "LAst", "LBlk"]]
        r2 = self.reg_results.loc[: , ["Season", "DayNum", "LTeamID", "LScore", "WTeamID", "WScore", "NumOT", "LFGA", "LAst", "LBlk", "WFGA", "WAst", "WBlk"]]
        r1.columns = ["Season", "DayNum", "T1", "T1_Points", "T2", "T2_Points", "NumOT", "T1_fga", "T1_ast", "T1_blk", "T2_fga", "T2_ast", "T2_blk"]
        r2.columns = ["Season", "DayNum", "T1", "T1_Points", "T2", "T2_Points", "NumOT", "T1_fga", "T1_ast", "T1_blk", "T2_fga", "T2_ast", "T2_blk"]
        regular_season = pd.concat([r1, r2], axis = 0)
        assert len(r1) == len(r1.drop_duplicates())
        assert len(r2) == len(r2.drop_duplicates())
        assert len(regular_season) == len(regular_season.drop_duplicates())
        
        t1 = self.results.loc[: , ["Season", "DayNum", "WTeamID", "LTeamID", "WScore", "LScore"]]
        t2 = self.results.loc[: , ["Season", "DayNum", "LTeamID", "WTeamID", "LScore", "WScore"]]
        t1.columns = ["Season", "DayNum", "T1", "T2", "T1_Points", "T2_Points"]
        t2.columns = ["Season", "DayNum", "T1", "T2", "T1_Points", "T2_Points"]
        tourney = pd.concat([t1, t2], axis = 0)
        tourney["ResultDiff"] = tourney['T1_Points'] - tourney['T2_Points']

        assert len(t1) == len(t1.drop_duplicates())
        assert len(t2) == len(t2.drop_duplicates())
        assert len(tourney) == len(tourney.drop_duplicates())
        return regular_season, tourney

    def _get_random_effects(self, reg):
        self.seeds.columns = ['Season', 'Seed', 'Team']
        X = reg.merge(self.seeds[['Season','Team']], left_on = ['Season','T1'], right_on = ['Season', 'Team'], how = 'inner')
        X = X.merge(self.seeds[['Season','Team']], left_on = ['Season', 'T2'], right_on = ['Season', 'Team'], how = 'inner')
        X['Const'] = 1
        X['Win'] = (X['T1_Points'] > X['T2_Points']).astype(int)
        X = X[['Const', 'Season', 'T1', 'T2', 'T1_Points', 'T2_Points', 'NumOT', 'Win']]
        
        test = X[X['Season'] == 2003]
        catEncoder1 = OneHotEncoder()
        catEncoder2 = OneHotEncoder()

        test1 = catEncoder1.fit_transform(test[['T1']]).toarray()
        test2 = catEncoder2.fit_transform(test[['T2']]).toarray()
        test = test.join(pd.DataFrame(test1 - test2))
        
    def prep_x(self):
        reg, tourney = self._prep_reg_tourney()
        self._get_random_effects(reg)


    def prep_y(self):
        pass


def main():
    a = RaddarModel()
    a.prep_x()

if __name__  == '__main__':
    main()