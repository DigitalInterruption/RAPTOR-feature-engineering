from dataImport import dataImport

import link_analysis.graph as gr
import feature_construction.features as fe

di = dataImport()

# Import samples
_, familySamples = di.getData()

# Generate graphs from samples
graphs = gr.genFamilyGraphs(familySamples)
del familySamples

# Create union graphs for each family
unionGraphs, nxUnionGraphs = fe.genUnionGraphs(graphs)
del graphs

# Create list of dataframes to store features
results = fe.createFeatureFrames(unionGraphs)

# Calculate features and store results
results = fe.calculateFeatures(unionGraphs, nxUnionGraphs, results)
del unionGraphs, nxUnionGraphs

# Collect features into single dataframe and label them by family and node
output = fe.collectResults(results, di.families)

# Write results to file
output.to_csv('features/' + 'results' + '.csv', index=False)
