import json
from pathlib import Path

from dbt_artifacts_api.model import Edge, Invocation, Node, NodeResult


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


def parse_invocation(invocation_path: Path) -> Invocation:
    result = json.loads(invocation_path.read_text())
    return Invocation(
        **{
            **result["metadata"],
            "elapsed_time": result["elapsed_time"],
        }
    )


def parse_node_result(node_result_path: Path) -> list[NodeResult]:
    result = json.loads(node_result_path.read_text())
    return [
        NodeResult(
            **{
                **node_result,
                "invocation_id": result["metadata"]["invocation_id"],
                "rows_affected": node_result["adapter_response"]["rows_affected"],
                "bytes_processed": node_result["adapter_response"].get("bytes_processed"),
            }
        )
        for node_result in result["results"]
    ]
