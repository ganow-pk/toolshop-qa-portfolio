# Where we left off (2026-11-17)

## Done
- [x] Framework built: Playwright + Python + pytest, POM, config-driven (`config/settings.py`)
- [x] 17 tests (10 UI, 7 API), each tagged with an ISTQB technique (untagged tests block the run)
- [x] First run: 14/17 passed. Healed H-001 (locked demo account, switched to `customer2@`) and H-002 (search read the old list, now waits on the search response). Re-run: **17/17 passed**
- [x] Report: ISTQB technique + Healed columns
- [x] Report: screenshot embedded for each UI test (`REPORT_SCREENSHOTS` = all / failures / off)
- [x] Report: step-by-step log for each test (passwords never logged)

## Next
1. [x] Report shows screenshot + step log for each test (confirmed 2026-11-18). Healed H-003 (page-load timeout); confirmed 17/17 on re-run
2. [x] Locked-account "no error message": not reproduced on 2026-11-18 (account unlocked). Recorded in `docs/BUGS.md` under "Investigated, not reproduced"
3. [ ] Create a GitHub repo `toolshop-qa-portfolio` and push
4. [ ] GitHub: Settings → Pages → Source: **GitHub Actions**. Then run the "Tests" workflow
5. [ ] Replace `YOUR-GITHUB-USERNAME` in `README.md` (badge + report link)
6. [ ] Add the live report link to both resumes

## Ideas for later
- More tests: checkout flow (State Transition), registration form (Boundary Value Analysis on password rules)
- Run against `with-bugs.practicesoftwaretesting.com` to find and write up real defects
- Use `docs/TEST_DESIGN.md` as ISTQB exam study notes

## Commands
    pytest                         # all tests, headless
    pytest --headed --slowmo 500   # watch the browser
    pytest -m smoke                # smoke set only
    open report/index.html         # open the report (Mac)
