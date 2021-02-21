
import geopandas as gpd
import warnings
import numpy as np
import os
from os import path
import maup

"""
This script aggregates block-level demographic data up to desired geometries.
For example, the pre-filled values here aggregate Wisconsin block-level data up
to wards.
"""

# Set filepath roots.
georoot = "../data/geometries/"
indir = path.join(georoot, "wisconsin-wards-2020")
outdir = path.join(georoot, "wisconsin-wards-2020-acs-adjoined")

# Turn on progress bars.
maup.progress.enabled = True

# Filter out UserWarnings.
warnings.filterwarnings('ignore', 'GeoSeries.isna', UserWarning)

# Do we want to include CVAP data?
cvap = False

# Read in existing data and blocks.
existing = gpd.read_file(indir)
blocks = gpd.read_file(path.join(georoot, "blocks-demo-adjoined")).to_crs(existing.crs)

# Get the columns we want.
all_columns = list(set(list(blocks))-{"GEOID", "geometry"})
nocvap_columns = list(set(c for c in list(blocks) if "_" not in c)-{"GEOID","geometry"})
columns = all_columns if cvap else nocvap_columns

# Aggregate up to precincts.
assignment = maup.assign(blocks, existing)
existing[columns] = blocks[columns].groupby(assignment).sum()

# Fill NaNs with 0.
existing[columns] = existing[columns].fillna(0)

# Assert that our columns are nearly equal.
for column in columns:
	try: assert np.isclose(existing[column].sum(), blocks[column].sum())
	except AssertionError:print(f"The column {column} didn't sum properly.")

# Fix geometries and write to file.
existing["geometry"] = existing["geometry"].buffer(0)
if not path.exists(outdir): os.mkdir(outdir)
existing.to_file(outdir)
