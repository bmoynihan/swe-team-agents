# GitHub Actions Security Checklist (quick)

## Token permissions
- [ ] Default `GITHUB_TOKEN` permissions restricted (read-only)
- [ ] Each job declares only what it needs (`jobs.<id>.permissions`)
- [ ] No accidental `write-all` / overly broad permissions

## Event safety
- [ ] No untrusted user input injected into `run:` blocks
- [ ] `pull_request_target` used only with strict controls (if used at all)

## Third-party actions & dependencies
- [ ] Third-party actions pinned to full commit SHA (or justified exception)
- [ ] No unpinned curl | bash install in CI
- [ ] Build provenance and artifacts reviewed

## Secrets
- [ ] Secrets only from GitHub Secrets / OIDC
- [ ] No secrets echoed to logs; add-mask used for non-secret sensitive values
- [ ] Rotation plan documented if exposure suspected

## Supply chain (optional)
- [ ] dependency-review-action enabled for PRs
- [ ] OpenSSF Scorecard scheduled / PR-triggered (if repo policy allows)


