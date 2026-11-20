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
};
