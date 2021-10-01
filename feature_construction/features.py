'''
    Calculate features (centrality measures) from graph
'''
import numpy as np
import pandas as pd
import networkx as nx

# Supress stdout if iGraph union function
from contextlib import contextmanager,redirect_stderr,redirect_stdout
from os import devnull

@contextmanager
def suppress_stdout_stderr():
    with open(devnull, 'w') as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield (err, out)

# Take vertex/edge weights and process them so None is 0 for calculations
def cleanWeights(weights):
    weights = np.array(weights)
    weights[weights == None] = 0
    return weights.astype(int)

# Take iGraph graph and convert into NetworkX graph, preserving weights
def igraphToNetworkx(g):
    # Extract information from the iGraph object
    nodes = g.vs.indices
    nodeWeights = g.vs['weights']
    nodeNames = g.vs['name']
    edges = g.get_edgelist()
    edgeWeights = g.es['weights']
    # Create input data for NetworkX graph
    for n in nodes: nodes[n] = (n, {'name':nodeNames[n],'weights':nodeWeights[n]})
    for e in g.es.indices:
        edges[e] = (edges[e][0], edges[e][1], {'weights' : edgeWeights[e]})
    # Create NetworkX graph to match the input graph
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G

# Create union graph for each family, calculating cumulative vertex/edge weights
def genUnionGraphs(graphs):
    unionGraphs = []
    nxUnionGraphs = []
    # Iterate through each family
    for f in graphs:
        # Supress unionisation stdout to clean up output
        with suppress_stdout_stderr():
            uniG = f[0].union(f[1:len(f)])
        # Create numpy array to store cuulative wrights
        totalNodeWeights = np.zeros((len(uniG.vs['weights_1'])))
        totalEdgeWeights = np.zeros((len(uniG.es['weights_1'])))
        # Iterate through each sample to add weights to array
        for i in range(len(f)):
            name = 'weights_' + str(1 + i)
            totalNodeWeights += cleanWeights(uniG.vs[name])
            totalEdgeWeights += cleanWeights(uniG.es[name])
        # Apply cumulative weights to unionised graph
        uniG.vs['weights'] = totalNodeWeights
        uniG.es['weights'] = totalEdgeWeights
        # Add unionised graph to list
        unionGraphs.append(uniG)
        # Generate NetworkX graph and add to list
        nxUniG = igraphToNetworkx(uniG)
        nxUnionGraphs.append(nxUniG)
    return unionGraphs, nxUnionGraphs

# Create list of dataframes to collect the calculated features
def createFeatureFrames(graphs):
    # Declare field names for storage of the generated features
    fields = ['node-weight', 'in-degree', 'out-degree', 'degree', 'closeness-wtd',\
         'in-closeness-wtd', 'out-closeness-wtd', 'closeness-unwtd',\
              'in-closeness-unwtd', 'out-closeness-unwtd', 'betweenness-wtd',\
                  'betweenness-unwtd','first-order-influence-wtd',\
                      'first-order-influence-unwtd',\
                          'clustering-coefficient']
    # Generate bogus data to fill the feature dataframe initially
    bogus = [None]*len(fields)
    # Recursively create list of dataframes for each family
    results = [pd.DataFrame([bogus]*len(f.vs['name']), f.vs['name'], fields)\
         for f in graphs]
    return results

# Take graph and calculate clustering coefficient (transitivity) for each node
def getNodeTransitivity(G):
    # Get list of nodes/vertexes
    nodes = list(G.nodes)
    # Create numpy array to store results
    trans = np.zeros(len(nodes))
    # Iterate through each node
    for i, n in enumerate(nodes):
        # Get the neighbourhood for the node (successor nodes)
        N = G.neighbors(n)
        # Create subgraph for the neighbourhood
        nG = G.subgraph(N)
        # Calculate transitivity for subgraph and store result
        trans[i] = nx.algorithms.cluster.transitivity(nG)
    return trans

# Calculate centrality measurements for each node in each graph
def calculateFeatures(graphs, nxGraphs, results):
    # Record calculated features for each graph.
    #   - Both Weighted and Unweighted (BWaU)
    norm = False     # Normalisation flag
    for i, G in enumerate(graphs):
        # Record cumulative node weights
        results[i]['node-weight'] = G.vs['weights']
        # Record in, out and all degree measures
        results[i]['in-degree'] = G.indegree() 
        results[i]['out-degree'] = G.outdegree()
        results[i]['degree'] = G.degree()
        # Record in, out and all closeness measures. BWaU
        results[i]['closeness-wtd'] = G.closeness(mode='ALL',
                weights='weights', normalized=norm)
        results[i]['in-closeness-wtd'] = G.closeness(mode='IN',
                weights='weights', normalized=norm)
        results[i]['out-closeness-wtd'] = G.closeness(mode='OUT',
                weights='weights', normalized=norm)
        results[i]['closeness-unwtd'] = G.closeness(mode='ALL',
                normalized=norm)
        results[i]['in-closeness-unwtd'] = G.closeness(mode='IN',
                normalized=norm)
        results[i]['out-closeness-unwtd'] = G.closeness(mode='OUT',
                normalized=norm)
        # Record the weighted and unweighted betweenness meadures
        results[i]['betweenness-wtd'] = G.betweenness(weights='weights')
        results[i]['betweenness-unwtd'] = G.betweenness()
        # Record the 1st order influence measures. BWaU
        # TODO: look into error: RuntimeWarning: Weighted directed graph in
        #       eigenvector centrality at:
        #       ../../../source/igraph/src/centrality.c:352
        results[i]['first-order-influence-wtd'] = G.eigenvector_centrality(
                weights='weights', scale=norm)
        results[i]['first-order-influence-unwtd'] = G.eigenvector_centrality(
                scale=norm)
        # Record clustering coefficient measure
        results[i]['clustering-coefficient'] = getNodeTransitivity(nxGraphs[i])
    return results

# Collect results into a single dataframe and label
def collectResults(results, families):
    output = pd.DataFrame(columns=results[0].columns)
    for i, f in enumerate(families):
        results[i].insert(0, 'node', results[i].index)
        results[i].insert(0, 'family', f)
        output = output.append(results[i], ignore_index=True)
    return output

if __name__ == "__main__":
    from graphImport import *

    # Flags and definitions
    testOutput = True
    testTarget = 'clustering-coefficient'
    printDf = False
    save = True
    distances = False
    plot = False
    
    # Create family union graphs
    unionGraphs, nxUnionGraphs = genUnionGraphs(graphs)
    
    # Create dataframes to store results
    results = createFeatureFrames(unionGraphs)

    # Calculate features and populate results tables
    results = calculateFeatures(unionGraphs, nxUnionGraphs, results)

    if testOutput: print([r[testTarget] for r in results])
    if printDf: print(collectResults(results, families).head)
    # Write calculated features to file
    if save:
        outputDf = collectResults(results, families)
        path = 'features/' + 'unionAllDevel.csv'
        outputDf.to_csv(path, index=False)

    # Write distance matrices to file
    if distances:
        for i, f in enumerate(families):
            apt = unionGraphs[i]
            names = apt.vs['name']
            distances = apt.shortest_paths(mode='IN')
            df = pd.DataFrame.from_records(distances, columns = names)
            df['name'] = names
            df.set_index("name", inplace = True)
            df.to_csv('distances/distances_' + f + '.csv')

    # Plotting of each graph iteratively changing vertex and edge sizes by weight
    # TODO: exponents are a silly way to scale these, investigate alternative
    if plot:
        from math import exp
        fileFormat = '.png'
        # Create style dictionary and set base layout
        style = {}
        style['arrow_size'] = 5
        style['arrow_width'] = 3
        for i, g in enumerate(unionGraphs):
            print(g)
            style['vertex_size'] = [weight*exp(-8)+25 for weight in g.vs['weights']]
            style['edge_size'] = [weight*2+5 for weight in g.es['weights']]
            try: ig.plot(g, 'test' + str(i) + fileFormat, **style)
            except: print('graph '+str(i)+' failed to plot')

