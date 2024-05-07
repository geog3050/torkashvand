'''
This script is the second solution to map the regions in a consistent way over time.
This script redefine the partitions based on the overlap of the regions in the maps.
The example I used is the migration regions in the US from 1882 to 1930, in three time intervals, based on leiden community detection algorithm.
we map the regions from louvain community detection in away that the regions can be comparable visually over time.
'''

import geopandas as gpd
import pandas as pd
import os
import matplotlib.pyplot as plt

folder = '/Users/maryamtorkashvand/Library/CloudStorage/OneDrive-UniversityofIowa/My_Phd/Phd_Courses/Spring_2024/Geoprogramming/project/data/'
shapefile = folder + 'states48hq.shp'
partitiondir = folder + 'flows/Leiden_partition'

# read the shapefile and change the projection
states48 = gpd.read_file(shapefile)
states48 = states48.to_crs("ESRI:102003")
# make a list of the partitions from the partition csv files
partitions = []
for dirpath, dirnames, files in os.walk(partitiondir):
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(dirpath, file)
            df = pd.read_csv(file_path)
            partitions.append(df)

# Function to calculate overlap Index or Jaccard Index which is the intersection over the union of two sets
def calculate_overlap(set1, set2):
    try:
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        index = intersection / union if union else 0
        return index
    except Exception as e:
        print(f"Error in calculating overlap index. the index is 0. Error: {e}")
        return 0

maps = []
threshold = 0.2  # overlap index threshold for considering partitions as similar (0.2 means 20% overlap)

''' We iterate over the partitions and map the regions based on the overlap of the regions in the maps.'''

for i, partition in enumerate(partitions):
    # join the partition with states48 on the node column
    gdf = states48.merge(partition.rename(columns={'node': 'rootsid', 'partition': f'partition_{i}'}), on='rootsid')
    if i > 0:
        # calculate overlap index between current and previous partitions, map similar ones
        prev_gdf = maps[-1]
        current_labels = {}
        for label, group in gdf.groupby(f'partition_{i}'):
            best_match = None
            best_score = 0
            for prev_label, prev_group in prev_gdf.groupby(f'partition_{i - 1}'):
                score = calculate_overlap(set(group['rootsid']), set(prev_group['rootsid']))
                if score > best_score and score >= threshold:
                    best_match = prev_label # update the best match
                    best_score = score # update the best score
            if best_match:
                current_labels[label] = best_match
            else:
                current_labels[label] = f"Region {len(current_labels) + 1}"
        gdf[f'partition_{i}'] = gdf[f'partition_{i}'].map(current_labels)
    else:
        # initialize partitions for the first map if it is the first map
        unique_partitions = gdf[f'partition_{i}'].unique()
        partition_to_region = {part: f"Region {j + 1}" for j, part in enumerate(unique_partitions)}
        gdf[f'partition_{i}'] = gdf[f'partition_{i}'].map(partition_to_region)

    maps.append(gdf)

# Plotting the maps
title_list = ["1882_1887", "1887_1901", "1901_1924"]
fig, axes = plt.subplots(1, len(maps), figsize=(30, 10))

for i, gdf in enumerate(maps):
    gdf.plot(ax = axes[i], column = f'partition_{i}', edgecolor = "#8f8c8c", linewidth = 0.5)
    axes[i].set_title(title_list[i], fontsize=26, fontweight='bold')
    axes[i].set_axis_off()

fig.tight_layout()
plt.subplots_adjust(wspace=0.02, hspace=0.02)
plt.show()

output = folder + 'MigrationRegionsSolution1.png'
fig.savefig(output, dpi=300, bbox_inches='tight')