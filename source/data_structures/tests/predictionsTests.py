import sys
sys.path.append('../')

import unittest
from predictions import *
from teams import *

class CheckPredictionsGenerator(unittest.TestCase):
    def setUp(self):
        kaggle_file_2021 = '../../data/kaggle_predictions/testPredictions2021.csv'
        kaggle_file_2022 = '../../data/kaggle_predictions/seedPreds2022.csv'
        self.kagglePredGenerator21 = KagglePredictionsGenerator(kaggle_file_2021)
        self.kagglePredGenerator22 = KagglePredictionsGenerator(kaggle_file_2022)
        self.probs1 = self.kagglePredGenerator21.probabilities
        self.probs2 = self.kagglePredGenerator22.probabilities
    
    def test_probLengths(self):
        self.assertGreaterEqual(len(self.probs1), 60 * 60 / 2)
        self.assertGreaterEqual(len(self.probs2), 60 * 60 / 2)
        self.assertLessEqual(len(self.probs1), 70 * 70 / 2)
        self.assertLessEqual(len(self.probs2), 70 * 70 / 2)
    
    def test_probIds(self):
        idSet1 = set()
        for prob in self.probs1:
            self.assertLess(prob[0], prob[1])
            idSet1.add(prob)
        self.assertEqual(len(idSet1), len(self.probs1))

        idSet2 = set()
        for prob in self.probs2:
            self.assertLess(prob[0], prob[1])
            idSet2.add(prob)
        self.assertEqual(len(idSet2), len(self.probs2))

class CheckBlankTemplate(unittest.TestCase):
    def setUp(self):
        """
        Need proper set of teams to initiate templates
        So do check of teams
        """
        pass


def run_some_tests():
    # Run only the tests in the specified classes
    test_classes_to_run = [
                            CheckPredictionsGenerator
                            ]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)
        
    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

if __name__ == '__main__':
    run_some_tests()