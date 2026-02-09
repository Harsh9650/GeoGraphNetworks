import zipfile
from pathlib import Path
from GraphNetwork import graph_networkx
from shp2graph import data_from_shapefile


def main():
    zip_filename = Path("tl_2023_48_prisecroads.zip")
    network_name = "Texas"

    if not zip_filename.exists():
        raise FileNotFoundError(zip_filename)

    # Extract into its own folder
    extract_dir = zip_filename.stem

    with zipfile.ZipFile(zip_filename, "r") as z:
        z.extractall(extract_dir)

    shp_path = Path(extract_dir) / "tl_2023_48_prisecroads.shp"

    dataset, geom_with_issues = data_from_shapefile(
        shp_path,
        epsg_value=2163,
        save_name=network_name
    )

    network = graph_networkx(
        dataset,
        file_name=network_name,
        plt_size=(50, 30),
        node_size=0.1
    )

    print(
        f"Number of Nodes: {network.number_of_nodes()}, "
        f"Number of Edges: {network.number_of_edges()}"
    )


if __name__ == "__main__":
    main()
