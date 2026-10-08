# Functional qualification

The adapted runtime is 516 MB. Gold/reference: Pydicom 13/13; Requests 44/44. Empty classes: Pydicom 1/13; Requests 0/44. Neither empty class resolves its task. Required IDs, including missing/skipped/error outcomes, define the all-pass endpoint.

Pydicom collection initially timed out attempting downloads. The evaluator now has pinned test fixtures fetched from the repository URL register, checked against its hash register where downloads were needed. Fixtures remain evaluator-only. Docker image configuration was sanitized to remove inherited proxy variables and bind-file volumes. Source files are made readable in containers. No setup failure is treated as agent failure.

Adaptations: Python 3.11 rather than official Conda; retained imports; no linter or iterative hidden-test feedback. This is not an official leaderboard result. Network-isolation and real MCP/agent readiness are the next gate.

Isolation/readiness passed: fresh CLI completed, wrote READY, and one successful MCP status call was logged. Native MCP subprocesses require explicit PYTHONPATH; the portable shell adapter sets it. Mounted static CLI helper is required by this CLI version. Agent containers retain DAC_OVERRIDE to read mounted source/auth and network bridge files, but have no host evaluator or Docker mount.
