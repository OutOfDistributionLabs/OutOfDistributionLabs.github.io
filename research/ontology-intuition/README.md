# Hierarchical abstractions & agent intuition

This folder is the public home for one research programme: ontology graphs and hierarchical abstractions for software agents, including the intuition engine and its evaluations.

`index.html` presents published white papers first, followed by the **Auto research** progress section. `project.json` is the programme register: add publications and tasks here. Existing task folders retain their original URLs and reproducibility artifacts; they are members of this programme, not separate research programmes. Each task's `research.json` points back here with `parent_project`.

To rebuild the page:

```sh
python tools/research/build_hub.py --project ontology-intuition
```

The reusable publisher rebuilds and commits the parent page alongside each task checkpoint or heartbeat. Browser progress checks run every 60 seconds while the page is visible, using each task's existing `status.json`. This does not start research runs or notifications. Without JavaScript or during connection failures, the last published status remains visible.

Add future subtasks to the register, create their ordinary research publisher configuration, and set `parent_project` to `ontology-intuition`. White papers link directly to PDFs and their task progress; task progress pages link back to this programme. Distinguish a completed protocol or study from proof of the programme's broader hypothesis.

Design verification: responsive layouts at 320, 390, 844 and 1440 pixels; home Research/Close/Escape controls; all publication/progress links and return links; simulated live status and unavailable-status fallback; JavaScript-disabled content. Seven publisher workflow tests pass, including parent-page regeneration and checkpoint publication. Mobile and desktop screenshots were visually reviewed.
