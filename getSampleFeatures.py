import csv

import link_analysis.graph as gr
import feature_construction.features as fe

# Specify the sample to be processed
# TODO - pass this using commandline arguments
dataDir = 'data/devel/'
family = 'Simda'
name = '1IpWLz6eyhVxDAfQMKEd'

# Generate file path
sPath = dataDir + family + '/' + name + '.csv'

# Read opcode sequence into list
sample = []
with open(sPath, 'r') as file:
    reader = csv.reader(file, delimiter='\n')
    [sample.append(line[0]) for line in reader]

# Generate graph from sample
graph = gr.genGraph(sample)

# Create NetworkX graph for sample
nxGraph = fe.igraphToNetworkx(graph)

# Create list of dataframes to store features (wrap in list)
results = fe.createFeatureFrames([graph])

# Calculate features and store results
results = fe.calculateFeatures([graph], [nxGraph], results)

# Collect features into single dataframe and label them by family and node
output  = fe.collectResults(results, [family])

# Write results to file
output.to_csv('features/' + name + '.csv', index=False)
