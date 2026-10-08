# Official evaluator qualification

Dataset: LiberCoders/FeatureBench v1.1 Fast, revision `76b4a4566e04f4bcc13c35125d4f301791efa736`, 100 rows. Official harness commit `8d4e347ec57546685c5a87e8676bf575db022ea6`, MIT license. Two lv1 instances selected by fixed lexicographic distinct-repository rule before agent outcomes; see manifest.

Initial official image pulls exhausted most of 32 GB because VFS copies cumulative filesystems at each layer. Cancelled both pulls; cancelled layers were reclaimed. Importing the pinned merged image filesystems into single-layer derived images preserves filesystem data and selected runtime configuration, but changes image identity. Source/derived digests will be recorded. Official gold and empty-patch grading are mandatory. No grades or agent outcomes yet.

Agent preparation uses upstream masking, removal of pristine `/root/my_repo`, removal of F2P files, bytecode cleanup and fresh git history. Separate evaluator containers hold hidden test patches. Agent containers receive no evaluator files, Docker socket, host workspace, or prior-arm outputs. Restrict inference-time networking to exact model API origins using the upstream Unix-socket proxy, chained through the platform proxy. Probe access boundaries before each arm. Authentication uses a selected credential path without exposing its contents.

Sentinel: runtime qualification incomplete. Authentication is now working, but reference scoring and isolation checks must pass before agents execute.

The complete merged Metaflow image finished at 17.7 GB, exceeding the practical image-plus-VFS-container envelope. It was removed after recording provenance. A second derived import excludes only `/opt/miniconda3/pkgs`, `/root/.cache` and original `/root/my_repo/.git`; active environments/source/tests remain. Retained links into removed caches are checked, and official gold grading decides runtime validity. This additional deviation precludes exact leaderboard infrastructure parity.

Final runtime gate: HOLD. The compact import completed, but both official control containers failed to create due to storage exhaustion. Tests never ran; normalized resolution is null. No agents ran. See the qualification results and report. Authentication is working. Registered task images/containers were removed; managed environment recovery and more storage are required.
