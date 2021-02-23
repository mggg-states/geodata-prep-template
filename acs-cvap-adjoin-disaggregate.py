import geopandas as gpd
import warnings
import pandas as pd
import os
from os import path
import maup

from geometry import prorate

"""
This script adjoins and disaggretates provided datasets from their parent
geometries (generally block groups) to blocks.
"""

#################
# INITIAL SETUP #
#################

# Do we want to restart the whole process?
restart = False

# Set the state.
state = 27

# Set up some filenames.
georoot = "../data/geometries/"
demoroot = "../data/demographics/"
outdir = path.join(georoot, "blocks-demo-adjoined")

# Which years of CVAP data are we attaching?
year = 2019

# Turn on progress bars.
maup.progress.enabled = True

# Filter out UserWarnings.
warnings.filterwarnings('ignore', 'GeoSeries.isna', UserWarning)


###############################################################
# JOIN ACS, CVAP DATA TO BLOCK GROUPS, DISAGGREGATE TO BLOCKS #
###############################################################

# Load geographies, ACS data, and CVAP data.
bgs_geo = gpd.read_file(path.join(georoot, "bgs"))
bgs_acs = pd.read_csv(path.join(demoroot, "acs-joined.csv"))
bgs_cvap = pd.read_csv(path.join(demoroot, "acs-cvap-transposed/bg-cvaps-t-2019.csv"))

# Join ACS and CVAP data to geographies. First, ensure that the GEOID columns are
# all the same type. Then, merge the lists on GEOIDs.
bgs_geo["GEOID"] = bgs_geo["GEOID"].astype(bgs_acs["GEOID"].dtype)
bgs_cvap["GEOID"] = bgs_cvap["geoid"].astype(bgs_acs["GEOID"].dtype)

bgs = bgs_geo.merge(bgs_cvap, on="GEOID")
bgs = bgs.merge(bgs_acs, on="GEOID")

# Create a list of columns to disaggregate to blocks; we do this in separate
# parts, weighting population differently than voting-age population.
pop_columns = list(set(c for c in list(bgs_acs) if "VAP" not in c) - {"GEOID"})
acsvap_columns = [column for column in list(bgs_acs) if "VAP" in column]
cvap_columns = list(bgs_cvap)
vap_columns = list(set(acsvap_columns + cvap_columns) - {"GEOID", "geoid"})

# Load the block shapefile.
blocks = gpd.read_file(path.join(georoot, "blocks"))

# Prorate population data and (C)VAP data separately.
blocks = prorate(blocks, bgs, "2010POP", "2010POP", columns=pop_columns)
blocks = prorate(blocks, bgs, "2010VAP", "2010VAP", columns=vap_columns)

# Get all the columns we want.
allcols = pop_columns + vap_columns + ["GEOID", "geometry"]

# Ensures that we aren't straying too far from the real values, as well as
# asserts that no column has a sum greater than the total population.
for column in pop_columns + vap_columns:
	print(column, abs(blocks[column].sum() - bgs[column].sum()))

	try: assert blocks[column].sum() <= blocks["TOTPOP19"].sum()
	except AssertionError:
		print(
			f"The {column} column has a sum greater than the total population. "
			f"Something isn't right."
		)

# Write to file.
if not path.exists(outdir): os.mkdir(outdir)
gpd.GeoDataFrame(blocks[allcols], geometry="geometry").to_file(path.join(outdir))
