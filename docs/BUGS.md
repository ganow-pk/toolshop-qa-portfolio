# Defects found

The full list of findings, including minor and cosmetic ones, is in each [exploratory session report](exploratory/).
Defects found while testing are filed as GitHub issues using the [bug report template](../.github/ISSUE_TEMPLATE/bug_report.md) and listed here.

| Issue | Title | Environment | Severity | Found by | Status |
|-------|-------|-------------|----------|----------|--------|
| [#1](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/1) | Login form gives no feedback when the email is invalid and password is blank | with-bugs | Major (usability) | Automated test failure, confirmed by exploratory testing | Open |
| [#2](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/2) | Price range slider does not filter the product list | with-bugs | Major | Exploratory (Session 02), independent | Open |
| [#3](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/3) | Categories menu shows an "Undefined" entry that lists no products | with-bugs | Major | Exploratory (Session 02), independent | Open |
| [#4](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/4) | Update Profile fails with "resource not found" | with-bugs | Major | Exploratory (Session 02), independent | Open |
| [#5](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/5) | Changing the password locks the user out of their account | with-bugs | Critical | Exploratory (Session 02), guide hunt #21 | Open |
| [#6](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/6) | Sorting is reversed for every sort option | with-bugs | Major | Exploratory (Session 02), extends guide hunt #6 | Open |
| [#7](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/7) | Contact form: attachment help text lists formats that are then rejected | with-bugs | Major | Exploratory (Session 02), extends guide hunt #23 | Open |

## Investigated, not reproduced
| Date | Observation | Result |
|------|-------------|--------|
| 2026-11-18 | with-bugs build: after a successful login, the automated test saw the user menu read "User Data not found" instead of the user's name (failure screenshot). | Re-tested by hand the same day: the user's name showed normally. Possibly a brief loading state the test caught. Not filed. Watch for it in future runs. |
| 2026-11-17 / 18 | While the shared `customer@` demo account was locked (API: `423 Locked`), the login page appeared to show no error message (failure screenshot from H-001). | Re-tested by hand on 2026-11-18: the account had been unlocked and login succeeded, so the locked state could not be recreated. Not filed. Recheck if the account is locked again. |
