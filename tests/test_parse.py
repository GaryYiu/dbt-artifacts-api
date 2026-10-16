from pathlib import Path

import pytest
from pydantic import ValidationError

from dbt_artifacts_api.model import Node
from dbt_artifacts_api.parse import parse_edges, parse_manifest

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_manifest_returns_nodes():
    nodes = parse_manifest(FIXTURES / "manifest.json")
    assert len(nodes) > 0
    assert all(node.unique_id for node in nodes)


def test_parse_manifest_returns_edges():
    edges = parse_edges(FIXTURES / "manifest.json")
    assert len(edges) > 0
    assert all(edge.parent for edge in edges)
    assert all(edge.child for edge in edges)
    assert all(not edge.parent.startswith("test") for edge in edges)


def test_node_missing_field():
    with pytest.raises(ValidationError):
        Node(unique_id="model.test")
