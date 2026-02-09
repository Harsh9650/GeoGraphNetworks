import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.ops import split
from shapely.geometry import Point
from shapely.geometry import MultiLineString, LineString


def extract_nodes(line):
    """Extracting First and Last node"""
    return Point(line.coords[0]), Point(line.coords[-1])
    
        
def drop_z(geom):
    """Removing Z dimension if present."""
    if hasattr(geom, "has_z") and geom.has_z:
        return type(geom)([(x, y) for x, y, *_ in geom.coords])
    return geom


def data_cleaning(road_network):
    """
    Cleaning the road network while preserving original semantics:
    - add LINEARID
    - drop duplicate geometries
    - remove lines fully contained inside others
    - extract start/end nodes
    """

    # -------------------------------------------------
    # 1. drop duplicates + reset index
    # -------------------------------------------------
    gdf = road_network.drop_duplicates(subset="geometry").reset_index(drop=True)

    gdf["LINEARID"] = gdf.index + 1

    # -------------------------------------------------
    # 2. removing contained lines
    # -------------------------------------------------
    sindex = gdf.sindex
    contained_ids = set()

    for idx, geom in zip(gdf.LINEARID, gdf.geometry):

        # only test nearby candidates
        candidates = list(sindex.intersection(geom.bounds))

        for j in candidates:
            other_id = gdf.LINEARID.iloc[j]

            if idx == other_id:
                continue

            other_geom = gdf.geometry.iloc[j]

            if geom.within(other_geom):
                contained_ids.add(idx)
                break

    gdf = gdf[~gdf.LINEARID.isin(contained_ids)].reset_index(drop=True)

    # -------------------------------------------------
    # 3. extracting endpoints
    # -------------------------------------------------
    gdf[["start_node", "end_node"]] = (
        gdf.geometry
           .apply(lambda x: pd.Series(extract_nodes(x)))
    )

    #print("cleaning performed")

    return gdf



def intersections(road_network):
    """
    - only one intersection per pair (i < j)
    - only Point geometries
    - ignore MultiPoint/overlaps
    Using spatial index for speed
    """

    gdf = road_network

    sindex = gdf.sindex
    rows = []

    for idx, geom in zip(gdf.LINEARID, gdf.geometry):

        candidates = list(sindex.intersection(geom.bounds))

        for j in candidates:
            other_id = gdf.LINEARID.iloc[j]

            if other_id <= idx:
                continue

            other_geom = gdf.geometry.iloc[j]

            inter = geom.intersection(other_geom)

            if inter.geom_type == "Point":
                rows.append((idx, inter))
                rows.append((other_id, inter))

    data = pd.DataFrame(rows, columns=["LINEARID", "intersection_node"])

    return data.drop_duplicates().reset_index(drop=True)


def intersection_tracking(road_network):
    """
    attach start_node, end_node, geometry to each intersection row
    """

    data = intersections(road_network)

    data = data.merge(
        road_network[["LINEARID", "start_node", "end_node", "geometry"]],
        on="LINEARID",
        how="left"
    )

    #print("intersections found")

    return data
    
    
    
def subroute_length(data):
    """
    For each road–intersection pair, split the original LineString into two segments:
    1) start_node  → intersection_node
    2) intersection_node → end_node

    The length of each segment is computed (in kilometres).
    If splitting fails to produce exactly two LineStrings, the segment lengths are
    marked as missing and the problematic geometry is recorded for inspection.
    """

    start_to_intersect, intersect_to_end, geom_with_issues = [], [], []

    for row in data.itertuples():

        if row.start_node == row.intersection_node:
            start_to_intersect.append(row.intersection_node.length / 1000)
            intersect_to_end.append(row.geometry.length / 1000)

        elif row.intersection_node == row.end_node:
            start_to_intersect.append(row.geometry.length / 1000)
            intersect_to_end.append(row.intersection_node.length / 1000)

        else:
            result = split(row.geometry, row.intersection_node)
            linestrings = [g for g in result.geoms if isinstance(g, LineString)]

            if len(linestrings) == 2:
                start_to_intersect.append(linestrings[0].length / 1000)
                intersect_to_end.append(linestrings[1].length / 1000)
            else:
                start_to_intersect.append(np.nan)
                intersect_to_end.append(np.nan)
                geom_with_issues.append((row.geometry, row.intersection_node))

    data["start_to_intersect"] = start_to_intersect
    data["intersect_to_end"] = intersect_to_end

    data = data.drop("geometry", axis=1)

    column_names = [
        "LINEARID",
        "start_node",
        "intersection_node",
        "end_node",
        "start_to_intersect",
        "intersect_to_end",
    ]

    data = data.reindex(columns=column_names)

    #print("length assigned")

    return data, geom_with_issues



def data_merge(data):
    """
    Each row represents two road segments:
    (start_node → intersection_node) and (intersection_node → end_node).

    The table is reshaped so that each segment becomes its own row with
    three fields only: start_node, end_node and distance. Invalid segments
    (zero length or identical start/end) are removed and duplicate
    connections are ignored before exporting coordinates for graph creation.
    """

    # create two segment tables and stack them vertically
    subset_1 = data.drop(["LINEARID", "end_node", "intersect_to_end"], axis=1) \
                   .rename(columns={"intersection_node": "end_node",
                                    "start_to_intersect": "distance"})

    subset_2 = data.drop(["LINEARID", "start_node", "start_to_intersect"], axis=1) \
                   .rename(columns={"intersection_node": "start_node",
                                    "intersect_to_end": "distance"})

    edges = pd.concat([subset_1, subset_2], ignore_index=True)

    # remove zero-length and self-connections
    edges = edges[(edges["distance"] > 0) &
                  (edges["start_node"] != edges["end_node"])]

    # remove duplicate undirected connections
    seen = set()
    rows = []

    for row in edges.itertuples():
        key = tuple(sorted(((row.start_node.x, row.start_node.y),
                            (row.end_node.x, row.end_node.y))))

        if key in seen:
            continue

        seen.add(key)

        rows.append((
            row.start_node.x,
            row.start_node.y,
            row.end_node.x,
            row.end_node.y,
            row.distance
        ))

    dataset = pd.DataFrame(
        rows,
        columns=[
            "startnode_x", "startnode_y",
            "endnode_x", "endnode_y",
            "distance"
        ]
    )

    return dataset



def data_from_shapefile(shape_file, epsg_value, save_name=None):
    """
    Complete preprocessing pipeline:
    1) Load shapefile
    2) Keep only LineString geometries and drop Z values
    3) Reproject to the requested CRS for metric length calculation
    4) Clean network and detect intersections
    5) Split segments and compute sub-route lengths
    6) Merge into final edge list (start_x, start_y, end_x, end_y, distance)
    7) Export dataset
    """

    road_network = gpd.read_file(shape_file)

    if road_network.crs is None:
        # Fallback only for legacy UK rail datasets known to be EPSG:27700
        # road_network = road_network.set_crs("EPSG:27700")
        raise ValueError("Input shapefile has no CRS defined. Set CRS explicitly.")

    road_network = road_network[["geometry"]]

    road_network["geometry"] = road_network["geometry"].apply(drop_z)

    road_network = road_network[
        ~road_network.geometry.apply(lambda g: isinstance(g, MultiLineString))
    ]

    road_network = road_network.to_crs(epsg=epsg_value)

    road_network = data_cleaning(road_network)

    data = intersection_tracking(road_network)

    data, geom_with_issues = subroute_length(data)

    dataset = data_merge(data)

    dataset = dataset.dropna(subset=["distance"])

    if save_name:
        dataset.to_excel(save_name+".xlsx", index=False)

    return dataset, geom_with_issues

