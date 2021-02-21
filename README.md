
This is a template project for collecting, disaggregating, and aggregating data
for use with districtr and associated projects.

## Installation
While this isn't a python package, it requires a number of packages to be
pre-installed before the scripts can be used. To install these packages, see
the `requirements.txt` file or run `pip install -r requirements.txt`.

## Usage
The process for _properly_ retrieving, disaggregating, and aggregating data,
especially to attach to geometries, is often arduous. Here, we provide a set of
scripts and a sensible file structure to aid in that process.

### Steps

1. **Gather geometric data.** Shapefiles for the desired geometries (e.g.
   Wisconsin wards), as well as auxiliary geometries (Census blocks, Census
   block groups) should be retrieved _and opened using a GIS tool to verify that
   they are well-formed_ before doing anything else. Census TIGER/Line shapefiles
   are the best options for auxiliary geometries.
2. **Sensibly rename files.** Use the `rename.py` script to rename the Census
   TIGER/Line shapefiles, as _all_ files in the directory must have the same
   prefix. For example, Wisconsin's Census block directory and included files
   all have the name `tl_2019_55_tabblock10`, which isn't particularly
   descriptive. Renaming to something like `wisconsin-blocks` or just `blocks`
   is cleaner.
3. **Attach weighting data to auxiliary geometries.** To do so, run the
   `census-data-adjoin.py` script. This retrieves population and voting-age
   population data from the 2010 Census PL94-171 dataset, which will serve as
   weights for ACS population and voting-age population data when disaggregated
   from block groups to blocks. `census-data-adjoin.py` adjoins this data to
   existing Census geometries retrieved in (1) and overwrites the files. **After
   running this script, ensure that the overwritten geometry files are still
   well-formed and contain the required data.**
4. **Attach ACS (/CVAP) data to block group geometries and disaggregate.**
   1. **IF NOT ADJOINING CVAP DATA, SKIP.** Run the `cvap-data-prep.py`
      script after unzipping `acs-cvap-2019.zip` in the `data/demographics/`
      directory. This performs a grouping + transposition operation which puts
      the  CVAP data in a desirable format.
   2. **Retrieve ACS data.** Using the `acs-data-retrieve.py` script, retrieve 
      ACS data for the desired year and columns. This downloads the data from
      the Census API and saves it in the `data/demographics/` directory for use
      later.
   3. **Adjoin and disaggregate data.** The `acs-cvap-adjoin-disaggregate.py`
      script joins desired ACS and ACS CVAP data to the provided block group
      shapefile and disaggregates those data down to blocks based on attached
      weighting data (2010 population, 2010 voting-age population). Once
      complete, the shapefiles with adjoined data are saved to the
      `data/geometries/` directory. Be warned, this process might take a while.
5. **Aggregate to desired geometries.** Using the `acs-cvap-aggregate.py`
   script, aggregate block-level data to the desired geometries. This script
   looks for block-level data in the `data/geometries/` folder and outputs
   completed files to the desired location (the `data/geometries/` folder, by
   default.)