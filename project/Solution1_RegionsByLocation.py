'''
This script is first solution to map the regions in consistent way over time.
This script redefine the partitions based on their locations on the map.
The example I used is the migration regions in the US from 1882 to 1930, in three time intervals, based on leiden community detection algorithm.
we map the regions from louvain community detection in away that the regions can be comparable visually over time.
'''

import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
from matplotlib.patches import Patch

folder = '/Users/maryamtorkashvand/Library/CloudStorage/OneDrive-UniversityofIowa/My_Phd/Phd_Courses/Spring_2024/Geoprogramming/project/data/'
# read the shapefile of the states
shapefile = folder + 'states48hq.shp'
states48 = gpd.read_file(shapefile)
partitiondir = folder + 'flows/Leiden_partition'
#print (states48.head())

# read the partition into the df and make a list of the partitions dfs
partition_list = []
map_list = []
for dirpath, dirnames, files in os.walk(partitiondir):
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(dirpath, file)
            df = pd.read_csv(file_path)
            partition_list.append(df)
            # extract last four characters from the filename before '.csv'
            suffix = file[-8:-4]  # Assuming the filename is in the format 'flow_1882_1887.csv'
            try:
                # join the partition with states48 on the node column
                merged_gdf = states48.merge(df, left_on='rootsid', right_on='node', how='inner')
                merged_gdf['map_index'] = suffix
                merged_gdf = merged_gdf.to_crs("ESRI:102003") # change the projection to Albers Equal Area
                map_list.append(merged_gdf)
                print(f"Partition {suffix} merged with the states shapefile successfully.")
            except Exception as e:
                print(f"Partition {suffix} cannot be merged with the states shapefile. Error: {e}")

# print(partition_list)
# print(map_list)

''' Mapping regions in a consistent way over time:
    defining new values for partitions based on the location of the states,
    then replace all instances of that partition value with new value.
    when we do it for all maps, all maps have the same type values in indicator states and we can assign colors to them and the colors will be constant.
    States that are indicators: Maine for NE, California: West, everithing else: Mid, Georgia: SE, Texas: South.
'''
for gdf in map_list:
    partition_value_ME = gdf[gdf["rootsid"] == 123]["partition"].unique()
    gdf["partition"] = gdf["partition"].replace(partition_value_ME, "Region 1")

    partition_value_GE = gdf[gdf["rootsid"] == 113]["partition"].unique()
    gdf["partition"] = gdf["partition"].replace(partition_value_GE, "Region 3")

    partition_value_TX = gdf[gdf["rootsid"] == 148]["partition"].unique()
    gdf["partition"] = gdf["partition"].replace(partition_value_TX, "Region 4")

    partition_value_CA = gdf[gdf["rootsid"] == 106]["partition"].unique()
    gdf["partition"] = gdf["partition"].replace(partition_value_CA, "Region 5")
    # here we check all values in patrition column and change those that are not str to the region2
    gdf["partition"] = gdf["partition"].apply(lambda x: "Region 2" if not isinstance(x, str) else x)

#print(map_list)

# Plotting maps
# define colors for each region and titles for each map
color_dict = {"Region 1": "#8dd3c7", "Region 2": "#e6f5c9", "Region 3": "#bebada", "Region 4": "#80b1d3", "Region 5": "#fbb4ae"}
title_list = ["1882_1887", "1887_1901", "1901_1924"]

fig, axes = plt.subplots(1, 3, figsize=(30, 10))
for idx, map_gdf in enumerate(map_list):
    # Create a new column for color in each geodataframe based on the partition
    map_gdf['color'] = map_gdf['partition'].map(color_dict).fillna("white")
    map_gdf.plot(ax=axes[idx], color=map_gdf['color'], edgecolor = "#8f8c8c", linewidth = 0.5)
    axes[idx].set_title(title_list[idx], fontsize=26, fontweight='bold')
    axes[idx].set_axis_off()
# Create a legend
legend_patches = [Patch(facecolor=color, label=label) for label, color in color_dict.items()]
fig.legend(handles=legend_patches, loc='lower center', ncol=len(legend_patches), bbox_to_anchor=(0.5, 0.05), fontsize=16)
fig.tight_layout()
plt.subplots_adjust(wspace=0.02, hspace=0.02)
plt.show()

output = folder + 'MigrationRegionsSolution2.png'
fig.savefig(output, dpi=300, bbox_inches='tight')