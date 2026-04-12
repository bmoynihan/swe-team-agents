# Maintainer Notes

This repository keeps live agent artifacts under `docs/agents/`.

The active run pointer lives at `docs/agents/current-run.json`.
Each active run snapshot lives under `docs/agents/runs/<run-id>/`.
Hook audit logs are written only under `docs/agents/runs/<run-id>/hook-audit/`.

The Team Lead helpers bootstrap and validate the shared working set in `docs/agents/` and then sync that state into the active run folder.


