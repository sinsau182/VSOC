const { chromium } = require("playwright");
const fs = require("fs");

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto("https://app.destrosolutions.com/");

  console.log("Log in manually, complete MFA if needed,");
  console.log("and navigate to an authenticated dashboard.");

  await page.waitForTimeout(120000);

  fs.mkdirSync("output", { recursive: true });
  await context.storageState({
    path: "output/auth-state.json"
  });

  await browser.close();
})();