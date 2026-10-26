---
tags:
  - plan
phase: 5
size: L
---

# M05 PSIRT

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M04 Remediation and Supply chain]] · ➡ **Next:** [[M06 Compliance CRA]]

*Product Security Incident Response: take in reports, run cases against SLAs and CRA clocks, publish advisories.*

## Pages
- `/psirt`: tabs **Operations · Triage board · Cases · Advisories · Playbooks · Collaboration**
- `/products/:product/psirt`: the product's cases

## Features
**Operations dashboard**
- KPIs: open cases, critical open, SLA overdue, waiting for triage, **CRA Art. 14 clocks**
- Quick actions: **New case · Vulnerability intake · Open cases for exploited CVEs · Assignment rules · SLA policies**

**Cases**
- Table: ID · Title · CVE(s) · Severity · Owner · SLA due · Status
- Status chips: Open · Overdue · Art. 14 overdue or due soon · Draft · Closed
- Case page: "Work this case", linked findings, timeline, back to PSIRT

**Triage board**
- Kanban of incoming reports → cases

**Playbooks**
- Step-by-step response templates (also searchable from Ctrl K)

**Advisories**
- Draft and publish security advisories (CSAF)

**Rules**
- Assignment rules (auto-owner by product/component)
- SLA policies (hours per severity; feeds [[M02 Vulnerabilities]] due dates)

## Data
PSIRT case · Intake report · Playbook · Advisory · Assignment rule · SLA policy

## Depends on
[[M03 Decisions and VEX]]

## Done when
- A report can go from intake → triage → case → advisory, with an owner at each step
- SLA and Art. 14 clocks count down and flag overdue cases
- Assignment rules give new cases an owner automatically

## Unknowns ⚠
- What the Triage board, Advisories, Playbooks and Collaboration tabs look like inside (tab names captured, content not)
