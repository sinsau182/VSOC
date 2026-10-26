---
tags:
  - plan
phase: 7
size: M
---

# M07 Reports

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M06 Compliance CRA]] · ➡ **Next:** [[M08 Threat intel]]

*Ready-made reports from the platform's data, generated on demand or delivered on a schedule.*

## Pages
- `/reports`: sections **Generate a report · Produced · Scheduled deliveries**

## Features
**Report types seen**
| Report | Content |
|---|---|
| Executive Summary | Quarterly posture, severity cards (all products, last 90 days) |
| KEV Exposure | CISA KEV-listed CVEs in your fleet |
| SBOM Report | CycloneDX-shaped component inventory |
| VEX Export | CSAF-style VEX statements per CVE |
| Customer Disclosure | Per-customer CVE + VEX disclosure |
| PSIRT SLA | Per-case SLA policy and hours remaining |
| Supplier Risk | External suppliers, open CVEs |
| EU CRA Article 14 | Per-product / per-incident ENISA SRP filing |

- Options per report: product scope, period (30 / 90 days), confidentiality (Internal / Confidential)
- Produced reports list, with **Reopen scope**
- Scheduled deliveries (recurring send)

## Data
Report definition · Report run (file, scope, created by) · Schedule

## Depends on
Data from [[M01 Products and SBOMs]] to [[M06 Compliance CRA]]. **SBOM** and **VEX Export** can ship with the MVP.

## Done when
- Each report type generates a PDF or a machine-readable file (CycloneDX, CSAF) for any product scope
- Schedules run and deliver by email
- Produced reports stay available for download

## Unknowns ⚠
- Delivery channels for scheduled reports (email only? Slack?)
- What each report looks like when opened
