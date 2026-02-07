# Function Reference

This section documents each function in the preprocessing pipeline and the external library operations it relies on.

---

## `data_from_shapefile(shape_file, epsg_value, save_name)`

**Main entry point (run-all pipeline).**

Loads a shapefile and executes the complete preprocessing workflow:

1. Read shapefile
2. Drop Z dimension
3. Remove MultiLineString geometries
4. Reproject to metric CRS
5. Clean topology
6. Detect intersections
7. Split segments and compute lengths
8. Merge to edge list
9. Export to Excel

**Documentation**

* GeoPandas `read_file`
  [https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html](https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html)
* GeoPandas `to_crs`
  [https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html)

---

## `data_cleaning(road_network)`

**Topological cleaning of the network.**

* Removes duplicate geometries
* Assigns unique IDs (`LINEARID`)
* Removes lines fully contained inside others
* Extracts start/end nodes
* Uses spatial index for efficient spatial queries

**Documentation**

* GeoPandas spatial index (`sindex`)
  [https://geopandas.org/en/stable/docs/user_guide/sindex.html](https://geopandas.org/en/stable/docs/user_guide/sindex.html)
* Shapely `within` predicate
  [https://shapely.readthedocs.io/en/stable/manual.html#predicates](https://shapely.readthedocs.io/en/stable/manual.html#predicates)

---

## `intersections(road_network)`

**Detects pairwise line intersections.**

* Uses spatial index to find candidate pairs
* Computes geometric intersections
* Keeps only `Point` intersections
* Avoids duplicate pair checks

**Documentation**

* Shapely `intersection()`
  [https://shapely.readthedocs.io/en/stable/manual.html#object.intersection](https://shapely.readthedocs.io/en/stable/manual.html#object.intersection)

---

## `intersection_tracking(road_network)`

**Associates intersection points with original geometries.**

* Merges intersection results with start/end nodes and geometry
* Prepares data for segment splitting

**Documentation**

* pandas `DataFrame.merge`
  [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)

---

## `subroute_length(data)`

**Splits lines at intersections and computes segment lengths.**

* Splits LineString using intersection node
* Creates two subsegments
* Computes length in projected CRS
* Converts to kilometers
* Records problematic geometries

**Documentation**

* Shapely `split()`
  [https://shapely.readthedocs.io/en/stable/manual.html#shapely.ops.split](https://shapely.readthedocs.io/en/stable/manual.html#shapely.ops.split)
* Shapely `length`
  [https://shapely.readthedocs.io/en/stable/manual.html#object.length](https://shapely.readthedocs.io/en/stable/manual.html#object.length)

---

## `data_merge(data)`

**Constructs the final edge list.**

* Reshapes split segments into start→end edges
* Removes zero-length edges
* Removes self-loops
* Removes duplicate undirected edges
* Outputs coordinate-based edge list

**Documentation**

* Pandas `concat`
  [https://pandas.pydata.org/docs/reference/api/pandas.concat.html](https://pandas.pydata.org/docs/reference/api/pandas.concat.html)
* Pandas filtering
  [https://pandas.pydata.org/docs/user_guide/indexing.html](https://pandas.pydata.org/docs/user_guide/indexing.html)

---

## `drop_z(geom)`

**Removes Z (elevation) dimension from geometries.**

Ensures all processing is strictly 2D for planar distance calculations.

**Documentation**

* Shapely coordinate sequences
  [https://shapely.readthedocs.io/en/stable/manual.html#coordinate-sequences](https://shapely.readthedocs.io/en/stable/manual.html#coordinate-sequences)

---

## `extract_nodes(line)`

**Extracts first and last coordinates of a LineString.**

Returns start and end nodes as `Point` objects.

**Documentation**

* Shapely LineString/Point
  [https://shapely.readthedocs.io/en/stable/manual.html#linestrings](https://shapely.readthedocs.io/en/stable/manual.html#linestrings)

