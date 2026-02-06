# GeoGraphNetworks

### Shapefile-Derived Datasets for Accurate and Scalable Graph Representations

GeoGraphNetworks provides a comprehensive collection of large-scale transportation and hydrographic networks derived from official geospatial data. These datasets are prepared as clean, analysis-ready graph structures that support research, modeling, and infrastructure studies.

The repository includes nationwide networks for:

* **United States of America (USA)** — roads and railways
* **Great Britain (GB)** — roads and rivers

All datasets are designed to be immediately usable for graph and network analysis.

---

## Data Availability

The GeoGraphNetworks data repository is hosted on Figshare:

[https://figshare.com/articles/dataset/GeoGraphNetworks_Great_Britain_s_Web_of_Roads_Rivers/27284859](https://figshare.com/articles/dataset/GeoGraphNetworks_Great_Britain_s_Web_of_Roads_Rivers/27284859)

This GitHub repository provides:

* documentation
* preprocessing pipeline
* tools used to generate the datasets
* visual representations of the networks

---

## Dataset Coverage

### United States

* Primary and secondary road networks
* Coverage across all 50 states
* 1 federal district (Washington, D.C.)
* 5 territories
* **Total: 56 road networks**

Rail infrastructure:

* Single nationwide railway network
* Includes cross-border connectivity with Canada

Files:

* 57 Excel (.xlsx)
* 57 JSON
* **Total: 114 files**

---

### Great Britain

* Road and river infrastructure
* Tiled using Ordnance Survey 100 km × 100 km grid

Files:

* 53 Excel (.xlsx)
* 53 JSON
* **Total: 106 files**
* 52 road networks
* 1 river network

Each file is named using the official Ordnance Survey tile code.

---

## File Formats

### JSON

Contains graph objects built using NetworkX and ready for immediate use in Python workflows.

### Excel

Provides edge lists that can be imported into any environment or language to construct graph networks.

This dual format ensures compatibility across different tools and platforms.

---

## Processing Pipeline

This repository also includes the complete preprocessing pipeline used to generate the graph datasets from raw shapefiles.

The pipeline:

* cleans and deduplicates geometries
* removes contained or redundant segments
* detects intersections efficiently using spatial indexing
* splits lines at intersections
* computes segment lengths in a projected coordinate system
* exports clean edge lists for graph construction

The workflow is implemented using:

* GeoPandas
* Shapely
* Pandas
* NumPy

The process is designed to be:

* reproducible
* scalable to large national datasets
* computationally efficient
* topologically consistent

Users can apply the same pipeline to their own shapefiles to generate comparable network datasets.

---

## Intended Use

These networks support:

* graph and network science research
* routing and pathfinding studies
* transportation analysis
* infrastructure planning
* hydrological modeling
* large-scale spatial analytics

GeoGraphNetworks enables researchers, planners, and analysts to explore how roads, railways, and waterways connect people and places at regional and national scales.

---

## Requirements

Python 3.9+

Dependencies:

* GeoPandas
* Shapely
* Pandas
* NumPy

A valid coordinate reference system (CRS) must be defined for all input shapefiles to ensure accurate distance calculations.

---

## Reproducibility

All published networks were generated using the preprocessing workflow provided in this repository.
This ensures that datasets can be regenerated, extended, or customized consistently.

---

## Summary

GeoGraphNetworks combines:

* large-scale geospatial datasets
* ready-to-use graph formats
* an efficient and transparent processing pipeline

to provide reliable, scalable, and reproducible network representations of national infrastructure systems.
