---
tags:
  - plan
phase: 0
size: L
---

# M00 Foundation

⬆ **Back:** [[REBUILD PLAN]] · ➡ **Next:** [[M01 Products and SBOMs]]

*Login, accounts, roles and the app shell that every page sits in.*

## Pages
- Login (seen by the crawler's login script, not in the crawl)
- App shell on every page: [[Global shell]]
- `/settings` (profile + company) · `/settings/members` · `/settings/mfa`

## Features
**Auth & accounts**
- Email login, session handling
- Two-factor authentication with an authenticator app (TOTP)
- Organisation (company name, logo, website, country)
- Profile (photo, name, job title), "Start tour" onboarding

**Team & roles**
- Members table: Member · Role · Status · Joined · Actions
- Invite member / generate invite link
- Roles: **Admin · Analyst · Viewer**, enforced on every API call

**App shell**
- Sidebar in 3 groups: Main (Home, Products, Friday) · Security (Vulnerabilities, Threat intel, PSIRT, Supply chain, Compliance) · Workspace (Reports, Integrations, Settings); collapsible
- Top bar: global search (Ctrl K) over products, CVEs and playbooks · notifications · dark/light theme · user menu
- Breadcrumbs, "Data as of …" freshness stamp
- Slot for the Friday side panel (filled in [[M09 Friday AI assistant]])

**Shared UI kit** (used by every later module)
- Data table: sort, search, pagination (25/50/100), row select, bulk actions
- Global **product filter** dropdown ("All products / TCU-200 / …")
- KPI tiles, filter chips with counts (e.g. "Critical 5", "KEV 3")
- Detail drawer, tabs, multi-step wizard, "About…" info tooltips
- Export button (CSV/PDF), empty and error states with **Retry**

## Data
Organisation · User · Member/Role · Session · Notification

## Depends on
Nothing.

## Done when
- A user can sign up or be invited, log in, turn on MFA and switch theme
- Viewers can't edit, Analysts can't manage members, Admins can do everything
- The shell renders on all routes, and Ctrl K search opens (results come later)
- The table, filter, drawer and wizard components are documented and reusable

## Unknowns ⚠
- Login and sign-up screens and any SSO options (not crawled)
- What notifications contain
- The Home page (`/`) only captured the greeting "Good afternoon, *name*". Its dashboard content is unknown
