
import pandas as pd
import numpy as np
from os import path

from geometry import retrieve, reformat, variables

"""
This script retrieves data from the ACS for the provided year, summary file
type, and variable names. Because Census block groups are the smallest level for
which these statistics are reported, we attach a GEOID column to each row of
data so it can be joined to its respective block groups later.
"""


def suml(list):
	"""
	Concatenates a list of lists and returns the concatenated lists.
	"""
	l = []
	for _l in list: l += _l
	return l


# Set the state FIPS code and some file locations.
state = 55
georoot = "./data/geometries/"
demoroot = "./data/demographics/"

# For which year of the ACS are we getting data?
year = 2019

# Set a column -> description mapping. Variable names can be found here:
# https://api.census.gov/data/2019/acs/acs5/variables.html.
columns = {
	"B01001_001E": "TOTPOP19",
	"B02001_002E": "WHITE19",
	"B02001_003E": "BLACK19",
	"B02001_004E": "AMIN19",
	"B02001_005E": "ASIAN19",
	"B02001_006E": "NHPI19",
	"B02001_007E": "OTH19",
	"B02001_008E": "2MORE19",
	"B03002_002E": "NHISP19"
}

columngroups = {
	"VAP19": variables("B01001", 7, 25, suffix="E") + variables("B01001", 31, 49, suffix="E"),
}

# Set the list of columns to retrieve.
cols = ["GEO_ID"] + list(columns) + suml([columngroups[name] for name in columngroups])

# Get the GEOIDs and attach them to the dataframe.
bgs_acs = pd.DataFrame().append(
	retrieve(
		state, year, dataset="acs5", cols=cols,
		geometry=[("county", "*"), ("tract", "*"), ("block group", "*")]
	)
)

# Go through each column and ensure that their sum is *not* 0.
for column in list(bgs_acs):
	try:
		assert bgs_acs[column].sum() != 0
	except AssertionError:
		print(
			f"The variable \"{column}\" appears to have returned no results. Please"
			f"check that the \"{column}\" variable is reported at the geography "
			f"level requested."
		)

# Sum the appropriate columns for calculating VAP.
for column, group in columngroups.items():
	summation = np.zeros(len(bgs_acs))
	for subcolumn in group: summation += np.array(list(bgs_acs[subcolumn]))
	bgs_acs[column] = list(summation)

# Rename columns and fix GEOID column.
colmap = {"GEO_ID": "GEOID"}
colmap.update(columns)
bgs_acs = reformat(bgs_acs, colmap=colmap)

# Create a column for designating Hispanic and Latino population by subtracting
# the "not Hispanic/Latino" column from the "total population" column.
bgs_acs["HISP19"] = bgs_acs["TOTPOP19"] - bgs_acs["NHISP19"]

# Trim off unnecessary columns and save to file.
allcols = ["GEOID"] + list(columns.values()) + ["VAP19", "HISP19"]
bgs_acs[allcols].to_csv(path.join(demoroot, "acs-joined.csv"), index=False)
