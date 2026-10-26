---
tags:
  - plan
phase: 4
size: L
---

# M04 Remediation and Supply chain

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M03 Decisions and VEX]] · ➡ **Next:** [[M05 PSIRT]]

*Plan the upgrades that clear vulnerabilities, chase suppliers, and see the supplier → component → product chain.*

## Pages
- `/products/:product/remediation`: upgrade plan
- `/vulnerabilities` → **Remediation** and **By fix** tabs
- `/products/:product/suppliers`: suppliers and parts for a product
- `/supply-chain` ⚠ (landing page, not captured) · `/supply-chain/graph` · `/supply-chain/suppliers/:supplier`
- CRA tools that belong here: `/compliance/cra/renovate-bridge`, `/compliance/cra/destro-gate` (see [[M06 Compliance CRA]])

## Features
**Remediation**
- Upgrade plan table: Upgrade · CVEs cleared · KEV cleared · Supplier · Owner · Status
- Chips: Clears KEV · No task yet · Supplier task · No fixed version
- Assign owner (a person or a team), **Draft supplier task**, search by component/supplier/CVE

**Supplier pages**
- Header: name, registered or not, security contact
- Actions: **Request SBOM · Notify about a CVE · Register supplier**
- Open CVEs on their components, KEV count, newest SBOM
- Products and components they supply
- Requests and answers (SBOM / VEX / security questionnaire), interface agreement, declared vs observed SBOM

**Product suppliers tab**
- Table: Supplier · Country · Components · Open CVEs · Known exploited · Open tasks · Last response

**Dependency graph**
- Supplier → component → product graph; line width = open CVEs on that path; exploited paths highlighted
- Views: Dependencies · Investigation

## Data
Remediation item · Supplier task / request · Supplier (registered profile, contact, agreement)

## Depends on
[[M03 Decisions and VEX]] (and the components and suppliers from [[M01 Products and SBOMs]])

## Done when
- Picking an upgrade shows exactly which CVEs and KEVs it clears
- A supplier task can be sent, tracked and answered, and the answer updates the finding or VEX
- The graph loads for every product and links to supplier and component pages

## Unknowns ⚠
- `/supply-chain` landing page
- How supplier tasks are delivered (email? portal?). The demo account showed "Supplier tasks could not be read"
