import json
from pathlib import Path

from dbt_artifacts_api.model import Edge, Node


def parse_manifest(manifest_path: Path) -> list[Node]:
    manifest = json.loads(manifest_path.read_text())
    return [
        Node(
            **{
                **raw,
                "materialized": raw["config"]["materialized"],
                "checksum": raw["checksum"]["checksum"],
            }
        )
        for raw in manifest["nodes"].values()
    ]


def parse_edges(edges_path: Path) -> list[Edge]:
    edges = json.loads(edges_path.read_text())
    return [
        Edge(parent=parent, child=child)
        for child, parents in edges["parent_map"].items()
        for parent in parents
    ]
