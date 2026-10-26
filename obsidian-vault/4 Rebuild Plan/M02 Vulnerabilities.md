---
tags:
  - plan
phase: 2
size: XL
---

# M02 Vulnerabilities

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M01 Products and SBOMs]] · ➡ **Next:** [[M03 Decisions and VEX]]

*Match every component version to known CVEs, rank the findings by real risk, and track them against SLAs.*

## Pages
- `/vulnerabilities`: cross-product view, tabs **Overview · By CVE · By fix · Remediation**
- `/products/:product/vulnerabilities`: per-product findings
- Finding detail drawer (opened with `?cve=`, also reachable from `?sev=`, `?kev=1`, `?component=` and `?q=` filters)

## Features
**Data pipeline (backend)**
- Scheduled sync of **NVD advisories, CISA KEV, FIRST EPSS, OSV**
- Matching engine: component + version → CVE, with match confidence and evidence
- Finding = CVE × component × build. SLA due date set from severity policy
- "Where findings come from" panel: count per source

**Lists**
- KPI tiles: Open CVEs · Open findings · Exploited (KEV) · Critical · Past SLA
- Severity bands with counts (Critical / High / Medium / Low / Not rated) → click to filter
- Table: CVE · Severity · CVSS · EPSS · KEV · Component · Fixed in · Status · Exposure · Owner · SLA due
- Filters: product, component@version, decision status (No decision · Affected · Investigating · Not affected · Fixed), severity, state, exploited only, fix available, past SLA; sort by Risk · Severity · EPSS · Due date
- "Act now" chip (KEV or EPSS ≥ 10%), bulk select, Assign owner, Import supplier VEX

**Finding detail drawer**
- TL;DR, Description, "Does this affect me?", "How do I fix it?", "How this score was reached"
- Component, Fix information, Affected builds, Blast radius, Related CVEs in this component
- Match evidence, Evidence trace, Discovery story, Threat context
- Action plan / Remediation plan, Decision chain, VEX statement (links to [[M03 Decisions and VEX]])
- Copy CVE id, previous/next finding, "Friday, work on it" (links to [[M09 Friday AI assistant]])

**By fix**
- Group findings by the upgrade that clears them (feeds [[M04 Remediation and Supply chain]])

## Data
CVE · Finding · SLA policy · Data source + run log · Exposure type (on device · over network · over cellular link)

## Depends on
[[M01 Products and SBOMs]]

## Done when
- Uploading an SBOM produces findings within minutes, with CVSS, EPSS and the KEV flag filled in
- The numbers on the dashboard, product and drawer views agree
- Every filter can be shared by URL (`?sev=critical`, `?kev=1`, `?component=curl`)
- SLA due dates are calculated and "past SLA" is flagged

## Unknowns ⚠
- The SLA policy rules (hours per severity) are set in PSIRT ([[M05 PSIRT]]). Their exact defaults are unknown
- How the risk score is calculated (the "How this score was reached" panel content was truncated)
