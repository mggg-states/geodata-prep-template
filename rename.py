
import os
from os import path

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", help="Current name")
parser.add_argument("-t", "--target", help="New name")
args = parser.parse_args()

"""
Renames all files in the specified root directory, keeping their extensions.
Optionally renames the directory, and all the files after the directory. (This
is especially useful when renaming things like block group or block shapefiles
downloaded from the Census Bureau!)
"""
# The existing root directory and the desired name.
source = args.source or ""
target = args.target or ""

# Rename each file.
for file in os.listdir(source):
  # Check whether the file has an extension.
  if "." in file:
      extension = file[file.index("."):]
      os.rename(path.join(source, file), path.join(source, target + extension))

# Rename the source directory.
split = source.split("/")
_base = split[:-1] if split[-1] != "" else split[:-2]
base = "/".join(_base)
new_root = path.join(base, target)
os.rename(source, new_root)
