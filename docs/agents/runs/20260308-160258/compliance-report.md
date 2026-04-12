# Compliance Report

## Summary
- **Status:** PASS / FAIL
- **Goal:** <!-- one sentence -->
- **Reviewed at:** <!-- ISO date/time -->
- **Reviewer:** compliance-officer
- **Ready for Quality Gate:** true / false

## License Posture
- **Repo license:** present / missing
  - Path: `<!-- LICENSE -->`
  - Notes: <!-- -->
- **Dependency license risk:** pass / fail / n/a
  - Notes:
    - <!-- new licenses introduced? unknown licenses? -->

## Third-Party Notices
- **Verdict:** pass / fail / n/a
- **Files:**
  - <!-- NOTICE, THIRD_PARTY_NOTICES.md -->
- **Notes:** <!-- -->

## Dependency Review Gate
- **Verdict:** pass / fail / not_configured
- **Workflow paths:**
  - `<!-- .github/workflows/dependency-review.yml -->`
- **Policy:**
  - Fail on severity: low/moderate/high/critical/unset
  - License policy: allow-list/deny-list/unset
- **Notes:** <!-- -->

## SBOM Posture (SPDX)
- **Verdict:** pass / fail / partial
- **How to generate:**
  - <!-- GitHub dependency graph export (SPDX JSON) or repo tooling -->
- **Notes:** <!-- coverage limitations, storage location -->

## SSDF Alignment Notes (engineering evidence)
- **Evidence artifacts:**
  - `docs/agents/task-spec.md`
  - `docs/agents/test-report.md`
  - `docs/agents/review-report.md`
- **Notes:** <!-- -->

## SLSA Provenance Notes (build provenance)
- **Current state:** none / partial / documented
- **Recommended next step:** <!-- -->
- **Notes:** <!-- -->

## Blockers
- **C1 — <category>:** <!-- license | notices | dependency-review | sbom | provenance | evidence | other -->
  - **Summary:** <!-- -->
  - **Evidence:** <!-- -->
  - **Recommended fix:** <!-- -->

## Non-blocking Findings
- **CN1:** <!-- -->

## Evidence
| Command / Check | Result | Notes |
|---|---|---|
| <!-- grep license files, workflow check, SBOM export instructions --> | pass/fail/not_run | <!-- --> |

---

## Machine-readable ComplianceReport (required)
```json
{
  "type": "ComplianceReport",
  "status": "PASS",
  "goal": "",
  "licensePosture": {
    "repoLicense": { "present": true, "path": "LICENSE", "notes": "" },
    "dependencyLicenseRisk": { "verdict": "not_applicable", "notes": [""] }
  },
  "thirdPartyNotices": {
    "verdict": "not_applicable",
    "files": [],
    "notes": [""]
  },
  "dependencyReviewGate": {
    "verdict": "not_configured",
    "workflowPaths": [],
    "policy": {
      "failOnSeverity": "unset",
      "licensePolicy": "unset",
      "notes": [""]
    }
  },
  "sbomPosture": {
    "verdict": "partial",
    "format": "SPDX",
    "howToGenerate": [""],
    "notes": [""]
  },
  "ssdfAlignmentNotes": {
    "evidenceArtifacts": ["docs/agents/task-spec.md", "docs/agents/test-report.md", "docs/agents/review-report.md"],
    "notes": [""]
  },
  "slsaProvenanceNotes": {
    "currentState": "documented",
    "recommendedNextStep": "",
    "notes": [""]
  },
  "blockers": [],
  "nonBlockingFindings": [
    { "id": "CN1", "summary": "", "recommendation": "" }
  ],
  "evidence": [
    { "commandOrCheck": "", "result": "not_run", "notes": "" }
  ],
  "readyForQualityGate": true
}
```


