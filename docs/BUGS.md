# Defects found

Defects found while testing are filed as GitHub issues using the [bug report template](../.github/ISSUE_TEMPLATE/bug_report.md) and listed here.

| Issue | Title | Environment | Severity | Found by | Status |
|-------|-------|-------------|----------|----------|--------|
| [#1](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/1) | Login form gives no feedback when the email is invalid and password is blank | with-bugs | Major (usability) | Automated test failure, confirmed by exploratory testing | Open |

## Investigated, not reproduced
| Date | Observation | Result |
|------|-------------|--------|
| 2026-11-18 | with-bugs build: after a successful login, the automated test saw the user menu read "User Data not found" instead of the user's name (failure screenshot). | Re-tested by hand the same day: the user's name showed normally. Possibly a brief loading state the test caught. Not filed. Watch for it in future runs. |
| 2026-11-17 / 18 | While the shared `customer@` demo account was locked (API: `423 Locked`), the login page appeared to show no error message (failure screenshot from H-001). | Re-tested by hand on 2026-11-18: the account had been unlocked and login succeeded, so the locked state could not be recreated. Not filed. Recheck if the account is locked again. |
