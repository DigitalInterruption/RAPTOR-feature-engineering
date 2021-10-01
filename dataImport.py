"""
    Module to manage data imports from 'data' directory:
        - file structure of the dataset is important, directories containing
            families should be used with a csv file named <family>.csv within
            the directory to index the hashes for that family
        - these family directories should be contained in a directory with the
            dataset name
        - example: <name>/<family>/<sampleHash>.csv
"""
import os
import csv
import pandas as pd
from collections import Counter

class dataImport():
    # Initialise dataImport class with the target dataset, read families from
    #   directory titles and calculate a value for the total number of classes
    def __init__(self):
        # Data directory variable, empty = current dir
        self.dataDir = 'data/'
        self.dataPath = self.dataDir
        self.families = os.listdir(self.dataPath)
        self.classes = len(self.families)

    # Function to get key files for each family.
    #   Returns 'keys', a list of key dataframes
    def getKeys(self):
        # Initialise list for keys
        keys = []
        # Iterate through each family and add key dataframe to keys list
        for family in self.families:
            path = self.dataPath + family + '/' + family + '.csv'
            key = pd.read_csv(path)
            keys.append(key)
        # Return list of key dataframes
        return keys

    # Function to read each sample into a list for each family.
    #   Returns 'keys', a list of key dataframes
    #   Returns 'samples', a nested list of each sample for each family
    #       use families variable to reference the order of the list
    def getData(self):
        # Initialise list for family of samples
        familySamples = []
        # Get key dataframes using getKeys function
        keys = self.getKeys()
        # Iterate through each family
        for i, family in enumerate(self.families):
            # Initialise list to be nested in familySamples
            samples = []
            # Get the file hashes from the key dataframe
            key = keys[i]
            idents = [i for i in key[family].values]
            # Iterate through each file listed in the key dataframe
            for ident in idents:
                sample = []
                # Open the csv file for the sample and read to list
                with open(self.dataPath + family + '/' + ident + '.csv',
                        'r') as file:
                    reader = csv.reader(file, delimiter='\n')
                    # TODO - messy way to get list of strings not list of lists
                    #   consider reformatting csv's to be one, comma separated,
                    #   line
                    [sample.append(line[0]) for line in reader]
                samples.append(sample)
            familySamples.append(samples)
        # Return key dataframes for reference and nested sample lists
        return keys, familySamples

