---
tags:
  - plan
phase: 1
size: XL
---

# M01 Products and SBOMs

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M00 Foundation]] · ➡ **Next:** [[M02 Vulnerabilities]]

*Register products, upload their software bills of materials, and see what each product is made of.*

## Pages
- `/products`: list with tabs **Products · SBOMs · TARA**
- `/products/:product`: product page with 8 tabs: **Overview · Product design · Software · Vulnerabilities · Decisions · Field · Releases · Compliance**
- `/products/:product/overview` · `/components` · `/sources` · `/releases` · `/suppliers`
- Product design sub-tabs: `/requirements` · `/threat-model` · `/verification-plan` · `/verification-records` (architecture, requirements, threat model, verification)
- `/products/firmware` ⚠ · `/products/:product/activity` ⚠

## Features
**Product list**
- Table: Product · Version · Category · Open CVEs · Exploited · Critical · Components · Suppliers · Deployments · Actions
- Summary line ("4 products · 20 open CVEs · 6 exploited"), search by name/version/owner
- **Register product**, **Upload SBOM**

**Product page**
- Header: name, version ("v2.7.0 latest"), version switcher, **Add scan · Edit details · Export**
- Product information card: developed by, department, manufacturer, category, sector, CRA class, release date, support end
- Overview tiles: risk score, open vulnerabilities, known exploited, fix available, VEX decided, change since last version, risk over time, data sources and their last run
- Activity/event log: When · Type · Event · By

**Software (components)**
- Sub-tabs **All components · Dependencies · Licences**
- Table: Component · Type · Supplier · Licence · Open CVEs; chips "With CVEs", "Fix available", "Known exploited"
- Stats: % open source, % exposed, top licences

**Sources (SBOM imports)**
- Table: File · Format · Hash · Date · By · Components
- Parse **CycloneDX** and **SPDX**; integrity check; supplier SBOMs; firmware uploads

**Releases**
- Release record: status, SBOM date, support end, component / open CVE / KEV / past-SLA counts
- Release log, links to CRA documents and TARA

**Product design**
- Requirements: add, import
- Threat model: risk matrix, **Import TARA**, open full TARA
- Verification plan and records (controls, reports, audit trail)

## Data
Product · Release · SBOM source · Component · Supplier (auto-created from SBOM metadata) · Requirement · Threat (TARA) · Verification record · Event log

## Depends on
[[M00 Foundation]]

## Done when
- Registering a product and uploading a CycloneDX or SPDX SBOM fills its component list
- Suppliers named in the SBOM appear automatically
- Each release keeps its own component snapshot, and the version switcher changes the data shown
- Edit details and Export work, and every change shows in the activity log

## Unknowns ⚠
- **Field** tab (deployments), **Decisions** tab, and the Firmware and Activity pages were not captured
- Requirements, Verification plan and Verification records showed "isn't part of the demo dataset", so their layout is unknown
- What "Add scan" scans (source repo? binary? container?)
