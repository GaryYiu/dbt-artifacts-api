import json
from pathlib import Path

from dbt_artifacts_api.model import Node

def parse_manifest(manifest_path: Path) -> list[Node]:
    manifest = json.loads(manifest_path.read_text())
    return [Node(**raw) for raw in manifest["nodes"].values()]