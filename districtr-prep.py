
import geopandas as gpd
import pandas as pd
import os
import os.path as path
from shutil import rmtree


"""
Creates a file with helpful descriptions and a copy of the desired shapefile. To
be added to the shapes/ directory of the districtr-process repo.
"""

georoot = "./data/geometries/"
exist = "wisconsin-wards-2020-acs-adjoined"
out = "./data/out/"

# Clean out the out directory.
if path.exists(out): rmtree(out); os.mkdir(out)

# Read in existing geographic data.
existing = gpd.read_file(path.join(georoot, exist))

# Create a CSV where the first column is the column name and the second is its
# dtype.
columns = list(existing)
types = [existing[column].dtype for column in columns]
pd.DataFrame.from_dict({
	"name": columns,
	"type": types
}).to_csv(path.join(out, f"districtr-describe-{exist}.csv"), index=False)

# Create a copy of the shapefile.
existing.to_file(path.join(out, exist))
