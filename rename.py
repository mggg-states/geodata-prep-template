
import os
from os import path

"""
Renames all files in the specified root directory, keeping their extensions.
Optionally renames the directory, and all the files after the directory. (This
is especially useful when renaming things like block group or block shapefiles
downloaded from the Census Bureau!)
"""

# The existing root directory and the desired name.
root = ""
new_name = ""

# Rename each file.
for file in os.listdir(root):
	# Check whether the file has an extension.
	if "." in file:
		extension = file[file.index("."):]
		os.rename(path.join(root, file), path.join(root, new_name + extension))

# Rename the root directory.
split = root.split("/")
_base = split[:-1] if split[-1] != "" else split[:-2]
base = "/".join(_base)
new_root = path.join(base, new_name)
os.rename(root, new_root)
