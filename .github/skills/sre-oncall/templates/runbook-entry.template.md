# Runbook — <service/system> — <scenario>

**Last updated:** <YYYY-MM-DD>

## Symptoms
- <what users see>
- <what alerts show>

## First 5 minutes (stabilize)
1. Confirm impact scope (who/what is affected).
2. Check recent deploys / feature flags / migrations relevant to this change.
3. Check Golden Signals (latency, traffic, errors, saturation).
4. Apply the safest **generic mitigation** available (stop the bleeding):
   - disable the feature flag / revert config toggle
   - roll back the last deploy (if clearly correlated and safe)
   - shed load / rate limit / drain a bad region (if supported)

## Triage flow (decision points)
- Is the issue isolated to a subset of endpoints/tenants/regions?
- Is the issue correlated with a deploy, config change, or dependency event?
- Is it a correctness error (wrong output), availability error (5xx/timeouts), or performance regression?

## Diagnosis (quick checks)
- Logs: <what to search for>
- Metrics: <what charts/counters matter>
- Traces: <what spans/services to inspect>

## Mitigations
- <mitigation 1>
- <mitigation 2>

## Rollback
- <exact rollback steps from Task Spec, with links to scripts/docs>

## Escalation
- Page/notify: <team/alias> when <condition>
- If data/privacy risk: include security/privacy escalation path

## Comms (status update snippet)
Use `templates/status-update.template.md`.


