/**
 * DestroSolutions app crawler
 *
 * Visits every in-app page reachable from the home page using a saved
 * login session, and records what each page shows: headings, links,
 * buttons, form fields, tables and visible text. It never submits forms
 * or presses action buttons; it only opens menus and view tabs.
 *
 * Usage:  node login.js      (once, to save the session)
 *         node crawl-all.js
 *
 * Output (output/full-crawl):
 *   pages.json / pages.csv        one row per page
 *   features.json / features.csv  one row per UI element or tab view
 *   errors.json                   pages that failed to load
 */

const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

// ---------------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------------

const BASE = "https://app.destrosolutions.com/";
const ORIGIN = new URL(BASE).origin;
const AUTH = "output/auth-state.json";
const OUT = "output/full-crawl";

const MAX_PAGES = 1500;
const MAX_UI_CLICKS_PER_PAGE = 30;
const MAX_FILTER_VARIANTS = 2;   // e.g. keep 2 of the many ?cve=... views

// Pages that load but show an error message instead of content.
const ERROR_TEXT =
  /isn't part of the demo dataset|could not be (loaded|read)|couldn't load|failed to load/i;

// Labels the crawler must never click.
const UNSAFE_LABEL = /delete|remove|logout|sign out|save|submit|approve|send/i;

fs.mkdirSync(OUT, { recursive: true });

// ---------------------------------------------------------------------------
// Crawl state
// ---------------------------------------------------------------------------

const queue = [{ url: BASE, source: "start" }];
const queued = new Set([BASE]);
const visited = new Map();     // requested URL -> page record
const captured = new Set();    // final URLs already recorded
const variants = new Map();    // filter pattern -> count
const features = [];
const errors = [];

// ---------------------------------------------------------------------------
// URL helpers
// ---------------------------------------------------------------------------

function normalize(raw) {
  try {
    const u = new URL(raw, BASE);

    if (u.origin !== ORIGIN) return null;
    if (!["http:", "https:"].includes(u.protocol)) return null;

    u.hash = "";

    // Skip files and destructive routes.
    if (/\.(png|jpe?g|gif|svg|webp|pdf|zip|css|js|woff2?)(\?|$)/i.test(u.href)) return null;
    if (/\/(logout|signout|delete)(\/|$)/i.test(u.pathname)) return null;

    return u.href;
  } catch {
    return null;
  }
}

// Same path + same query keys = same screen with another filter value.
// The "tab" value stays in the pattern because each tab is its own view.
function filterPattern(href) {
  const u = new URL(href);
  const keys = [...u.searchParams.keys()].sort();
  if (keys.length === 0) return null;
  return `${u.pathname}?${keys.join("&")}|${u.searchParams.get("tab") || ""}`;
}

function addUrl(raw, source) {
  const url = normalize(raw);
  if (!url || visited.has(url) || queued.has(url) || captured.has(url)) return;

  const pattern = filterPattern(url);
  if (pattern) {
    const count = variants.get(pattern) || 0;
    if (count >= MAX_FILTER_VARIANTS) return;
    variants.set(pattern, count + 1);
  }

  if (queue.length + visited.size < MAX_PAGES) {
    queue.push({ url, source });
    queued.add(url);
  }
}

// ---------------------------------------------------------------------------
// Page helpers
// ---------------------------------------------------------------------------

// Wait until the page text stops changing, so pages are not saved half-rendered.
async function waitForContent(page) {
  await page.waitForLoadState("networkidle", { timeout: 8000 }).catch(() => {});

  let lastLength = -1;
  for (let i = 0; i < 16; i++) {
    const length = await page
      .evaluate(() => document.body.innerText.length)
      .catch(() => 0);

    if (length > 0 && length === lastLength) return;
    lastLength = length;
    await page.waitForTimeout(500);
  }
}

function captureQuality(text) {
  if (!text) return "empty";
  if (text.length < 2000 && ERROR_TEXT.test(text)) return "error message";
  return "ok";
}

async function inspectPage(page) {
  return page.evaluate(() => {
    const clean = value => (value || "").replace(/\s+/g, " ").trim();

    const visible = el => {
      const style = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.display !== "none" &&
        style.visibility !== "hidden" &&
        rect.width > 0 && rect.height > 0;
    };

    const describe = el => ({
      tag: el.tagName.toLowerCase(),
      text: clean(
        el.innerText ||
        el.getAttribute("aria-label") ||
        el.getAttribute("title") ||
        el.getAttribute("placeholder") ||
        ""
      ).slice(0, 250),
      role: el.getAttribute("role"),
      ariaLabel: el.getAttribute("aria-label"),
      href: el.tagName === "A" ? el.href : "",
      placeholder: el.getAttribute("placeholder"),
      type: el.getAttribute("type"),
      disabled: Boolean(el.disabled)
    });

    const elements = selector =>
      [...document.querySelectorAll(selector)].filter(visible).map(describe);

    const tables = [...document.querySelectorAll("table")]
      .filter(visible)
      .map((table, index) => ({
        tableIndex: index,
        headers: [...table.querySelectorAll("th")].map(th => clean(th.innerText)),
        rowCount: table.querySelectorAll("tbody tr").length
      }));

    return {
      url: location.href,
      title: document.title,
      headings: elements("h1,h2,h3,h4,[role=heading]"),
      navigation: elements(
        "nav a,nav button,aside a,aside button," +
        "[role=navigation] a,[role=navigation] button"
      ),
      links: elements("a[href]"),
      buttons: elements("button,[role=button],[role=tab],[role=menuitem]"),
      fields: elements("input,select,textarea,[role=combobox]"),
      tables,
      visibleText: clean(document.body.innerText).slice(0, 12000)
    };
  });
}

// Open collapsed menus inside navigation only. Never click other buttons.
async function expandSafeNavigation(page) {
  const selector = [
    "nav button[aria-haspopup]",
    "aside button[aria-haspopup]",
    "[role=navigation] button[aria-haspopup]",
    "nav button[aria-expanded='false']",
    "aside button[aria-expanded='false']",
    "[role=navigation] button[aria-expanded='false']"
  ].join(",");

  const count = Math.min(await page.locator(selector).count(), MAX_UI_CLICKS_PER_PAGE);

  for (let i = 0; i < count; i++) {
    try {
      const button = page.locator(selector).nth(i);
      if (!(await button.isVisible())) continue;

      const label = (await button.innerText().catch(() => "")).trim();
      if (UNSAFE_LABEL.test(label)) continue;

      await button.click({ timeout: 1500 });
      await page.waitForTimeout(200);
    } catch {
      // Menu could not be opened; move on.
    }
  }
}

// Click each view tab and record what it shows.
async function inspectTabs(page) {
  const count = Math.min(await page.locator('[role="tab"]').count(), MAX_UI_CLICKS_PER_PAGE);

  for (let i = 0; i < count; i++) {
    try {
      const tab = page.locator('[role="tab"]').nth(i);
      if (!(await tab.isVisible()) || !(await tab.isEnabled())) continue;
      if ((await tab.getAttribute("aria-selected")) === "true") continue;

      const label = (await tab.innerText().catch(() => "")).trim();
      if (UNSAFE_LABEL.test(label)) continue;

      await tab.click({ timeout: 1500 });
      await waitForContent(page);

      const snapshot = await inspectPage(page);

      features.push({
        url: snapshot.url,
        pageTitle: snapshot.title,
        featureType: "tab view",
        label,
        capture: captureQuality(snapshot.visibleText),
        headings: snapshot.headings,
        buttons: snapshot.buttons,
        fields: snapshot.fields,
        tables: snapshot.tables,
        visibleText: snapshot.visibleText
      });

      // Some tabs change the URL; crawl that URL as a page too.
      addUrl(snapshot.url, page.url());
      for (const link of snapshot.links) addUrl(link.href, snapshot.url);
    } catch {
      // Tab not interactable; move on.
    }
  }
}

// Turn a page snapshot into one feature row per UI element.
function recordFeatures(record, snapshot) {
  const base = { url: record.url, pageTitle: record.title };

  for (const h of snapshot.headings) {
    features.push({ ...base, featureType: "heading", label: h.text, element: h.tag });
  }
  for (const n of snapshot.navigation) {
    features.push({ ...base, featureType: "navigation", label: n.text, element: n.tag, targetUrl: n.href });
  }
  for (const b of snapshot.buttons) {
    features.push({ ...base, featureType: b.role === "tab" ? "tab" : "control", label: b.text, element: b.tag, role: b.role });
  }
  for (const f of snapshot.fields) {
    features.push({ ...base, featureType: "form field", label: f.text || f.placeholder, element: f.tag, placeholder: f.placeholder });
  }
  for (const t of snapshot.tables) {
    features.push({ ...base, featureType: "table", label: t.headers.join(" | "), rowCount: t.rowCount });
  }
}

// ---------------------------------------------------------------------------
// Output helpers
// ---------------------------------------------------------------------------

function csvEscape(value) {
  if (value === null || value === undefined) return "";
  const text = typeof value === "string" ? value : JSON.stringify(value);
  return '"' + text.replace(/"/g, '""') + '"';
}

function writeCsv(file, rows, columns) {
  const lines = [
    columns.map(csvEscape).join(","),
    ...rows.map(row => columns.map(col => csvEscape(row[col])).join(","))
  ];
  fs.writeFileSync(file, "﻿" + lines.join("\r\n"), "utf8");
}

function saveProgress() {
  fs.writeFileSync(path.join(OUT, "pages.json"), JSON.stringify([...visited.values()], null, 2));
  fs.writeFileSync(path.join(OUT, "features.json"), JSON.stringify(features, null, 2));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

(async () => {
  if (!fs.existsSync(AUTH)) {
    throw new Error(`Missing ${AUTH}. Run node login.js first.`);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ storageState: AUTH });
  const page = await context.newPage();
  page.setDefaultTimeout(8000);

  while (queue.length > 0 && visited.size < MAX_PAGES) {
    const item = queue.shift();
    const url = normalize(item.url);
    if (!url || visited.has(url)) continue;

    const record = {
      url,
      requestedUrl: url,
      discoveredFrom: item.source,
      title: "",
      status: "",
      capture: "",
      pageType: "application page",
      headings: [],
      navigation: [],
      links: [],
      buttons: [],
      fields: [],
      tables: [],
      visibleText: "",
      error: ""
    };

    visited.set(url, record);
    console.log(`[${visited.size}] ${url}`);

    try {
      const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 25000 });
      await waitForContent(page);

      const current = new URL(page.url());
      record.status = response?.status() ?? "";

      if (current.origin !== ORIGIN) {
        record.error = "Redirected outside application origin";
        continue;
      }
      if (/\/(login|signin|sign-in)(\/|$)/i.test(current.pathname)) {
        record.error = "Login required or session expired";
        continue;
      }

      // A redirect (e.g. /tara -> /products) is kept under the requested
      // URL; if the final page was already captured, don't capture it again.
      const finalUrl = normalize(current.href) || current.href;
      record.url = finalUrl;
      if (captured.has(finalUrl)) {
        record.capture = "duplicate (redirect)";
        continue;
      }
      captured.add(finalUrl);

      await expandSafeNavigation(page);

      const snapshot = await inspectPage(page);
      Object.assign(record, snapshot, { url: finalUrl });
      record.capture = captureQuality(snapshot.visibleText);

      for (const link of snapshot.links) addUrl(link.href, record.url);

      recordFeatures(record, snapshot);
      await inspectTabs(page);
    } catch (error) {
      record.error = String(error.message).slice(0, 300);
      errors.push({ url, error: record.error });
    }

    saveProgress();
    await page.waitForTimeout(400);
  }

  // Final files
  const pages = [...visited.values()];
  saveProgress();

  writeCsv(path.join(OUT, "pages.csv"), pages, [
    "url", "requestedUrl", "title", "status", "capture", "discoveredFrom", "pageType", "error"
  ]);
  writeCsv(path.join(OUT, "features.csv"), features, [
    "url", "pageTitle", "featureType", "label", "capture", "element", "role", "targetUrl", "placeholder", "rowCount"
  ]);
  fs.writeFileSync(path.join(OUT, "errors.json"), JSON.stringify(errors, null, 2));

  await browser.close();

  // Summary
  const tally = {};
  for (const p of pages) tally[p.capture || "failed"] = (tally[p.capture || "failed"] || 0) + 1;

  console.log("\nCrawl complete.");
  console.log(`Pages inspected:      ${pages.length}`);
  console.log(`Capture quality:      ${JSON.stringify(tally)}`);
  console.log(`Feature observations: ${features.length}`);
  console.log(`Output folder:        ${OUT}`);
})();
