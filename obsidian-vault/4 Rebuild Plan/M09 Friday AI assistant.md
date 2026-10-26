---
tags:
  - plan
phase: 9
size: L
---

# M09 Friday AI assistant

⬆ **Back:** [[REBUILD PLAN]] · ⬅ [[M08 Threat intel]] · ➡ **Next:** [[M10 Settings Integrations Policies]]

*An AI assistant that answers questions about your data and carries out multi-step work after you approve it.*

## Pages
- Side panel on every page (part of the [[Global shell]])
- `/friday` ⚠ · `/friday/inbox` ⚠ (Inbox) · `/friday/projects` ⚠ (Projects) · `/friday/plans` (Run history)
- Sidebar also shows **Chats**

## Features
**Side panel**
- Chat box ("Message Friday"), Send, attach an image or PDF
- Suggested questions: "What needs my attention today?", "How many critical CVEs are open?", "Show me our open PSIRTs."
- **Ask Friday about this page** (sends the current page as context)
- **Ask** (answer) vs **Do it** (take action) modes
- Proactive nudge, e.g. "6 exploited CVEs are open. Start with CVE-2016-5195. [Show them]"
- Expand to fullscreen, close, hide sections

**Work mode**
- "Friday, work on it" from a finding → creates a plan
- **Plans:** multi-step plans with a human approval step before each action (Run history)
- Inbox: items Friday needs you to look at · Projects: longer pieces of work

**Under the hood**
- LLM with tool use over the app's own API: read findings, draft VEX, draft supplier tasks, create PSIRT cases
- Respects the user's role. Every write goes through approval and is audited

## Data
Chat · Message · Plan · Plan step (proposed / approved / done) · Inbox item · Project

## Depends on
Most useful after [[M01 Products and SBOMs]] to [[M07 Reports]]. The chat panel can ship earlier, read-only.

## Done when
- Friday answers the 3 suggested questions correctly from live data
- "Do it" never writes anything without the user approving the step
- Every plan and action shows in Run history

## Unknowns ⚠
- Chat, Inbox and Projects pages were not captured
- What actions Friday is allowed to take
