'''
    Generate graph from opcode sequence
'''
import igraph as ig
from collections import Counter

# Create tuple list of edges from the provided sample
def getEdges(sample):
    # Get copy of sample
    sampleRoll = sample[:]
    # Roll the sample by 1 to the left
    sampleRoll.append(sampleRoll.pop(0))
    # Zip the lists into list of tuples as edges and remove the last element
    edges = list(zip(sample, sampleRoll))
    edges.pop()
    return edges

# Function to sample entire family to get list of all contained opcodes
# TODO - consider replacing this with a complete opcode catalogue
def enumerateSample(sample):
    # Create counter object
    counter = Counter(sample)
    # Extract useful information from the counter
    opcodeList = []
    countList = []
    indexes = []
    idx = 0
    for opcode in counter.keys():
        opcodeList.append(opcode)
        countList.append(counter[opcode])
        indexes.append(idx)
        idx += 1
    # Return a dict of opcodes and their id number, along with their counts
    return dict(zip(opcodeList, indexes)), countList

# Function to create graph from opcode sequence sample
def genGraph(sample):
    # Create tuple list of edges from the sample
    edges = getEdges(sample)
    # Get key to index the vertices of the graph
    opcodes, counts = enumerateSample(sample)
    g = ig.Graph(n=len(opcodes.keys()), directed = True, 
            vertex_attrs={'name':list(opcodes.keys())})
    # Add edges to graph (attributions could be done here)
    g.add_edges(edges)
    # Create weights and apply labels to graph before simplifying
    g.vs['weights'] = counts
    g.es["weights"] = [1] * g.ecount()
    g.vs['label'] = g.vs['name']
    g.simplify(combine_edges='sum')
    return g


# Create graphs for each sample, in each family, return a list of lists of
#   graphs
def genFamilyGraphs(familySamples):
    # Iterate through each family and corresponding samples
    graphs = []
    for samples in familySamples:
        # Record sample graphs into family groups
        familyGraphs = []
        for sample in samples:
            g = genGraph(sample)
            familyGraphs.append(g)
        graphs.append(familyGraphs)
    return graphs


if __name__ == '__main__':
    import data.dataImport
    
    di = data.dataImport.dataImport('devel')

    # Plotting flag
    plot = False

    # Save flag and graph storage directory
    save = True
    graphDir = 'graphs'

    # Subsample flag for debugging
    subsample = False

    # Get data using import module
    keys, familySamples = di.getData()

    # Reduce dataset for testing
    if subsample:
        #del familySamples[1:len(familySamples)]
        for familySample in familySamples:
            del familySample[10:len(familySample)]

    # Generate graphs for dataset
    graphs = genFamilyGraphs(familySamples)

    # If save flag is set, write the graph objects to file by pickling along
    #   with the family key file
    if save:
        for i, familyGraphs in enumerate(graphs):
            for name in keys[i]: familyName = name
            idents = keys[i].values.astype(str)
            keys[i].to_csv(graphDir + '/' + familyName + '/' + familyName +\
                    '.csv', index=False)
            for graph, ident in zip(familyGraphs, idents):
                sampleName = ''.join(ident.tolist())
                graph.write_pickle(fname=graphDir + '/' + familyName + '/' +\
                        sampleName + '.net')

    # Plotting of each graph, changing vertex and edge sizes by weight
    if plot:
        # Create style dictionary and set base layout
        style = {}
        style['arrow_size'] = 5
        style['arrow_width'] = 3
        fileFormat = '.png'
        for i, g in enumerate(familyGraphs):
            style['vertex_size'] = [weight*exp(-3)+25 for weight in 
                    g.vs['weight']]
            style['edge_size'] = [weight*3+5 for weight in g.es['weight']]
            try: ig.plot(g, 'test' + str(i) + fileFormat, **style)
            except: print('graph '+str(i)+' failed to plot')

