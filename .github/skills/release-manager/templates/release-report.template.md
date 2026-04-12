# Release Report

<!--
Fill this file as the Release Manager.
Rules:
- Start with a short human summary (≤12 lines).
- Then include exactly one JSON object of type ReleaseReport in a fenced code block.
- Keep claims evidence-backed (Task Spec / Patch Report / Test Report / diffs).
-->

## Summary (≤12 lines)
- Goal:
- Quality Gate:
- Recommended version:
- Changelog touched:
- Release notes ready:
- Rollout risk:
- Blockers (if any):

```json
{
  "type": "ReleaseReport",
  "status": "READY_FOR_HUMAN_RELEASE",
  "goal": "<from task-spec goal/summary>",
  "qualityGate": {
    "status": "PASS",
    "evidenceRef": "docs/agents/review-report.md"
  },
  "versioning": {
    "strategy": "semver",
    "recommendedNextVersion": "<e.g., 1.4.2>",
    "rationale": "<why this bump>"
  },
  "releaseNotesDraft": {
    "title": "<Release vX.Y.Z>",
    "highlights": [
      "<1–3 bullets>"
    ],
    "breakingChanges": [],
    "features": [],
    "fixes": [],
    "docs": [],
    "deprecations": [],
    "contributors": []
  },
  "rolloutPlan": [
    "1) Confirm CI is green and required approvals are present.",
    "2) Deploy to <env/stage>.",
    "3) Monitor <dashboards/alerts> for <signals> for <duration>.",
    "4) Gradually increase traffic / enable feature flag <flag>.",
    "5) Announce release in <channel>."
  ],
  "rollbackPlan": [
    "1) Disable <feature flag> (if applicable).",
    "2) Revert deployment to previous artifact/tag <tag>.",
    "3) If data migration was applied, execute rollback steps: <...>.",
    "4) Verify health checks and key user journeys."
  ],
  "releaseChecklist": [
    "Verify CHANGELOG/release notes match Task Spec and merged diff.",
    "Confirm version bump file(s) are updated (if repo requires).",
    "Tag the release using repo convention (e.g., vX.Y.Z).",
    "Create GitHub Release (paste release notes draft).",
    "Publish artifacts (if applicable).",
    "Post-release monitoring window completed.",
    "Document any follow-ups."
  ],
  "repoReleaseConfig": {
    "changelogPresent": true,
    "releaseYmlPresent": false,
    "notes": [
      "If using GitHub auto-generated release notes, consider adding .github/release.yml (see templates/release.yml.template.yml)."
    ]
  },
  "blockers": [],
  "followUps": [
    {
      "id": "F1",
      "summary": "Optional: align PR labels to release note categories to improve auto-generated notes.",
      "priority": "low"
    }
  ]
}
```

