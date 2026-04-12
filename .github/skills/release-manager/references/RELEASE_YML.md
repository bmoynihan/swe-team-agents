# GitHub auto-generated release notes (.github/release.yml) quick reference

GitHub can generate release notes for a GitHub Release and supports optional configuration via `.github/release.yml`.

## Key config fields (YAML)
- `changelog.exclude.labels`: PR labels to omit entirely from notes
- `changelog.exclude.authors`: GitHub usernames/bots to omit entirely
- `changelog.categories[*].title`: section title
- `changelog.categories[*].labels`: labels that route PRs into that section (`"*"` is the required catch-all)
- `changelog.categories[*].exclude.labels` / `exclude.authors`: per-category exclusion

## Notes
- Keep categories aligned with your repo label taxonomy.
- Prefer a small set of stable categories; don’t churn labels for aesthetics.
- If you add `.github/release.yml`, it should be on the default branch before you rely on it for future releases.


