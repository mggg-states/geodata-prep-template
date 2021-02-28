import geopandas as gpd
import pandas as pd
from os import path

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--geometries", help="Geographic files directory")
parser.add_argument("-s", "--state", help="State FIPS")
args = parser.parse_args()

from geometry import retrieve, reformat

"""
This script retrieves population data (and other selected variables, if desired)
from the 2010 Census PL94-171 dataset, joins them to block and block group
geometries, and saves the geometries to file. The Census data retrieved are the
weights used to disaggregate data from larger geometries, down to blocks, then
back up to other geometries.
"""

# File locations.
georoot = args.geometries or "./data/geometries/"

# Set the state FIPS.
state = args.state or 27

# Create initial dataframes.
bgs_census = pd.DataFrame()
blocks_census = pd.DataFrame()

# Retrieve Census data for block/groups.
bgs_census = bgs_census.append(retrieve(
	state, 2010, dataset="sf1",
	geometry=[("county", "*"), ("tract", "*"), ("block group", "*")],
	cols=["GEO_ID", "P010001", "P008001"]
))

blocks_census = blocks_census.append(retrieve(
	state, 2010, dataset="sf1",
	geometry=[("county", "*"), ("tract", "*"), ("block", "*")],
	cols=["GEO_ID", "P010001", "P008001"]
))

# Load block/group geometries.
bgs = gpd.read_file(path.join(georoot, "bgs"))
blocks = gpd.read_file(path.join(georoot, "blocks"))

# Reformat the dataframes so they have proper column identifiers and indices.
# Then, adjoin that data to the block groups and blocks we found earlier.
bgs_census = reformat(
	bgs_census, colmap={"P010001": "VAP10", "P008001": "TOTPOP10"}
)

blocks_census = reformat(
	blocks_census, colmap={"P010001": "VAP10", "P008001": "TOTPOP10"}
)

# Merge data.
bgs["GEOID"] = bgs["GEOID"].astype(int)
bgs = bgs.merge(bgs_census, on="GEOID")

blocks["GEOID"] = blocks["GEOID10"].astype(int)
blocks = blocks.merge(blocks_census, on="GEOID")

# Write to file.
bgs.to_file(path.join(georoot, "bgs"))
blocks.to_file(path.join(georoot, "blocks"))
