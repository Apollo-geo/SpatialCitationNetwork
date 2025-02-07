from pymongo import MongoClient
import networkit as nk
import pandas as pd
import numpy as np

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['LiteratureNetwork']
papers_collection = db['Papers']
references_collection = db['References']

# Initialize the Networkit graph
G = nk.Graph(directed=True)

# Mapping between node ID and article title
node_id_map = {}

# Dictionary storing node attributes
node_attributes = {}

# Create a collection to keep track of the node titles that have been added
existing_titles = set()

#Add nodes (from Papers collection)
for paper in papers_collection.find():
    title = str(paper.get('Title', 'UnknownPaperTitle'))
    authors = paper.get('Authors', 'UnknownAuthors')

    if title not in node_id_map and title not in existing_titles:
        node_id = G.addNode()
        node_id_map[title] = node_id
        node_attributes[node_id] = {'title': title, 'authors': authors}
        existing_titles.add(title)

# Add nodes (from the References collection)
for reference in references_collection.find():
    for ref in reference['References']:
        title = ref.get('Title', 'UnknownReference') if len(ref.get('Title', 'UnknownReference')) > len(ref.get('Details', 'UnknownReference')) else ref.get('Details', 'UnknownReference')
        authors = ref.get('Authors', '')

        if title and title not in node_id_map and title not in existing_titles:
            node_id = G.addNode()
            node_id_map[title] = node_id
            node_attributes[node_id] = {'title': title, 'authors': authors}
            existing_titles.add(title)

# Add edges
for reference in references_collection.find():
    source_title_dict = reference.get('PaperTitle', {})
    source_title = source_title_dict if isinstance(source_title_dict, str) else source_title_dict.get('')
    source_node_id = node_id_map.get(source_title, None)

    if source_node_id is not None:
        for ref in reference.get('References', []):
            target_title = ref.get('Title', 'Unknown') if len(ref.get('Title', 'Unknown')) > len(
                ref.get('Details', 'Unknown')) else ref.get('Details', 'Unknown')

            # Check if the reference relationship exists
            if target_title in node_id_map:
                target_node_id = node_id_map[target_title]
                G.addEdge(source_node_id, target_node_id)

# Now, you can use Networkit's various algorithms to analyze graph G
# Calculate Gamma Index
def calculate_gamma_index(G):
    num_nodes = G.numberOfNodes()
    num_edges = G.numberOfEdges()
    
    if num_nodes <= 1:
        return 0  # If there are not enough nodes, do not calculate the Gamma index
    
    # Maximum possible number of edges (for directed graphs)
    max_edges = num_nodes * (num_nodes - 1)
    
    gamma_index = num_edges / max_edges
    return gamma_index
gamma_index = calculate_gamma_index(G)

# Convert a directed graph to an undirected graph
undirected_G = nk.graphtools.toUndirected(G)

# Find all connected components
components = nk.components.ConnectedComponents(undirected_G)
components.run()

effective_diameters = []

# Calculate the effective diameter for each connected component separately
for component_nodes in components.getComponents():
    subgraph = nk.graphtools.subgraphFromNodes(undirected_G, component_nodes)
    if subgraph.numberOfEdges() > 0:
        ed_approx = nk.distance.EffectiveDiameterApproximation(subgraph)
        ed_approx.run()
        effective_diameters.append(ed_approx.getEffectiveDiameter())

# Calculate the average effective diameter of all connected components
if effective_diameters:
    avg_effective_diameter = np.mean(effective_diameters)
    print(f"Average Effective Diameter (All Components): {avg_effective_diameter}")
else:
    print("No effective diameters found.")

#Calculate the clustering coefficient (Clustering Coefficient)
clustering_coeff = nk.globals.ClusteringCoefficient.exactGlobal(G)

# Count isolated points
isolated_nodes = [node for node in undirected_G.iterNodes() if undirected_G.degree(node) == 0]
num_isolated_nodes = len(isolated_nodes)
print(f"Number of isolated nodes: {num_isolated_nodes}")

nk.community.detectCommunities(nk.graphtools.toUndirected(G))
print("Number of Nodes is", G.numberOfNodes())
print("Number of Edges is", G.numberOfEdges())
print(f"Gamma Index of the network: {gamma_index}")
print(f"Clustering Coefficient: {clustering_coeff}")

# Create a dictionary to store the in-degree of a node (the number of times it is pointed to)
in_degree_counts = {}

# Traverse each node in the graph
for node in G.iterNodes():
    in_degree = 0
    for neighbor in G.iterInNeighbors(node):
        in_degree += 1
    in_degree_counts[node] = in_degree

# Find the node with the highest in-degree
max_in_degree_node = max(in_degree_counts, key=in_degree_counts.get)
max_in_degree = in_degree_counts[max_in_degree_node]

print(f"Node {max_in_degree_node} has the highest in-degree with {max_in_degree} incoming edges.")

# Find the top 150 nodes with the highest in-degree
top_in_degree_nodes = sorted(in_degree_counts, key=in_degree_counts.get, reverse=True)[:150]

# Create a dictionary containing output information
output_data = {
    'Node ID': top_in_degree_nodes,
    'In-degree': [in_degree_counts[node_id] for node_id in top_in_degree_nodes],
    'Title': [node_attributes[node_id]['title'] for node_id in top_in_degree_nodes]
}

# Create a DataFrame object
df = pd.DataFrame(output_data)

# Write DataFrame to Excel file
df.to_excel('top_in_degree_nodes_WholeDB.xlsx', index=False)
