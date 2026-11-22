# Skill Index — muse-rsi

> Complete index of the **66 listed skills** in muse-rsi: 6 Tier 1 skills + 15 verified gap fillers + 8 DevOps + 8 Academic + 8 Full-Stack + 8 Office + 5 Research + 7 Health + 1 Agent & Orchestration (repo-level), plus 11 original skills in this repo, further reference for Tiers 2–6, and a link-only index of 139 Lumitome skills. All 66 were verified directly — the last 27 via the web on 20 November 2026 (see [docs/recheck-web.md](../docs/recheck-web.md)), plus 2 more verified 22 November 2026 (modern-web-guidance, elephant-goldfish-model).
>
> To install the whole system at once (skills + router + tools + memory + SOUL merge, keeping your agent's character), run `python3 setup/setup.py --yes` — see [setup/README.md](../setup/README.md).
>
> **Verified:** 20 November 2026. Star counts are as recorded on that date and may have changed since.
>
> This repository does not copy upstream `SKILL.md` content. Each entry contains only a link, a one-line description, and a verification status.

## Summary

| Group | Count | Status |
|---|---|---|
| Tier 1 — Core RSI | 6 | Passed; install first |
| Gap fillers from the critique — 15 skills | 15 | Passed; close the 5 biggest gaps |
| Domain Pack — DevOps & Infra | 8 | Fully verified (SKILL.md + licence) |
| Domain Pack — College & Academic | 8 | Fully verified (SKILL.md + licence) |
| Domain Pack — Full-Stack Development | 8 | Verified via web 20 Nov 2026; row 8 verified 22 Nov 2026 |
| Domain Pack — Office & Corporate | 8 | Verified via web 20 Nov 2026 |
| Domain Pack — Research | 5 | Verified via web 20 Nov 2026 |
| Domain Pack — Health & Medical | 7 | Verified via web 20 Nov 2026 |
| Agent & Orchestration (repo-level) | 1 | Verified via web 22 Nov 2026 |
| **Total listed skills** | **66** | — |
| Original skills in this repository | 11 | Written for this RSI system |
| Lumitome Reference Index (link only) | 139 | Verified locally from the Lumitome clone |
| Pending re-check | 0 | All 30 re-checked via web on 20 Nov 2026 — 27 promoted, 3 not (see below) |
| Further reference, Tiers 2–6 | 32 | Verified; install only when needed |
| Not recommended | 2 (plus offensive skills) | Do not install |

## Tier 1 — Core RSI (6)

Install these first.

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Notes |
|---|---|---|---|---|---|
| 1 | [anthropics/skills](https://github.com/anthropics/skills) | 197,897 | Yes | Not detected | Official skills: articles, slides, spreadsheets. |
| 2 | [obra/superpowers](https://github.com/obra/superpowers) | 322,499 | Yes | MIT | Research-to-writing workflow. |
| 3 | [mattpocock/skills](https://github.com/mattpocock/skills) | 328,522 | Yes (in subfolders) | MIT | `SKILL.md` files live in subfolders under `skills/`. |
| 4 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 119,305 | Yes | MIT | Production-grade engineering skills. |
| 5 | [google/skills](https://github.com/google/skills) | 24,470 | Yes (in subfolders) | Apache-2.0 | `SKILL.md` files live in subfolders under `skills/`. |
| 6 | [github/spec-kit](https://github.com/github/spec-kit) | 150,774 | No | MIT | Spec-driven toolkit, not a `SKILL.md` package. |

## Gap Fillers — 15 Skills

These close the 5 biggest gaps found in the critique (see [docs/critique.md](../docs/critique.md)): anti-slop / design taste, long-term memory, testing / QA / accessibility, Bahasa Indonesia, and browser + advanced video + presentations.

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Closes the gap in |
|---|---|---|---|---|---|
| 1 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 119,141 | Yes | MIT | Anti-slop / design taste. |
| 2 | [browser-use/browser-use](https://github.com/browser-use/browser-use) | 121,585 | Yes | MIT | Browser agent. |
| 3 | [OpenMontageInc/OpenMontage](https://github.com/OpenMontageInc/OpenMontage) | 81,870 | Yes | AGPL-3.0 | Full video production system. |
| 4 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 69,274 | Yes (integration folder) | Apache-2.0 | Long-term agent memory. |
| 5 | [Nutlope/hallmark](https://github.com/Nutlope/hallmark) | 58,330 | Yes | MIT | Anti-slop design. |
| 6 | [volcengine/OpenViking](https://github.com/volcengine/OpenViking) | 42,518 | Yes | AGPL-3.0 | Memory + RAG + self-evolving skills. |
| 7 | [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | 31,050 | Yes | MIT | SEO / GEO. |
| 8 | [meta/astryx](https://github.com/meta/astryx) | 31,198 | Yes | MIT | AI video editor. |
| 9 | [heydamir/unslop](https://github.com/heydamir/unslop) | 18,976 | Yes | CC-BY-4.0 | Anti-slop UI. |
| 10 | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 12,676 | Yes | Apache-2.0 | AI office suite. |
| 11 | [presenton/presenton](https://github.com/presenton/presenton) | 11,980 | No (app + API) | Apache-2.0 | Presentation generator, used as a tool. |
| 12 | [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) | 7,005 | Yes (at root) | MIT | Self-evolving skills. |
| 13 | [plugin87/ux-ui-agent-skills](https://github.com/plugin87/ux-ui-agent-skills) | 3,209 | Yes | MIT | Accessibility, WCAG 2.2. |
| 14 | [evanklem/evanflow](https://github.com/evanklem/evanflow) | 419 | Yes | NOASSERTION | TDD, 16 skills. Small repo — read it first. |
| 15 | [adhiprib/humanizer-indonesia](https://github.com/adhiprib/humanizer-indonesia) | 346 | Yes (at root) | MIT | Natural Indonesian writing. Small repo. |


## Domain Pack — DevOps & Infra (8)

Fully verified on 20 November 2026 (SKILL.md + licence checked directly). See [docs/expansion.md](../docs/expansion.md).

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Notes |
|---|---|---|---|---|---|
| 1 | [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill) | 2,481 | Yes (`skills/terraform-skill/SKILL.md`) | Apache-2.0 | Terraform & OpenTofu, top pick. |
| 2 | [BagelHole/DevOps-Security-Agent-Skills](https://github.com/BagelHole/DevOps-Security-Agent-Skills) | 1,210 | Yes (`skills/`, 80+ skills) | MIT | Widest coverage: K8s, Terraform, AWS/Azure/GCP, hardening, SOC2/ISO27001. Import selectively, not the whole tree. |
| 3 | [LukasNiessen/kubernetes-skill](https://github.com/LukasNiessen/kubernetes-skill) | 479 | Yes (at root) | MIT | K8s/Helm/Kustomize, EKS/GKE/AKS, GitOps. |
| 4 | [zxkane/aws-skills](https://github.com/zxkane/aws-skills) | 379 | Yes (`plugins/*/skills/*/SKILL.md`) | MIT | AWS IaC, serverless, cost ops. |
| 5 | [aws/tools-for-devops-agent](https://github.com/aws/tools-for-devops-agent) | 143 | Yes (`skills/*/SKILL.md`) | Apache-2.0 | Official AWS org; AWS-only; 100 open issues — check the backlog first. |
| 6 | [ollygarden/opentelemetry-agent-skills](https://github.com/ollygarden/opentelemetry-agent-skills) | 126 | Yes (`skills/otel-*/SKILL.md`) | Apache-2.0 | Vendor-neutral observability. |
| 7 | [bregman-arie/devops-sre-skills](https://github.com/bregman-arie/devops-sre-skills) | 30 | Yes (`skills/argocd/...`) | Apache-2.0 | SRE runbooks. Small/new — read it first. |
| 8 | [vstorm-co/production-stack-skills](https://github.com/vstorm-co/production-stack-skills) | 28 | Yes (`skills/production-check/SKILL.md`, `skills/production-deploy/SKILL.md`) | MIT | FastAPI/Postgres/Docker/deploy. Small/new. |

## Domain Pack — College & Academic (8)

Fully verified on 20 November 2026 (SKILL.md + licence checked directly). See [docs/expansion.md](../docs/expansion.md).

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Notes |
|---|---|---|---|---|---|
| 1 | [Gabberflast/academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) | 1,646 | Yes (at root) | **Proprietary** | Academic slides. Link only — read LICENSE.txt before any vendoring/redistribution. |
| 2 | [917Dhj/DeepPaperNote](https://github.com/917Dhj/DeepPaperNote) | 1,417 | Yes (`skills/deeppapernote/SKILL.md`) | MIT | Paper → linked Obsidian notes; Zotero-aware. Also counts for Research. |
| 3 | [LeonChaoX/qinyan-academic-skills](https://github.com/LeonChaoX/qinyan-academic-skills) | 1,055 | Yes (`skills/`) | MIT | Largest academic library (182 installable skills). |
| 4 | [WenyuChiou/ai-research-skills](https://github.com/WenyuChiou/ai-research-skills) | 681 | **No** (only `catalog/skills.yml`) | MIT | Reference catalog only — nothing installable. |
| 5 | [wp-a/nature-academic-search](https://github.com/wp-a/nature-academic-search) | 397 | Yes (at root) | MIT | Multi-source literature search, citation verification, Zotero/EndNote export. Docs partly Mandarin. |
| 6 | [ShZhao27208/Aut_Sci_Write](https://github.com/ShZhao27208/Aut_Sci_Write) | 269 | Yes (`skills/sci-download/SKILL.md`) | MIT | Literature search/download, PDF extraction, Zotero sync. Some sources may need institutional access. |
| 7 | [ShaishavMaisuria/research-paper-lifecycle-skills](https://github.com/ShaishavMaisuria/research-paper-lifecycle-skills) | 62 | Yes (`skills/add-venue-profile/SKILL.md`) | Apache-2.0 | 42 skills, full paper lifecycle incl. submission & rebuttal. |
| 8 | [Nbill27/academic-writing-skills](https://github.com/Nbill27/academic-writing-skills) | 27 | Yes (`skills/academic-writing/SKILL.md`) | MIT | Indonesian thesis/article writing. Small but directly relevant. |

## Lumitome Reference Index (139, link only)

[Fahmi's own Lumitome](https://github.com/fahmi0812/Lumitome) (OpenCode-based coding assistant, v0.3.79) has 139 core skills in `.opencode/skills/` (17 offensive excluded per repo policy), all verified locally from a clone on 20 November 2026. The full table is in [docs/lumitome-index.md](../docs/lumitome-index.md). Link only — no `SKILL.md` content is copied here.

| Domain | Skills | Assessment |
|---|---|---|
| Design & Media | 36 | Strong |
| Full-Stack Development | 31 | Strong |
| Security (defensive) | 13 | Strong (defensive only) |
| Agent & Orchestration | 28 | Strong |
| DevOps & Infra | 8 | Thin (no K8s/Terraform/observability — covered by the DevOps pack above) |
| Office & Corporate | 5 | Thin |
| Writing & Language (ID) | 5 | Thin |
| Finance & Business (ID) | 4 | Covered for Indonesian small business |
| College & Academic | 4 | Thin (covered by the Academic pack above) |
| Research | 2 | Thin |
| Health & Medical | 0 | **Missing** — covered by the new `health-research-literacy` original skill |
| Other | 3 | — |

The Lumitome registry holds 930 skills in total (`router/skills-registry.json`, verified locally), of which 764 are routable — the 166-skill red-team pack is disabled by design and is **never** included here, even as a reference.


## Domain Pack — Full-Stack Development (8)

Verified via the web on 20 November 2026 (SKILL.md + licence read from each repo page). See [docs/recheck-web.md](../docs/recheck-web.md). Row 8 (modern-web-guidance) verified 22 November 2026.

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Notes | Keywords |
|---|---|---|---|---|---|---|
| 1 | [petrkindlmann/qa-skills](https://github.com/petrkindlmann/qa-skills) | 291 | Yes (`skills/accessibility-testing/SKILL.md`) | MIT | QA / test automation (Playwright, Cypress, E2E). Top pick. | |
| 2 | [PramodDutta/qaskills](https://github.com/PramodDutta/qaskills) | 250 | Yes (`.claude/skills/ship-prod/SKILL.md`) | MIT | QA/testing directory. Overlaps with petrkindlmann — pick one. | |
| 3 | [wsimmonds/claude-nextjs-skills](https://github.com/wsimmonds/claude-nextjs-skills) | 115 | Yes (root folders, e.g. `nextjs-advanced-routing/SKILL.md`) | MIT | Next.js skills. Last commit 24 Oct 2025 — stale, over 1 year old. | |
| 4 | [laguagu/claude-code-nextjs-skills](https://github.com/laguagu/claude-code-nextjs-skills) | 74 | Yes (`skills/ai-app/SKILL.md`) | MIT | Next.js 16 + AI SDK 7 + pgvector + Bun. Active. | |
| 5 | [kazdenc/builder-skills](https://github.com/kazdenc/builder-skills) | 46 | Yes (`.claude/skills/dev/test/test-plan/SKILL.md`) | MIT | 47 skills: product, frontend, full-stack, browser automation. Last update 9 Mar 2026. | |
| 6 | [PyModel/react-frontend-skills](https://github.com/PyModel/react-frontend-skills) | 43 | Yes (`skills/react/SKILL.md`) | MIT | React 19 / Next.js 16 / TypeScript, testing, UI. | |
| 7 | [leejpsd/typescript-react-nextjs-patterns](https://github.com/leejpsd/typescript-react-nextjs-patterns) | 22 | Yes (at root) | MIT | TypeScript/React/Next.js decision guides. Small repo. | |
| 8 | [googlechrome/modern-web-guidance](https://github.com/googlechrome/modern-web-guidance) | 24,695 | Yes (`skills/modern-web-guidance/SKILL.md`) | Apache-2.0 | 210 expert guides for the modern web platform: CSS, HTML, client-side JS, accessibility, dark mode, dialog, modal, popover, container queries, view transitions, forms, validation, autofill, passkeys, performance, web components. CLI search/retrieve via npx, Node >=22. | dialog, modal, dark mode, container queries, accessibility, popover, forms, validation, autofill, passkeys, performance, web components, CSS, HTML, typography, carousel, accordion, tabs, toast, scrollbar, wasm, webassembly, oklch, CWV, LCP, INP, CLS, built-in AI, sanitization, chrome |

## Agent & Orchestration — repo-level (1)

Repo-level upstream entry for Google's Elephant-Goldfish Model (design-doc workflow: Elephant drafts with full context, Goldfish blind-reviews without it). Verified via the web on 22 November 2026. Upstream has 8 skills; 7 are already indexed as Lumitome references from Fahmi's Lumitome clone (`egm-bootstrap`, `egm-brainstorm`, `egm-draft`, `egm-drift-report`, `egm-resolve`, `egm-review`, `egm-review-loop`) — `egm-lite` is not in `docs/lumitome-index.md` yet (pre-existing gap, not added here). This row adds only the upstream repo, not duplicate per-skill entries.

| # | Skill | Stars (22 Nov 2026) | SKILL.md? | Licence | Notes | Keywords |
|---|---|---|---|---|---|---|
| 1 | [google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model) | 21,959 | Yes (8 skills in subfolders) | Apache-2.0 | Elephant drafts design docs with full context; Goldfish blind review audits them without prior context. 8 skills: brainstorm, draft, review, review-loop, resolve, lite, bootstrap, drift-report. | egm, elephant, goldfish, blind review, design doc, design document, specification, spec, fresh eyes, review loop, brainstorm, drift, rfc, architecture, trade-off, assumption, reviewer, design review, spec review |

## Domain Pack — Office & Corporate (8)

Verified via the web on 20 November 2026. See [docs/recheck-web.md](../docs/recheck-web.md).

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Notes |
|---|---|---|---|---|---|
| 1 | [chunkydotdev/email-skills](https://github.com/chunkydotdev/email-skills) | 8 | Yes (`skills/diagnostics/email-diagnostics/SKILL.md`) | MIT | Email deliverability, auth, bounce, compliance. |
| 2 | [JunfengRan/PPTWork](https://github.com/JunfengRan/PPTWork) | 7 | Yes (`ppt/SKILL.md`) | MIT | Plan, write, and export PowerPoint decks. Last update 22 Jul 2026. |
| 3 | [Dangooy/trade-pipeline-skill](https://github.com/Dangooy/trade-pipeline-skill) | 41 | Yes (`.claude/skills/trade-pipeline-run/SKILL.md`) | MIT | Excel inquiry → Quotation / PI / CI / Packing List. Trade-docs niche. |
| 4 | [hearthbook-tools/spreadsheet-agent-skills](https://github.com/hearthbook-tools/spreadsheet-agent-skills) | 0 | Yes (`skills/formula-first-workbook/SKILL.md`) | MIT | Excel formula-first: linter, break-even pricing, month-end close. 0 stars — unproven. |
| 5 | [integrityauthority/office-agent-skills](https://github.com/integrityauthority/office-agent-skills) | 2 | Yes (`.agents/skills/office-live/SKILL.md`) | MIT | MS Office + Microsoft 365. Live editing is Windows-COM only. |
| 6 | [ProfCiccio/Skills-Catalog](https://github.com/ProfCiccio/Skills-Catalog) | 0 | Yes (`ai-workflow-infographic/SKILL.md`) | None shown | Executive comms, project delivery, knowledge management. No licence shown — check before use. |
| 7 | [Ijam18/MAJI-Skills](https://github.com/Ijam18/MAJI-Skills) | 19 | Yes (`.agents/skills/maji-commit/SKILL.md`) | **AGPL v3** | Planning/shipping/docs playbooks. Link only — never vendor (AGPL). |
| 8 | [skillsaas/microsoft-outlook](https://github.com/skillsaas/microsoft-outlook) | 0 | Yes (at root) | MIT | Outlook: inspect .msg/.eml/.ics, triage, drafts via Graph. 0 stars. |

## Domain Pack — Research (5)

Verified via the web on 20 November 2026. See [docs/recheck-web.md](../docs/recheck-web.md). PaperSpine is NOT here — it has no `SKILL.md` (see Not Included).

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Notes |
|---|---|---|---|---|---|
| 1 | [Weizhena/Deep-Research-skills](https://github.com/Weizhena/Deep-Research-skills) | 2,581 | Yes (`skills/research-en/research/SKILL.md`) | MIT | Structured deep research, multi-agent. Last update 23 Aug 2026. |
| 2 | [zsyggg/paper-craft-skills](https://github.com/zsyggg/paper-craft-skills) | 1,519 | Yes (`skills/paper-analyzer/SKILL.md`) | MIT (README) | Paper analysis, comics, summaries. Licence stated in README only. |
| 3 | [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) | 1,226 | Yes (at root) | MIT (README) | 8-phase deep-research pipeline. Licence stated in README only. |
| 4 | [lingzhi227/agent-research-skills](https://github.com/lingzhi227/agent-research-skills) | 474 | Yes (`skills/deep-research/SKILL.md`) | None shown | Systematic literature review + 10 more skills (incl. Zotero). No licence shown. Last update 27 Feb 2026. |
| 5 | [keemanxp/slr-prisma](https://github.com/keemanxp/slr-prisma) | 126 | Yes (at root) | MIT | Systematic literature review following PRISMA 2020. Only PRISMA-specific skill found. |

## Domain Pack — Health & Medical (7)

Verified via the web on 20 November 2026. Research and health-informatics only — see the health guardrail in the README. See [docs/recheck-web.md](../docs/recheck-web.md).

| # | Skill | Stars (20 Nov 2026) | SKILL.md? | Licence | Notes |
|---|---|---|---|---|---|
| 1 | [aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills) | 2,073 | Yes (subfolders, e.g. `scientific-skills/Academic Writing/abstract-summarizer/SKILL.md`) | MIT | Hundreds of skills: protocol design, data analysis, evidence insight, academic writing. |
| 2 | [Aperivue/medsci-skills](https://github.com/Aperivue/medsci-skills) | 391 | Yes (`skills/analyze-stats/SKILL.md`) | MIT | Medical research: literature search, reporting guidelines, statistics, figures, submission. |
| 3 | [BioTender-max/awesome-bio-agent-skills](https://github.com/BioTender-max/awesome-bio-agent-skills) | 225 | Yes (`skills/claude-science/alphafold2/SKILL.md`) | CC0 1.0 | Curated list for biomedical research (genomics, proteomics, single-cell, protein design). Discovery index, not a package. Last update 1 Jul 2026. |
| 4 | [awslabs/hcls-agent-skills](https://github.com/awslabs/hcls-agent-skills) | 78 | Yes (`skills/variant-calling/SKILL.md`) | MIT-0 | 43 skills across 13 HCLS domains: medical coding, claims, genomics, imaging, drug discovery. Check skills one by one. |
| 5 | [ajhcs/healthcare-agents](https://github.com/ajhcs/healthcare-agents) | 54 | Yes (`skills/healthcare-agents/SKILL.md`) | Apache-2.0 | 51 specialist agents for US healthcare *admin* workflows only. |
| 6 | [PhenoML/ClaudeFHIRSkill](https://github.com/PhenoML/ClaudeFHIRSkill) | 53 | Yes (at root) | Apache-2.0 | Build FHIR artefacts/apps with Claude. Pure health-informatics. Last update 2 Mar 2026. |
| 7 | [NVIDIA/digital-health-skills](https://github.com/NVIDIA/digital-health-skills) | 18 | Yes (`skills/digital-health-clinical-asr-setup/SKILL.md`) | Apache-2.0 | Agent-guided health AI workflows: evaluation, data generation, deployment. Vendor repo, small. |

## Pending Re-check — resolved

All 30 pending repos were re-checked via the web on 20 November 2026 (see [docs/recheck-web.md](../docs/recheck-web.md)). **27 were promoted** into the four domain packs above. **3 were not:**

- [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine) — no `SKILL.md` at all (tool/app, not an installable skill). Reference only.
- [bleu-dragon/codex-web-dev-skills](https://github.com/bleu-dragon/codex-web-dev-skills) — no visible `SKILL.md` (skills only inside a `.rar` archive), no licence, 1 star.
- [jmandel/health-skillz](https://github.com/jmandel/health-skillz) — handles real patient EHR data. Permanently excluded.

## Router — Install and Route (skills/router/)

[skills/router/SKILL.md](router/SKILL.md) + [skills/router/registry.json](router/registry.json) (248 entries: 66 core + 32 reference + 11 originals + 139 Lumitome reference). Install the router as a custom skill together with the 11 original skills. It scores each request with a BM25-style ranker over `keywords` (3.0) + `domain` (2.0) + `notes` (1.0), breaks ties by tier (original > core > reference > lumitome-reference), and returns `NO_MATCH` when no keyword matches. Routing is covered by a 130-case eval (`scripts/eval_routing.py`) — all 130 passed on 22 November 2026.

## Original Skills in This Repository (11)

Written for the KimiCharmi RSI — not copies of upstream skills:

| Skill | File | Purpose |
|---|---|---|
| rsi-loop | [rsi-loop/SKILL.md](rsi-loop/SKILL.md) | Daily RSI loop: audit → fix → test → snapshot → save or roll back. |
| self-audit | [self-audit/SKILL.md](self-audit/SKILL.md) | Checklist for auditing a new skill before installation. |
| anti-slop-checklist | [anti-slop-checklist/SKILL.md](anti-slop-checklist/SKILL.md) | Anti-slop checklist for UI, video, and writing. |
| health-research-literacy | [health-research-literacy/SKILL.md](health-research-literacy/SKILL.md) | Read and appraise medical literature. Research only — never diagnose, treat, or handle patient data. |
| academic-campus | [academic-campus/SKILL.md](academic-campus/SKILL.md) | Indonesian thesis lifecycle, citations (Zotero), campus documents, study planning. |
| office-corporate | [office-corporate/SKILL.md](office-corporate/SKILL.md) | Email, meetings, spreadsheets, decks, internal comms. Never send/share without approval. |
| fullstack-delivery | [fullstack-delivery/SKILL.md](fullstack-delivery/SKILL.md) | Spec → TDD → review → CI → deploy → observe. No prod deploy without tests + rollback plan. |
| visual-check | [visual-check/SKILL.md](visual-check/SKILL.md) | Screenshot any page or HTML file at 360, 768, and 1280 pixels plus dark mode, and report console errors, failed requests, and horizontal overflow. |
| contribute | [contribute/SKILL.md](contribute/SKILL.md) | Contribute back to the repo from any Muse agent: fork, verify, PR, file issues, star, and send an install report. |
| council | [council/SKILL.md](council/SKILL.md) | Blind multi-model council — three judges from three providers decide high-stakes calls. |
| interrogate-claim | [interrogate-claim/SKILL.md](interrogate-claim/SKILL.md) | Adversarial interrogation — stress-test a claim, artifact, or plan before trusting it. |

> Note (21 Nov 2026): the original is named `interrogate-claim` because the
> name `interrogate` is already taken in the registry by a lumitome-reference
> entry (Agent & Orchestration, from Lumitome) with a near-identical purpose.

## Further Reference — Tiers 2–6

Verified on 20 November 2026 (39 of 40 repositories). Install only when needed, and read the notes under each table first.

### Tier 2 — Video (10)

| Skill | Stars | SKILL.md? | Licence | Notes |
|---|---|---|---|---|
| [masonmosen/muse-video-prompt-skill](https://github.com/masonmosen/muse-video-prompt-skill) | 66 | Yes (at root) | MIT | Small repo — read the `SKILL.md` first. |
| [LuoJiangYong/muse-video-skill](https://github.com/LuoJiangYong/muse-video-skill) | 116 | Yes (at root) | MIT | Small repo — read the `SKILL.md` first. |
| [sonlovinbot-team/Muse-animated-short-film](https://github.com/sonlovinbot-team/Muse-animated-short-film) | 84 | Yes (at root) | MIT | Small repo — read the `SKILL.md` first. |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | 7,608 | Yes | Not detected | Official Remotion skills. |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | 74,489 | Not at root | NOASSERTION | Code-based video library; has a `.claude/skills/` folder. |
| [motiondivision/motion](https://github.com/motiondivision/motion) | 35,392 | No | MIT | Motion library, not a skill package. |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | 18,804 | Yes | MIT | Official GSAP skills. |
| [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | 3,442 | Yes | MIT | Timing, easing, Disney's 12 principles. |
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 144,783 | No | MIT | AI video-making app, not a `SKILL.md`. |
| [useapi/muse-api](https://github.com/useapi/muse-api) | 32 | Yes | MIT | Third-party service, not Meta's official API. Evaluate account and privacy risks first. |

### Tier 3 — Defensive Security (6)

| Skill | Stars | SKILL.md? | Licence | Notes |
|---|---|---|---|---|
| [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | 29,540 | Not at root | AGPL-3.0 | Finds leaked credentials. Note the AGPL obligations. |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 8,313 | Not at root | CC-BY-SA-4.0 | Skills distributed via the `plugins/` folder. |
| [kenryu42/cc-safety-net](https://github.com/kenryu42/cc-safety-net) | 2,079 | Yes | MIT | Automated Claude Code guardrails. |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | 7,033 | No | MIT | Command plugin, not a `SKILL.md`. Last updated 11 February 2026 — the oldest in this list. |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 76,062 | Yes | MIT | Multi-phase security audit. |
| [agamm/claude-code-owasp](https://github.com/agamm/claude-code-owasp) | 456 | Not at root | MIT | OWASP Top 10. Has a `.claude/skills/` folder. |

### Tier 4 — Research, Documents, Voice (8)

| Skill | Stars | SKILL.md? | Licence | Notes |
|---|---|---|---|---|
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 204,758 | Yes | AGPL-3.0 | Third-party service; check API key and cost. |
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | 87,593 | No | Apache-2.0 | Crawler library, not a `SKILL.md`. |
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | 197,160 | No | MIT | Document-to-Markdown conversion tool. |
| [marp-team/marp-cli](https://github.com/marp-team/marp-cli) | 3,940 | No | MIT | Text-to-slides tool. |
| [kgmkm/muse-grok-x-search](https://github.com/kgmkm/muse-grok-x-search) | 211 | Yes (at root) | MIT | Small repo, empty description — read the `SKILL.md` first. |
| [openai/whisper](https://github.com/openai/whisper) | 113,157 | No | MIT | Transcription tool, not a `SKILL.md`. |
| [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) | 15,629 | No | MIT | Text-to-speech tool. |
| [nothinx/naskah-id](https://github.com/nothinx/naskah-id) | 115 | Yes (at root) | NOASSERTION | Indonesian-language skill. Check its LICENSE file first. |

### Tier 5 — Design, 3D (5)

| Skill | Stars | SKILL.md? | Licence | Notes |
|---|---|---|---|---|
| [arjun988/blender-skills](https://github.com/arjun988/blender-skills) | 4,450 | Not at root | MIT | Skills live in `.claude/skills/`. |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | 35,111 | No | MIT | MCP server for Blender, not a `SKILL.md`. |
| [majidmanzarpour/threejs-game-skills](https://github.com/majidmanzarpour/threejs-game-skills) | 2,863 | Yes | MIT | Three.js browser games. |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 152,002 | No | MIT | Distributed as a plugin — check the plugin contents first. |
| [kaankiziltug/logo-design-skill](https://github.com/kaankiziltug/logo-design-skill) | 7,394 | Yes | MIT | Logo design. |

### Tier 6 — Trading, Research Only (3)

Research and backtesting only. **No automated live trading** without Fahmi's approval.

| Skill | Stars | SKILL.md? | Licence | Notes |
|---|---|---|---|---|
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 123,237 | No | Apache-2.0 | Multi-agent research framework. |
| [microsoft/qlib](https://github.com/microsoft/qlib) | 50,447 | No | MIT | AI-oriented quantitative research platform. |
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | 57,094 | No | GPL-3.0 | Crypto trading bot — research only. |

## Not Included in This Index

| Repository | Reason |
|---|---|
| [guanmo-ai/guan](https://github.com/guanmo-ai/guan) | Not found (404) on 20 November 2026. |
| [win4r/MuseAI-Skills](https://github.com/win4r/MuseAI-Skills) | Unofficial installation snapshot, not a standard skill package. Reference only. |
| [Turnitout-Humanizer](https://github.com/AhmadHassan-BTed/Turnitout-Humanizer) | No `SKILL.md`; description is "Plagiarism Remover & Similarity Evader". |
| [jmandel/health-skillz](https://github.com/jmandel/health-skillz) | Handles real patient EHR data via SMART on FHIR. Permanently excluded. Confirmed by web re-check: no `SKILL.md` found either. |
| [bleu-dragon/codex-web-dev-skills](https://github.com/bleu-dragon/codex-web-dev-skills) | No visible `SKILL.md` (inside a `.rar` archive), no licence, 1 star. Confirmed by web re-check. |
| [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine) | No `SKILL.md` at all (6,363 stars, MIT). A tool/app, not an installable skill. Reference only. |
| [realactivity/tula](https://github.com/realactivity/tula) | Personal health intelligence, patient data + second opinion. Permanently excluded. |
| [aizech/clinical-skills](https://github.com/aizech/clinical-skills) | Live clinical decision support. Permanently excluded. |
| [rhavekost/clinical-toolkit](https://github.com/rhavekost/clinical-toolkit) | Live clinical calculators. Permanently excluded. |
| Offensive skills (pentesting, exploits, SMS bombers, jailbreaks) | Not included in muse-rsi, even though they appear in the starred list. |
| Lumitome red-team pack (166 skills) | Disabled by design in Lumitome. Never included, even as a reference. |

## How to Read the "SKILL.md?" Column

- **Yes** — a `SKILL.md` file was found and read in one example subfolder.
- **Yes (at root)** — `SKILL.md` exists at the repository root.
- **Yes (in subfolders)** — `SKILL.md` files exist in subfolders, not at the root.
- **Not at root** — no `SKILL.md` at the root, but a `skills/` / `.claude/skills/` / `plugins/` folder exists.
- **No** — no `SKILL.md` and no skill folder at the root. The repository is usually a library or a tool, not a skill package.
