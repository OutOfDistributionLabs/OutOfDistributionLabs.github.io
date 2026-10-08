# Reproducing the small pilot

Use Linux Docker with at least 6 GB of available space for the small image and isolated copies, plus the 1.1 GB pinned repository archive. The source benchmark is `https://github.com/microsoft/repoclassbench` at the manifest commit; Python task metadata is `data/input/python_data.json`. The upstream README links the repository archive, Google Drive file ID `1vWSxDldwIs2Bq9Mfeu6OnOQq3S1otfMv`. Verify the full manifest SHA256s before extraction. Extract only the two manifest issue repositories, safely rejecting archive traversal/symlinks and omitting Git history. Third-party repository licenses apply.

Keep full rows, reference classes, repositories with tests, and generated patches in private directories outside the agent mounts. This public bundle deliberately does not distribute hidden answers. The archive contains obfuscated names; do not replace it with upstream unmodified repositories.

The helper functions in `harnesses/small_repository.py` prepare the pinned Python base, mask a source view, run a class in hidden grading, and invoke a fresh API-only Codex container. Install the official MCP SDK/engine dependencies and the Docker SDK on the host. Network isolation uses the MIT-licensed FeatureBench Python utility at source commit `8d4e347ec57546685c5a87e8676bf575db022ea6`; only its proxy/bridge/container utility is reused, not FeatureBench task evaluation. The inference adapter requires the static `codex` and `codex-code-mode-host` binaries and an existing device-auth file. Mount only that selected authentication file; do not put it in images or repository files.

Run `prepare_runtime(base, output)` using the pinned `base` in runtime.json. Verify inventory differences before comparing outcomes; image IDs can differ on rebuild. Create both masked views with `masked_view(row, originals, output)` and make paths readable. Provision Pydicom evaluator fixture files from its published URL register; verify fixture SHA256s against fixtures.json. Keep them outside the agent view. Run each reference and empty class with `grade`; all reference required IDs must pass and neither empty class may resolve its task. Then run a fresh `infer(..., probe_only=True)` session and require a real MCP call and successful answer write.

The runner accepts private assets explicitly:

```sh
python -m benchmarks.repoclassbench_small \
  --rows /private/selected-rows.json \
  --originals /private/originals \
  --views /private/masked-views \
  --output /private/new-results
```

Use a new output directory. It enforces the frozen code hashes, control results and readiness. Before an independent reproduction, create a new project/freeze recording the rebuilt image and CLI identity instead of overwriting this experiment's evidence. Public results are descriptive because there are only two tasks. Source-evidence tool mode B is flat and C graph; A has no MCP configuration or shell adapter. Generated candidates are independently inserted and graded; hidden test feedback is not sent back to the agent. Cached token counters are retained, and cost is unknown.
