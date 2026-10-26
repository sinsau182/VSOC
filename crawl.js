
const { chromium } = require("playwright");
const fs = require("fs");
const { createObjectCsvWriter } = require("csv-writer");

const BASE = "https://app.destrosolutions.com/";
const ORIGIN = new URL(BASE).origin;
const MAX_PAGES = 1000;

const visited = new Map();
const queue = [{ url: BASE, source: "start" }];

function normalize(raw) {
  try {
    const u = new URL(raw, BASE);

    // Restrict crawl to the same origin.
    if (u.origin !== ORIGIN) return null;
    if (!["http:", "https:"].includes(u.protocol)) return null;

    // Remove fragments; preserve query parameters because
    // they may represent distinct application pages.
    u.hash = "";
    return u.href;
  } catch {
    return null;
  }
}

(async () => {
  if (!fs.existsSync("output/auth-state.json")) {
    throw new Error("Run login.js first.");
  }

  fs.mkdirSync("output", { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    storageState: "output/auth-state.json"
  });

  const page = await context.newPage();
  page.setDefaultTimeout(10000);

  while (queue.length && visited.size < MAX_PAGES) {
    const item = queue.shift();
    const url = normalize(item.url);

    if (!url || visited.has(url)) continue;

    const row = {
      url,
      discovered_from: item.source,
      title: "",
      status: "",
      page_type: "unknown",
      error: ""
    };

    visited.set(url, row);

    try {
      const response = await page.goto(url, {
        waitUntil: "domcontentloaded",
        timeout: 20000
      });

      await page.waitForTimeout(800);

      row.status = response?.status() ?? "";

      // Detect expired login/session redirects.
      if (
        /\/(login|signin|sign-in)(\/|$)/i.test(
          new URL(page.url()).pathname
        )
      ) {
        row.error = "Login required or session expired";
        continue;
      }

      row.url = page.url();
      row.title = await page.title();

      row.page_type = await page.evaluate(() => {
        const p = location.pathname.toLowerCase();
        if (p.includes("dashboard")) return "dashboard";
        if (p.includes("report")) return "report";
        if (p.includes("setting")) return "settings";
        return "application page";
      });

      // Collect links rendered in the current DOM.
      const links = await page.locator("a[href]").evaluateAll(
        anchors => anchors.map(a => ({
          href: a.href,
          text: (a.innerText || a.getAttribute("aria-label") || "")
            .trim().replace(/\s+/g, " ").slice(0, 200)
        }))
      );

      for (const link of links) {
        const next = normalize(link.href);
        if (next && !visited.has(next)) {
          queue.push({ url: next, source: url });
        }
      }
    } catch (err) {
      row.error = String(err.message).slice(0, 300);
    }

    // Be gentle to the application.
    await page.waitForTimeout(300);
  }

  const csv = createObjectCsvWriter({
    path: "output/url-inventory.csv",
    header: [
      { id: "url", title: "URL" },
      { id: "title", title: "PAGE TITLE" },
      { id: "status", title: "HTTP STATUS" },
      { id: "page_type", title: "PAGE TYPE" },
      { id: "discovered_from", title: "DISCOVERED FROM" },
      { id: "error", title: "ERROR" }
    ]
  });

  await csv.writeRecords([...visited.values()]);
  await browser.close();

  console.log(`Recorded ${visited.size} URLs.`);
  console.log("Inventory: output/url-inventory.csv");
})();
