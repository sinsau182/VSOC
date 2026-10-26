---
tags:
  - plan
phase: 6
size: XL
---

# M06 Compliance CRA

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M05 PSIRT]] · ➡ **Next:** [[M07 Reports]]

*Guide the organisation through the EU Cyber Resilience Act and produce the evidence and ENISA reports it requires.*

This is the biggest module (22 pages). Build it in 4 parts:

## Part A — CRA dashboard and wizard
- `/compliance`: tabs **Overview · Dashboard · Security updates**, a **9-step wizard** (1 Product · 2 Scope · 3 Classification · 4 Risk · 5 Requirements · 6 Support & EOL · 7 Vuln & ENISA · 8 CE Marking · 9 Self-Assessment)
- KPIs: products in scope, open vulnerabilities, reports submitted, pending action; readiness by part, requirements met, evidence coverage
- Live Article 14 cases table: CVE · Product · Stage · Next deadline · Evidence
- **Generate Evidence Pack**, Reset, product filter
- Guided tools cards (Risk calculator, Cost calculator, Support period planner, Vulnerability analyzer, Compliance matrix, Asset & risk registry…)

## Part B — Assessments
- `/compliance/checklist`: **48-item checklist** (Annex I and Articles 11–32), status per item, owner, **Download report (PDF)**
- `/compliance/classification`: 6-step product classification (Scope Art 2 → Core function Art 7(1) → Annex III/IV → Standards Art 32(2) → Result), saved decision, version history
- `/compliance/gap-analysis`: 26 domains, 107 checks. Table: Organisation · Readiness · Gaps · Critical · Evidence
- `/compliance/templates`: 12 document templates (Technical documentation Annex VII, EU Declaration of Conformity, CVD policy, Incident response plan, Risk assessment, SBOM manifest, Secure development policy, Support period statement, Threat model, User security instructions, Vulnerability handling) with confidentiality levels and download

## Part C — ENISA reporting
- `/compliance/enisa/:product`: per-product ENISA report (7-point check, **Submit to ENISA**, post deadline to Slack)
- `/compliance/cra/srp`: ENISA Single Reporting Platform submission brief (fields by phase: 24h / 72h / 14 days)

## Part D — CRA library and tools
- **Learn (mostly static content):** `/compliance/cra` (overview, obligations by role, documents, timeline, penalties), `/cra/annexes` (Annex I–VIII), `/cra/articles` ⚠, `/cra/standards`, `/cra/timeline`, `/cra/raci` (who does what: manufacturer, importer, distributor, notified body, OSS steward), `/cra/open-source` (steward vs volunteer)
- **Operate (working tools):**
  - `/cra/sbom-builder`: CLI to build SBOMs (install, 3 scan modes, upload)
  - `/cra/container-scan`: submit a container image, list recent scans
  - `/cra/destro-gate`: block merges that introduce new vulnerabilities (repo install + blocking policy)
  - `/cra/license-risk`: licence families and CRA posture across OSS dependencies
  - `/cra/renovate-bridge`: show Renovate dependency-update PRs in PSOC
  - `/cra/early-signals`: fuzzer-found vulnerabilities before NVD (OSS-Fuzz)
  - `/cra/steward`: register an open-source steward project
  - `/cra/tools` ⚠

## Data
Compliance profile per product · Wizard answers · Checklist item status · Classification decision · Gap analysis · Document instance · Evidence item · ENISA submission · Container scan · Gate policy

## Depends on
[[M01 Products and SBOMs]], [[M03 Decisions and VEX]], [[M05 PSIRT]] (Article 14 cases)

## Done when
- A product can go through all 9 wizard steps and gets a readiness score
- The checklist, classification and gap analysis save and can be exported as PDF
- An evidence pack downloads with the technical file documents filled from product data
- An exploited vulnerability starts the 24h / 72h / 14-day ENISA clocks, and a submission can be prepared

## Unknowns ⚠
- `/cra/articles` and `/cra/tools` were not captured
- Whether ENISA submission is a real API integration or produces a file to upload by hand
- Part D tools (gate, container scan, SBOM builder) are separate products in themselves. Decide whether they're in scope
