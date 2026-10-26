---
tags:
  - plan
phase: 10
size: M
---

# M10 Settings, Integrations, Policies

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M09 Friday AI assistant]] · 🏁 Last module

*Everything left over: the public trust portal, links to outside tools, and security policies.*

## Pages
- `/settings/trust-portal`: public page for customers ("Give a customer…")
- `/integrations` ⚠
- `/policies` ⚠
- Profile, company, members and MFA are already built in [[M00 Foundation]]

## Features
**Trust portal**
- Public, branded page showing chosen advisories, VEX, SBOMs and the CVD policy to customers

**Integrations** (likely, judging by references elsewhere in the app)
- Slack (seen: "Post deadline to Slack" on ENISA pages)
- Git repos / CI (Destro Gate, SBOM builder, Renovate bridge)
- Container registries (container scan)
- Email for supplier tasks and scheduled reports
- Ticketing (Jira etc.): assumed, not seen

**Policies**
- Security policies driving SLAs, gates and assignment (assumed, not seen)

## Data
Integration connection (type, credentials, status) · Trust portal config · Policy

## Depends on
[[M00 Foundation]]. Each integration is used by the module that needs it.

## Done when
- The trust portal publishes only what an Admin selects, at a public URL
- Each integration can be connected, tested and disconnected, and shows its status

## Unknowns ⚠
- `/integrations` and `/policies` contents were not captured, so this module needs a re-crawl before planning it in detail
