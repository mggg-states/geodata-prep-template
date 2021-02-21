
import geopandas as gpd
import censusdata
import maup


def dissolve(source, join="CONGDIST", columns=[]):
    """
    Dissolves source geography boundaries based on a column which identifies
    the smaller geography with the larger one.

    :param source: String or geodataframe; string is a filepath, geodataframe is source.
    :param join: String; column on which boundaries are joined; optional.
    :param columns: List; columns to sum when dissolving; optional.
    :return: Geodataframe with dissolved boundaries.
    """
    # Dissolve VTD geometries into congressional district ones.
    source = gpd.read_file(source) if type(source) == str else source
    target = source[[join, "geometry"]].dissolve(by=join)

    # If columns are specified, we aggregate data from VTDs to whatever the
    # target is. If a file destination is provided, send the output to a
    # shapefile.
    if len(columns) > 0:
        assignment = maup.assign(source, target)
        target[columns] = source[columns].groupby(assignment).sum()

    return target


def prorate(target, source, targetcol, sourcecol, columns):
    """
    Prorates data the source geometries down to the target geometries.

    :param target: Target geometries.
    :param source: Source geometries.
    :param targetcol: Column for target weights.
    :param sourcecol: Column for source weights.
    :param columns: Columns to prorate.
    :return: Geodataframe with prorated data.
    """
    assignment = maup.assign(target, source)
    weights = target[targetcol] / assignment.map(source[sourcecol])
    prorated = maup.prorate(assignment, source[columns], weights)
    target[columns] = prorated

    return target


def retrieve(
        fips,
        year,
        dataset="acs5",
        geometry=[],
        cols=["B01001_001E", "GEO_ID"]
    ):
    """
    Retrieves data from the census API.

    :param fips: Integer; state FIPS houston from which we retrieve data.
    :param year: Integer; year for which we retrieve data.
    :param dataset: String; Census dataset from which we retrieve data.
    :param geometry: String; geometry for which we retrieve data.
    :param cols: List; columns of data to retrieve.
    :return: Properly-formatted dataframe.
    """
    return censusdata.download(
        dataset,
        year,
        censusdata.censusgeo(
            [("state", str(fips))] + geometry
        ),
        cols
    )


def reformat(df, geo=("GEO_ID", "GEOID"), colmap={"B01001_001E": "TOTPOP"}):
    """
    Reformats census api data into a more familiar format.

    :param df: Dataframe.
    :param geo: Tuple; header to replace, and replacement header.
    :param colmap: Dictionary; maps old header names to new ones.
    :return: Modified dataframe.
    """
    # Properly format all the geoids so they don't have that annoying tag on the
    # front.
    geo_source, geo_target = geo
    df[geo_target] = df[geo_source].apply(lambda g: int(g.split("US")[1]))

    # Set the index to be the "GEOID" column, but immediately reset the index
    # so we just get the index to be {1, ..., n}.
    df = df.set_index(geo_target)
    df = df.reset_index()

    # Delete old column.
    del df[geo_source]

    # Rename the column(s) appropriately.
    df = df.rename(columns=colmap)

    return df


def reset_index(df, _from, _to):
    """
    Given a dataframe, reset the dataframe's index and remove the _from column.

    :param df: (Geo)dataframe.
    :param _from: Column to take data from.
    :param _to: Column to take data to.
    :return: (Geo)dataframe with reset index.
    """
    df = df.reset_index()
    df[_to] = df[_from].astype(int)
    df = df.set_index(_to)
    df = df.reset_index()
    del df[_from]

    return df


def variables(prefix, start, stop, suffix="E"):
    """
    Returns the ACS variable names from the provided prefix, start, stop, and
    suffix parameters. Used to generate batches of names, especially for things
    like voting-age population. Variable names are formatted in the following
    way:

                    <prefix>_<number identifier><suffix>

    where <prefix> is a population grouping, <number identifier> is the number
    of the variable in that grouping, and <suffix> designates the file used.

    :param str prefix: Population grouping; typically "B01001".
    :param int start: Where to start numbering.
    :param int stop: Where to stop numbering. Inclusive.
    :param str suffix: Suffix designating the file. For most purposes, this is
        "E".
    """
    return [
        f"{prefix}_{str(t).zfill(3)}{suffix}"
        for t in range(start, stop+1)
    ]
