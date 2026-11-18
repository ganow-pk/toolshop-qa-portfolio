# Defects found

Defects found while testing are filed as GitHub issues using the [bug report template](../.github/ISSUE_TEMPLATE/bug_report.md) and listed here.

| Issue | Title | Severity | Found by | Status |
|-------|-------|----------|----------|--------|
| | | | | |

## Investigated, not reproduced
| Date | Observation | Result |
|------|-------------|--------|
| 2026-11-17 / 18 | While the shared `customer@` demo account was locked (API: `423 Locked`), the login page appeared to show no error message (failure screenshot from H-001). | Re-tested by hand on 2026-11-18: the account had been unlocked and login succeeded, so the locked state could not be recreated. Not filed. Recheck if the account is locked again. |
