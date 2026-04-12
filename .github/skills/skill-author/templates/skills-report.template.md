# Skills Inventory Report

<!--
Purpose: human + machine-readable inventory of repo skills.
Rules:
- Keep human summary <= 12 lines.
- Then include EXACTLY ONE JSON object (SkillsReport) in a fenced code block.
-->

## Summary (≤12 lines)
- Status: <READY_FOR_QUALITY_GATE|BLOCKED>
- Skills scanned: <N>
- Validation: <pass|fail|not_run> (with evidence link or rationale)
- Notes: <key takeaways + any blockers>

```json
{
  "type": "SkillsReport",
  "status": "READY_FOR_QUALITY_GATE",
  "skills": [
    {
      "path": ".github/skills/<skill-name>/SKILL.md",
      "name": "<skill-name>",
      "purpose": "string",
      "recommendedAgents": ["team-lead", "skill-author"],
      "templatesUsed": [".github/templates/skill.template.md"],
      "scriptsIncluded": [".github/skills/<skill-name>/scripts/<file>"]
    }
  ],
  "templates": [
    { "path": ".github/templates/task-spec.template.md", "notes": "string" },
    { "path": ".github/templates/review-report.template.md", "notes": "string" },
    { "path": ".github/templates/skill.template.md", "notes": "Skill skeleton for new skills." }
  ],
  "validation": [
    {
      "check": "skill-frontmatter",
      "result": "pass",
      "evidence": "python3 .github/skills/skill-author/scripts/validate_skills.py"
    }
  ],
  "knownIssues": [
    {
      "category": "missing_paths|repo_convention_conflict|other",
      "evidence": "string",
      "nextStep": "string"
    }
  ],
  "notesToTeamLead": ["string"]
}
```


