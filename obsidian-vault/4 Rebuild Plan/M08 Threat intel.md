---
tags:
  - plan
phase: 8
size: M
---

# M08 Threat intel

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M07 Reports]] · ➡ **Next:** [[M09 Friday AI assistant]]

*Show which real-world threats (campaigns, threat actors, exploits) touch your products.*

## Pages
- `/threat-intel`: tabs **Landscape · Actors · Graph · Watchlists · Sources**

## Features
- KPIs: active campaigns, actors linked to you, known exploited, threats to your products, feeds healthy
- "Threats to your products" table: CVE · Affected products · Why it matters · Source, with search
- Attack surface view
- Actors: threat actors and the CVEs they use
- Graph: actor → CVE → product
- Watchlists: follow CVEs, components or vendors
- Sources: feed list with health status

## Data
Threat actor · Campaign · Intel feed + health · Watchlist

## Depends on
[[M02 Vulnerabilities]] (needs findings to link threats to products)

## Done when
- Each threat shown is tied to at least one of the customer's own findings
- Watchlists send a notification when something new matches
- Feed health is visible, and a failing feed is flagged

## Unknowns ⚠
- Which intel feeds are used (only the CISA KEV source is confirmed)
- Content of the Actors, Graph and Watchlists tabs
