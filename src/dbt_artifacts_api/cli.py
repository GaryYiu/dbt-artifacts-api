import argparse
from pathlib import Path

from dbt_artifacts_api.model import ResourceType
from dbt_artifacts_api.parse import parse_manifest, parse_node_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_path", type=Path)
    parser.add_argument("run_results_path", type=Path)
    args = parser.parse_args()

    results = parse_node_result(args.run_results_path)
    manifest = parse_manifest(args.manifest_path)

    models = [node for node in manifest if node.resource_type == ResourceType.MODEL]
    results_filter = [
        result for result in results for model in models if result.unique_id == model.unique_id
    ]
    node_sorted = sorted(results_filter, key=lambda r: r.execution_time, reverse=True)[:5]
    for n in node_sorted:
        print(f"{n.unique_id}:{n.execution_time:.2f}s")


if __name__ == "__main__":
    main()
