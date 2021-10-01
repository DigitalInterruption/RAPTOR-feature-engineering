import csv
import os

from dataImport import dataImport
import link_analysis.graph as gr
import feature_construction.features as fe

# Import dataset
di = dataImport()
keys, familySamples = di.getData()

# Iterate through families and samples
for i, family in enumerate(di.families):
    key = keys[i][family]
    os.mkdir('features/' + family)
    
    for j, sample in enumerate(familySamples[i]):
        # Generate graph from sample
        graph = gr.genGraph(sample)

        # Create NetworkX graph for sample
        nxGraph = fe.igraphToNetworkx(graph)

        # Create list of dataframes to store features (wrap in list)
        results = fe.createFeatureFrames([graph])

        # Calculate features and store results
        results = fe.calculateFeatures([graph], [nxGraph], results)

        # Collect features into single dataframe and label them by family
        #   and node
        output  = fe.collectResults(results, [family])

        # Write results to file
        name = key[j]
        output.to_csv('features/' + family + '/' + name +
                '.csv', index=False)
