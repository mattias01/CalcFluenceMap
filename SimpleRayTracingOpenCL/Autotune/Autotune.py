#from Autotune import Parameter
from time import time, sleep
import csv
from scipy.stats.stats import pearsonr, spearmanr, kendalltau
from sklearn import mixture
import numpy as np

class Autotune(object):
    """Module to auto-tune parameters for OpenCL kernels"""
    def __init__(self, parameters, runFunc, runArguments, initFunc=None, deinitFunc=None):
        self.parameters = parameters
        self.runFunc = runFunc
        self.runArguments = runArguments
        self.initFunc = initFunc
        self.deinitFunc = deinitFunc
        self.best_time = float('inf')
        self.saved_states = []

    def findOptimizationParameters(self):
        if self.parameters.getNumberOfStates() > 0:
            print "Number of states to explore: " + str(self.parameters.getNumberOfStates())
            start_time = time()
            self.parameters.next() # Hack to get it to not test the first state twice.
            for i in range(self.parameters.getNumberOfStates()):
                arguments = list(self.runArguments)
                optParameters = self.parameters.getRunParametersList()
                arguments.append(optParameters)
                
                try:
                    _, _, test_time, _ = self.runFunc(*arguments)
                except:
                    test_time = float('inf')

                wg_size = self.parameters.getRunParametersTupleOnlyValues()[1] * self.parameters.getRunParametersTupleOnlyValues()[2] * self.parameters.getRunParametersTupleOnlyValues()[3]
                if test_time == float('inf'):
                    current_state = [i, -1, wg_size]
                else:
                    current_state = [i, test_time, wg_size]
                current_state.extend(self.parameters.getRunParametersTupleOnlyValues())
                self.saved_states.append(current_state)

                if test_time < self.best_time:
                    self.best_time = test_time
                    self.best_parameters = self.parameters.getRunParametersList()

                tab = '\t'
                if test_time == float('inf'): # Adjust tabulation so parameters are aligned in output.
                    tab += '\t'
                print str(i) + '\t' + "Time:" + str(test_time) + tab + " " + self.parameters.toStringCurrentValue()
                if i < self.parameters.getNumberOfStates()-1:
                    self.parameters.next()
            
            self.total_test_time = time() - start_time
            print "Total time:" + str(self.total_test_time) + " Best time:" + str(self.best_time) + " Best parameters:" + str(self.best_parameters)

    def getSavedStatesWithoutFailedRuns(self):
        list = []
        for i in range(len(self.saved_states)):
            if (self.saved_states[i][1] != -1):
                list.append(self.saved_states[i])
        return list

    def findWithinRangeOfBest(self, range):
        list = []
        state_list  = self.getSavedStatesWithoutFailedRuns()
        for x in state_list:
            if x[1] >= self.best_time * (1-range) and x[1] <= self.best_time * (1+range):
                list.append(x)
        return list

    def calcCorrelation(self, list, corr_func):
        stat_list = list
        corr_list = []
        for j in range(len(stat_list[0])):
            if j >= 2: # Skip header
                corr_list.append(corr_func([x[1] for x in stat_list], [x[j] for x in stat_list]))
        return corr_list

    def getStatistics(self, data):
        list = []
        #pearsoncorr_list = self.calcPearsonCorrelation(data)
        pearsoncorr_list = self.calcCorrelation(data, pearsonr)
        statistics_string = ["Pearson correlation:", ""]
        statistics_string.extend(pearsoncorr_list)
        list.append(statistics_string)
        #spearmancorr_list = self.calcSpearmanCorrelation(data)
        spearmancorr_list = self.calcCorrelation(data, spearmanr)
        statistics_string = ["Spearman correlation:", ""]
        statistics_string.extend(spearmancorr_list)
        list.append(statistics_string)
        kendallcorr_list = self.calcCorrelation(data, kendalltau)
        statistics_string = ["Kendalls tau correlation:", ""]
        statistics_string.extend(kendallcorr_list)
        list.append(statistics_string)
        return list

    def getTable(self, description=False, statistics=False, best_ten_percent=False, em=False):
        list = []
        header = ["Iteration", "Time", "Work_Group_Size"]
        header.extend(self.parameters.getRunParametersListOnlyNames())
        list.append(header)
        for i in range(len(self.saved_states)):
            list.append(self.saved_states[i])
        if description == True:
            description_string = ["Number of runs: " + str(self.parameters.getNumberOfStates()), "Total time:" + str(self.total_test_time)]
            list.append(description_string)
        if statistics == True:
            list.extend(self.getStatistics(self.getSavedStatesWithoutFailedRuns()))
        if best_ten_percent == True:
            list.append(["Best fifteen percent from best"])
            best = self.findWithinRangeOfBest(0.15)
            list.extend(best)
            list.extend(self.getStatistics(best))
        if em == True:
            gmm = mixture.DPGMM(n_components=10)
            y = gmm.fit([x[1:6] for x in self.getSavedStatesWithoutFailedRuns()])
            result = gmm.predict(np.array([x[1:6] for x in self.getSavedStatesWithoutFailedRuns()]))
            print result
        return list

    def saveCSV(self):
        table = self.getTable(description=True, statistics=True, best_ten_percent=True, em=True)
        with open('table.csv', 'wb') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerows(table)
