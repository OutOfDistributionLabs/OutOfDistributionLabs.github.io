# Resume the qualified feature-level pilot

Current state: paused for workspace capacity. Authentication works. No valid FeatureBench scores or agent attempts exist. Do not interpret upstream completed=true on a Docker error as successful evaluation.

Use a fresh Linux workspace with Docker and 128 GB storage for serial derived-image preparation, or a supported copy-on-write Docker setup. The managed cloud daemon cannot be reconfigured by this non-root worker. Reset/recover it rather than modifying orphan storage directories. `OOD_DISK_PATH` can select the actual Docker-storage filesystem for the preflight.

Install FeatureBench at source commit `8d4e347ec57546685c5a87e8676bf575db022ea6` in a separate Python 3.12 environment; the evaluator package inventory is recorded. Download dataset revision `76b4a4566e04f4bcc13c35125d4f301791efa736`, Fast split, and select only the manifest IDs, preserving all fields in evaluator-only files. No files containing patches/test patches may be mounted into inference.

Example for the first task, with evaluator-only data paths supplied by trusted setup:

```bash
python -m benchmarks.featurebench_assets --source libercoders/featurebench-specs_metaflow-instance_87a4ffa7 --tag ood-feature-metaflow:qualified --crane /path/to/crane --output /private/metaflow-image.json
python -m benchmarks.featurebench_qualify --tasks /private/task-list.json --images /private/image-map.json --output /private/new-controls
python -m benchmarks.featurebench_pilot --task /private/task.json --image ood-feature-metaflow:qualified --qualification /private/new-controls/qualification-results.json --output /private/new-paired-pilot --seed 20261007
```

On the larger workspace use full filesystem flattening first, without `--drop-caches`, and disclose the source/derived identity. `--drop-caches` is an optional recorded adaptation with link-payload preservation and additional qualification. The pilot refuses to run unless both gold and empty controls have the required classification/results. Images named “qualified” are just local tags; the name alone is not qualification.

Pinned model is `gpt-6.1-sol`, medium effort, CLI `0.159.0-alpha.3`, with 300-second per-arm ceilings and fresh ephemeral sessions. Model readiness must be rechecked in a replacement environment. No API key or paid API access is introduced. The adapter mounts the selected auth file without printing its contents. `OOD_CODEX_BINARY` can select the matching static Linux executable; a Node/npm shim is not sufficient for this container mount. The adapter uses platform proxy/CA trust, upstream API-only isolation, official masking and cleanup, and no Docker socket or host evaluator mount.

For the second manifest task use the Astropy image, seed 20261008, and new output directories. Preserve any infrastructure-invalid task and arm records; do not replace difficult or failed instances. Only publish sanitized aggregate results after reviewing logs for credentials. The container/MCP inference path remains untested, as clearly stated in the report.
