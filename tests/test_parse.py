from pathlib import Path

from dbt_artifacts_api.parse import parse_manifest

FIXTURES = Path(__file__).parent/"fixtures"

def test_dbt_artifacts_return_node():
    nodes = parse_manifest(FIXTURES/"manifest.json")
    assert len(nodes) > 0
    assert all(node.unique_id for node in nodes)