#from Autotune import Parameter
from time import time, sleep
import csv

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
                    _, test_time, _ = self.runFunc(*arguments)
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

                print str(i) + ", Time:" + str(test_time) + " " + self.parameters.toStringCurrent()
                if i < self.parameters.getNumberOfStates()-1:
                    self.parameters.next()
            
            self.total_test_time = time() - start_time
            print "Total time:" + str(self.total_test_time) + " Best time:" + str(self.best_time) + " Best parameters:" + str(self.best_parameters)

    def getTable(self, description=False):
        list = []
        if description == True:
            description_string = ["Number of runs: " + str(self.parameters.getNumberOfStates()), "Total time:" + str(self.total_test_time)]
            list.append(description_string)
        header = ["Iteration", "Time", "Work_Group_Size"]
        header.extend(self.parameters.getRunParametersListOnlyNames())
        list.append(header)
        for i in range(len(self.saved_states)):
            list.append(self.saved_states[i])
        return list

    def saveCSV(self):
        table = self.getTable()
        with open('table.csv', 'wb') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerows(table)
