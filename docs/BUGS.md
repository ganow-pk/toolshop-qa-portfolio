# Defects found

The full list of findings, including minor and cosmetic ones, is in each [exploratory session report](exploratory/).
Defects found while testing are filed as GitHub issues using the [bug report template](../.github/ISSUE_TEMPLATE/bug_report.md) and listed here.

| Issue | Title | Environment | Severity | Found by | Status |
|-------|-------|-------------|----------|----------|--------|
| [#1](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/1) | Login form gives no feedback when the email is invalid and password is blank | with-bugs | Major (usability) | Automated test failure, confirmed by exploratory testing | Open |
| [#2](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/2) | Price range slider does not filter the product list | with-bugs | Major | Exploratory (Session 02), independent | Open |
| [#3](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/3) | Category filter shows an "Undefined" entry that lists no products | with-bugs | Major | Exploratory (Session 02), independent | Open |
| [#4](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/4) | Update Profile fails with "resource not found" | with-bugs | Major | Exploratory (Session 02), independent | Open |
| [#5](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/5) | Changing the password locks the user out of their account | with-bugs | Critical | Exploratory (Session 02), guide hunt #21 | Open |
| [#6](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/6) | Sorting is reversed for every sort option | with-bugs | Major | Exploratory (Session 02), extends guide hunt #6 | Open |
| [#7](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/7) | Contact form: attachment help text lists formats that are then rejected | with-bugs | Major | Exploratory (Session 02), extends guide hunt #23 | Open |
| [#8](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/8) | Quantity + / − buttons on the product page do nothing | with-bugs | Major | Exploratory (Session 02), guide hunt #7; automated test | Open |
| [#9](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/9) | Cart badge stays at 1 after adding the same product a second time | with-bugs | Major | Exploratory (Session 02), independent; automated test | Open |
| [#10](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/10) | Add to favourites shows an error and adds nothing | with-bugs | Major | Exploratory (Session 02), guide hunt #7 | Open |
| [#11](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/11) | "Home" link in the top navigation opens the Contact page | with-bugs | Major | Exploratory (Session 02), guide hunt #15 | Open |
| [#12](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/12) | User menu shows "User Data not found" instead of the user's name after login | with-bugs | Minor | Automated test failure, confirmed by exploratory testing (Session 02, guide hunt #11) | Open |
| [#15](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/15) | Registration: password error says "minimal 6 characters" but the rule is 8 | **main** | Minor | Automated test failure (Error Guessing), confirmed by hand | Open |

## Investigated, not reproduced (or reproduced later)
| Date | Observation | Result |
|------|-------------|--------|
| 2026-11-17 / 18 | While the shared `customer@` demo account was locked (API: `423 Locked`), the login page appeared to show no error message (failure screenshot from H-001). | Re-tested by hand on 2026-11-18: the account had been unlocked and login succeeded, so the locked state could not be recreated. Not filed. Recheck if the account is locked again. |
