// Allure 3 settings, read by `npx allure generate` / `npx allure open`.
// Usage: scripts/allure_report.sh (see README, "Allure report").
import { readFileSync } from "node:fs";

export default {
  name: "Toolshop QA Portfolio",
  output: "./allure-report",
  // Failure buckets. One file serves both Allure versions: conftest.py also copies
  // it into allure-results/categories.json for Allure 2. First match wins.
  categories: JSON.parse(
    readFileSync(new URL("./config/allure_categories.json", import.meta.url), "utf-8"),
  ),
  // ALLURE_SINGLE_FILE=1 packs the whole report into one index.html that opens
  // straight from disk (file://). Used by scripts/dashboard.sh and
  // scripts/publish_local_run.py --allure. Without it: the usual folder report.
  plugins: {
    awesome: { options: { singleFile: process.env.ALLURE_SINGLE_FILE === "1" } },
  },
};
