''' This code is the functions for leiden community detection algorithm and applying it to the flow data.
We first make a migration matrix and graph and then apply the leiden algorithm to detect the communities.
We use the partition files results from this code to the main code of solution1 and solution2 of mapping the regions'''

import igraph as ig
import leidenalg as la
import pandas as pd
import os

def leidenPartitions(df, origin, destination, weight):
    ''' This function applies the leiden algorithm to detect the communities in the weighted graph.'''

    # convert flows into undirected flows
    try:
        df['key'] = df.apply(lambda row: tuple(sorted((row[origin], row[destination]))), axis=1)
        df = df.groupby('key')[weight].sum().reset_index()
        df['nodeA'] = df['key'].apply(lambda x: x[0])
        df['nodeB'] = df['key'].apply(lambda x: x[1])
        del df['key']
    except Exception as e:
        print(f"Flows cannot be converted into undirected flows. Error: {e}")

    # define undirected igraph
    tuples = [tuple(x) for x in df[['nodeA', 'nodeB', weight]].values]
    G_igraph = ig.Graph.TupleList(tuples, edge_attrs=[weight])

    # Apply the Leiden algorithm
    try:
        partition = la.find_partition(G_igraph, la.ModularityVertexPartition, weights=weight)
        modularity = G_igraph.modularity(partition.membership, weights=weight)
        print("The modularity is {}".format(modularity))
    except Exception as e:
        print(f"Leiden algorithm failed. Error: {e}")

    # Create partition DataFrame
    try:
        partition_df = pd.DataFrame({'node': G_igraph.vs['name'], 'partition': partition.membership})
        partition_df.rename(columns={'index': 'node'}, inplace=True)
        textlist = ["The modularity is {}".format(modularity),
                    "The number of partitions is {}".format(len(partition_df['partition'].unique()))]
    except Exception as e:
        print(f"Partition DataFrame cannot be created. Error: {e}")

    return partition_df, textlist

def leidenimplement(flowdir, origin, destination, weight):
    '''
    This function reads all the csv files in the directory that contains flow data (flowdir) and apply the leiden algorithm to detect the communities.
    It saves the partition and the modularity values in a text file.
    '''

    # walk through the directory of flow data
    files = os.listdir(flowdir)
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(flowdir, file)
            df = pd.read_csv(file_path)

            # apply leiden algorithm
            partition, text = leidenPartitions(df, origin, destination, weight)
            # define the new path to save the partition and the summary
            newpath = os.path.join(flowdir, "Leiden_partition")

            if not os.path.exists(newpath):
                os.makedirs(newpath)
            try:
                # Save the partition CSV
                csv_filename = f"Leiden_partition_{file[-8:]}"
                csv_file_path = os.path.join(newpath, csv_filename)
                partition.to_csv(csv_file_path, index=False)

                summary_filename = f"Leiden_partition_summary_{file[:-4]}.txt"
                summary_file_path = os.path.join(newpath, summary_filename)
                with open(summary_file_path, 'w') as f:
                    f.write('\n'.join(text))
            except Exception as e:
                print(f"Partition and summary files cannot be saved. Error: {e}")

# apply leiden algorithm to the flow data
folder = '/Users/maryamtorkashvand/Library/CloudStorage/OneDrive-UniversityofIowa/My_Phd/Phd_Courses/Spring_2024/Geoprogramming/project/data/'
try:
    flowdir = folder + 'flows'
    origin = 'orgState'
    destination = 'destState'
    weight = 'flows'
    leidenimplement(flowdir, origin, destination, weight)
    print("Leiden algorithm applied successfully.")
except Exception as e:
    print(f"Leiden algorithm failed. Error: {e}")