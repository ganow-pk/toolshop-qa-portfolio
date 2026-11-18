# Healing rules

"Healing" means repairing an automated test that fails for a reason that is **not** a product defect. These rules exist so that a green report always tells the truth.

## What may be healed
- **Test problems:** a wrong locator, a typo, a bad expectation about test data.
- **Setup problems:** a fixture that leaves the app in the wrong state.
- **Wait problems:** reading the page before the app has finished updating.
- **Data problems:** test data that changed on the shared environment.

## What may never be healed
- **Never loosen an assertion** to make a test pass. A weaker check that hides a real problem is a false pass.
- **Never "heal" a product bug.** If the product is wrong, the test stays red and the bug gets reported (see `.github/ISSUE_TEMPLATE/bug_report.md`).
- **Never harm a shared environment.** This suite runs against a public practice site that other people use. No tests that could lock shared accounts, delete shared data, or flood the server.

## How to heal
1. **Triage first.** Decide whether the cause is *tooling*, *data*, or *product*. Rule out tooling (re-run headed, re-run alone, check the trace) before calling it a product bug.
2. **At most two attempts per test.** If two honest fixes don't work, stop and investigate the product.
3. **Log every heal** in [`heal_log.md`](heal_log.md): spec, error, cause, change, result.
4. **Label the test** with `@pytest.mark.healed("H-00X")`. The HTML report shows the heal ID next to the result, so a healed pass is never presented as a clean pass.
