---
tags:
  - plan
phase: 3
size: L
---

# M03 Decisions and VEX

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M02 Vulnerabilities]] · ➡ **Next:** [[M04 Remediation and Supply chain]]

*Record the organisation's position on every finding (affected or not, and why) and publish it as VEX.*

## Pages
- `/decision/:finding`: "Security decision room", one per finding ⚠ (15 pages, content not captured)
- `/vex`: all VEX statements across products
- `/products/:product/vex`: per-product VEX, part of the product's tab group **VEX · PSIRT cases · Remediation · Exceptions · Playbooks**

## Features
**Decision room**
- One place to reach a decision on a finding: evidence, discussion, final status, sign-off
- Statuses: **Affected · Not affected · Fixed · Under investigation**, with a justification (the VEX justification codes)

**VEX statements**
- Table: CVE · Component · Status · Justification · State
- Lifecycle **Draft → review → Published**. "Draft the statement and open it for review"
- **New statement**, **Generate VEX** (one or "for all N" undecided)
- **Import supplier VEX** (a supplier's statements applied to matching findings)
- Filters: author, product, status, drafts/published, search
- KPIs: Decided X of Y, undecided, under investigation, drafts to review, published
- Due list: CVE · Owner · Due · Next step

**Exceptions**
- Accepted-risk exceptions with an owner and an expiry (tab exists, content not captured)

## Data
Decision · VEX statement (status, justification, state, author, version history) · Exception

## Depends on
[[M02 Vulnerabilities]]

## Done when
- Every finding can be given a status and justification, and the decision is shown everywhere that finding appears
- Statements move from draft to published with a reviewer
- VEX exports as **CycloneDX VEX** and **CSAF**, and supplier VEX imports and applies
- Each decision keeps a history of who changed what

## Unknowns ⚠
- The decision room's layout and workflow (only the "SECURITY DECISION ROOM" title was captured), so this needs a re-crawl
- Exceptions tab content
