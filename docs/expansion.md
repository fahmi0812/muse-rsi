# muse-rsi Expansion Plan — Full Cross-Domain (Full-Stack, DevOps, Office, College, Research, Health)

**Date:** 20 November 2026
**Status:** Fully implemented on 20 November 2026. The 30 pending repos were re-checked via the web the same day (see [recheck-web.md](recheck-web.md)): 27 promoted into four new domain packs (Full-Stack 7, Office 8, Research 5, Health 7), 3 not promoted. Total listed skills: 64.
**Sources (all verified, no invented numbers):**
- Lumitome map (local clone): `lumitome-skills-map.md` — 156 core skills, all SKILL.md descriptions read locally; registry 930 skills confirmed in `router/skills-registry.json`.
- External verification: `muse-rsi-expansion-verifikasi.md` — 48 external repos checked (46 unique). DevOps (8) and Academic (8) were fully verified first (SKILL.md + license); the remaining 30 were re-checked via the web the same day (see [recheck-web.md](recheck-web.md)): 27 promoted, 3 not. 0 pending.
- Current muse-rsi: `~/workspace/muse-rsi/` (README, skills/index.md, docs/verification.md, docs/critique.md).

## 1. Gap analysis per target domain

| Target domain | What Lumitome already covers (core 156) | Fully verified external repos | Still missing / pending |
|---|---|---|---|
| Full-Stack Development | 31 — STRONG: code review, TDD, refactoring, debugging, Next.js/React renderers, docs-pack, architecture | **7 — CLEARED via web re-check 20 Nov 2026** (see [recheck-web.md](recheck-web.md)); 1 not promoted (`bleu-dragon/codex-web-dev-skills`, no visible SKILL.md, no licence) | Lumitome has no dedicated API-design, DB-migration, or frontend-testing-depth skill beyond `test-value`/`tdd-red-green-refactor`. |
| DevOps & Infra | 8 — THIN: `automation-audit-ops`, `gh-axi`, `git-guardrails`, `mongodb-ops`, `supabase-ops`, `vercel-ops`, `release-bumper`, `rea-ci-tests-audit`. No K8s, no Terraform, no observability. | **8 — CLEARED NOW** (see §2) | Nothing blocking. This is the most complete domain after this expansion. |
| Agent & Orchestration | 28 — STRONG: EGM review loop, subagents, MCP builder, eval harness, skill creator/harmonization | Covered by Tier 1 (superpowers, agent-skills) | Nothing missing. |
| Office & Corporate | 5 — THIN: `internal-comms`, `one-pager`, `slides`, `smartdoc`, `tableau`. Plus `penulisan` pack (42, business writing). No email, spreadsheet, or meeting workflow in core. | **8 — CLEARED via web re-check 20 Nov 2026** (see [recheck-web.md](recheck-web.md)) | Nothing blocking. Note: `MAJI-Skills` is AGPL v3 — link only, never vendor. |
| College & Academic | 4 — THIN, all Indonesian academic writing: `laporan-generator`, `naskah-id`, `penulis-ilmiah`, `smartbook-ingest` (semester modules). No citation/Zotero workflow, no thesis lifecycle, no study planning. | **8 — CLEARED NOW** (see §2) | Thesis lifecycle + study workflow still need a new original skill (§4). |
| Research | 2 — THIN: `deep-research`, `research` only. | 2 already verified via Academic pass: `917Dhj/DeepPaperNote` (MIT, SKILL.md yes) and `WenyuChiou/ai-research-skills` (MIT, catalog only — no installable SKILL.md). **Plus 5 promoted via web re-check 20 Nov 2026** (Deep-Research-skills, paper-craft, claude-deep-research, agent-research-skills, slr-prisma); PaperSpine has no SKILL.md, so it is reference only. | Systematic review (PRISMA) is now covered by `keemanxp/slr-prisma`. |
| Health & Medical | **0 — MISSING.** Verified by grep on the clone: no skill dir, no pack dir, no FHIR string anywhere. Only false positives (document "health audit", PubMed listed as a source, `/api/health` endpoints). | **7 — CLEARED via web re-check 20 Nov 2026** (see [recheck-web.md](recheck-web.md)); 1 permanently excluded (`jmandel/health-skillz`, handles real patient EHR data). | Covered by the 7 external research-only repos plus the new original skill `health-research-literacy` (§4). |
| Security (defensive) | 30 — STRONG: 16 `hunt-*`, `code-audit`, `owasp-security`, `security-audit`, `fp-check`, `triage-validation`, `cvss-scoring` | — | Nothing missing. Red-team pack (166) is DISABLED by design and must never be added. |
| Design & Media | 36 — STRONG, the biggest core domain | Covered by existing gap fillers (taste, hallmark, unslop) | Nothing missing. |
| Finance & Business (ID) | 4 — `akuntansi-umkm`, `analisis-laporan-keuangan`, `keuangan-pribadi`, `pajak-dasar-id` | — | Out of scope for this expansion (already covered for Indonesian small business). |

## 2. Cleared to add now — 16 external repos (fully verified SKILL.md + license)

### 2a. DevOps & Infra — 8 repos (all MIT or Apache-2.0, no license flags)

| Repo | Stars (20 Nov 2026) | SKILL.md | License | Verdict |
|---|---|---|---|---|
| [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill) | 2,481 | Yes, `skills/terraform-skill/SKILL.md` | Apache-2.0 | FIT — Terraform & OpenTofu, top pick |
| [BagelHole/DevOps-Security-Agent-Skills](https://github.com/BagelHole/DevOps-Security-Agent-Skills) | 1,210 | Yes, `skills/` (80+ skills) | MIT | FIT WITH NOTES — import selectively, not the whole tree |
| [LukasNiessen/kubernetes-skill](https://github.com/LukasNiessen/kubernetes-skill) | 479 | Yes, root | MIT | FIT — K8s/Helm/Kustomize, EKS/GKE/AKS, GitOps |
| [zxkane/aws-skills](https://github.com/zxkane/aws-skills) | 379 | Yes, `plugins/*/skills/*/SKILL.md` | MIT | FIT — AWS IaC, serverless, cost ops |
| [aws/tools-for-devops-agent](https://github.com/aws/tools-for-devops-agent) | 143 | Yes, `skills/*/SKILL.md` | Apache-2.0 | FIT WITH NOTES — official AWS org; AWS-only; 100 open issues, check backlog first |
| [ollygarden/opentelemetry-agent-skills](https://github.com/ollygarden/opentelemetry-agent-skills) | 126 | Yes, `skills/otel-*/SKILL.md` | Apache-2.0 | FIT — vendor-neutral observability |
| [bregman-arie/devops-sre-skills](https://github.com/bregman-arie/devops-sre-skills) | 30 | Yes, `skills/argocd/...` | Apache-2.0 | FIT WITH NOTES — small/new (30 stars), SRE runbooks |
| [vstorm-co/production-stack-skills](https://github.com/vstorm-co/production-stack-skills) | 28 | Yes, `skills/production-check/SKILL.md`, `skills/production-deploy/SKILL.md` | MIT | FIT WITH NOTES — small/new; FastAPI/Postgres/Docker/deploy |

### 2b. College & Academic — 8 repos (fully verified)

| Repo | Stars (20 Nov 2026) | SKILL.md | License | Verdict |
|---|---|---|---|---|
| [Gabberflast/academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) | 1,646 | Yes, root | **Proprietary** (per SKILL.md frontmatter: "LICENSE.txt has complete terms") | FIT WITH NOTES — link only; read LICENSE.txt before any vendoring/redistribution |
| [917Dhj/DeepPaperNote](https://github.com/917Dhj/DeepPaperNote) | 1,417 | Yes, `skills/deeppapernote/SKILL.md` | MIT | FIT — paper → linked Obsidian notes; Zotero-aware; also counts for Research |
| [LeonChaoX/qinyan-academic-skills](https://github.com/LeonChaoX/qinyan-academic-skills) | 1,055 | Yes, `skills/` | MIT | FIT — largest academic library (182 installable skills) |
| [WenyuChiou/ai-research-skills](https://github.com/WenyuChiou/ai-research-skills) | 681 | **No** — root SKILL.md 404, no `skills/` dir; only `catalog/skills.yml` | MIT | FIT WITH NOTES — reference catalog only, nothing installable |
| [wp-a/nature-academic-search](https://github.com/wp-a/nature-academic-search) | 397 | Yes, root | MIT | FIT — multi-source literature search, citation verification, Zotero/EndNote export; docs partly Mandarin |
| [ShZhao27208/Aut_Sci_Write](https://github.com/ShZhao27208/Aut_Sci_Write) | 269 | Yes, `skills/sci-download/SKILL.md` | MIT | FIT WITH NOTES — WoS/Elsevier/Springer sources may need institutional access |
| [ShaishavMaisuria/research-paper-lifecycle-skills](https://github.com/ShaishavMaisuria/research-paper-lifecycle-skills) | 62 | Yes, `skills/add-venue-profile/SKILL.md` | Apache-2.0 | FIT — 42 skills, full paper lifecycle incl. submission & rebuttal |
| [Nbill27/academic-writing-skills](https://github.com/Nbill27/academic-writing-skills) | 27 | Yes, `skills/academic-writing/SKILL.md` | MIT | FIT — Indonesian thesis/article writing; small but directly relevant |

**Count check:** 16 cleared to list. 15 are installable as skill files (all except the WenyuChiou catalog, which has no SKILL.md). 1 is proprietary (Gabberflast) — list as a link, never vendor.

## 3. Re-check results — 30 repos (resolved 20 Nov 2026)

All 30 were re-checked directly on the web on 20 November 2026 (see [recheck-web.md](recheck-web.md)). **27 were promoted** into the four domain packs; **3 were not** (PaperSpine — no SKILL.md; codex-web-dev-skills — no visible SKILL.md, no licence; health-skillz — handles real patient EHR data, permanently excluded). The lists below are kept as the record of what was checked.

### 3a. Full-Stack — 8 (top 3: petrkindlmann/qa-skills, wsimmonds/claude-nextjs-skills, PyModel/react-frontend-skills)
petrkindlmann/qa-skills (291) · PramodDutta/qaskills (250) · wsimmonds/claude-nextjs-skills (115) · laguagu/claude-code-nextjs-skills (74) · kazdenc/builder-skills (46) · PyModel/react-frontend-skills (43) · leejpsd/typescript-react-nextjs-patterns (22) · bleu-dragon/codex-web-dev-skills (1 — already NOT RECOMMENDED, too weak/unproven).

### 3b. Office & Corporate — 8 (top 3: chunkydotdev/email-skills, JunfengRan/PPTWork, Dangooy/trade-pipeline-skill)
chunkydotdev/email-skills (8) · JunfengRan/PPTWork (7) · Dangooy/trade-pipeline-skill (41) · hearthbook-tools/spreadsheet-agent-skills (0) · integrityauthority/office-agent-skills (2) · ProfCiccio/Skills-Catalog (0) · Ijam18/MAJI-Skills (19 — **AGPL v3 flag**, check license compatibility first) · skillsaas/microsoft-outlook (0).

### 3c. Research — 6 (2 already verified via Academic, see §1)
WUBING2023/PaperSpine (6,363) · Weizhena/Deep-Research-skills (2,581) · zsyggg/paper-craft-skills (1,519) · 199-biotechnologies/claude-deep-research-skill (1,226) · lingzhi227/agent-research-skills (474) · keemanxp/slr-prisma (126 — only PRISMA-specific candidate found).

### 3d. Health & Medical — 8 (top 3: aipoch/medical-research-skills, Aperivue/medsci-skills, PhenoML/ClaudeFHIRSkill)
aipoch/medical-research-skills (2,073) · Aperivue/medsci-skills (391) · BioTender-max/awesome-bio-agent-skills (225 — curated list, not a skill package) · awslabs/hcls-agent-skills (78) · ajhcs/healthcare-agents (54 — US admin workflows only) · PhenoML/ClaudeFHIRSkill (53) · NVIDIA/digital-health-skills (18) · jmandel/health-skillz (82 — already NOT RECOMMENDED: handles real patient EHR data via SMART on FHIR).

**Permanently NOT RECOMMENDED (do not re-check for inclusion):** jmandel/health-skillz, realactivity/tula (patient data + second opinion), aizech/clinical-skills (live clinical decision support), rhavekost/clinical-toolkit (live clinical calculators incl. suicide-prevention screening), bleu-dragon/codex-web-dev-skills (1 star, unproven), guanmo-ai/guan (404), win4r/MuseAI-Skills (unofficial archive), and all offensive/red-team material.

## 4. New original skills to write for muse-rsi (4)

Write these as new `SKILL.md` files under `skills/` in muse-rsi (original content, same style as the existing 3). Each must state its guardrails up front.

1. **`health-research-literacy`** — Health research literacy, NOT clinical care. How to read medical literature (study designs, RCT vs cohort vs case report), appraise evidence (risk of bias, GRADE-style certainty), find guidelines and systematic reviews, and explain findings in plain language. **Hard guardrails:** never diagnose, never recommend treatment, never interpret a person's symptoms/labs, never handle patient data, always say "consult a clinician" and cite sources with uncertainty stated. Fills the 0-skill health gap without clinical risk.
2. **`academic-campus`** — College workflow for Indonesian students. Thesis lifecycle (topic → proposal → seminar → sidang → revision), citation management (Zotero/BibTeX), campus admin documents (surat, laporan magang), study planning and exam prep. Links to `Nbill27/academic-writing-skills`, Lumitome `penulis-ilmiah` / `laporan-generator` / `smartbook-ingest`. **Guardrail:** writing help only — never fabricate citations, data, or results; flag AI-detection evasion requests as out of scope.
3. **`office-corporate`** — Office & corporate workflow. Email triage and drafting, meeting notes → decisions → action items, spreadsheet checks (formulas, reconciliation), slide decks, internal comms (status reports, leadership updates), document versioning. Links to Lumitome `internal-comms` / `smartdoc` / `slides` / `tableau` and muse-rsi's existing `genspark-ai/genoffice`. **Guardrail:** never send email or share documents without explicit approval; never paste confidential content into external tools.
4. **`fullstack-delivery`** — Full-stack delivery workflow. Spec → TDD → code review → CI → deploy → observe, with checklists for API design, DB migrations, frontend accessibility, and release gates. Ties together `github/spec-kit`, `evanklem/evanflow` (TDD), the new DevOps additions (terraform-skill, kubernetes-skill, production-stack-skills), and Lumitome `docs-pack` / `finishing-a-development-branch`. **Guardrail:** no deploys to production without tests passing and a rollback plan.

## 5. Proposed new structure for muse-rsi

Keep everything that exists. Additions only — no file is deleted, no existing number changes.

| Section | Content | Status |
|---|---|---|
| Tier 1 — Core RSI | 6 (unchanged) | Done |
| Gap fillers | 15 (unchanged) | Done |
| **NEW: Domain Pack — DevOps & Infra** | 8 repos from §2a | **Cleared now** |
| **NEW: Domain Pack — College & Academic** | 8 repos from §2b (incl. 1 proprietary link-only + 1 catalog-only) | **Cleared now** |
| **NEW: Lumitome Reference Index** | Link-only index of the 156 core Lumitome skills, grouped by the 12 domains in `lumitome-skills-map.md`. Link only — never copy SKILL.md content. Red-team pack excluded, with the reason stated. | Done |
| **NEW: Pending Re-check** | The 30 repos from §3, re-checked via the web 20 Nov 2026: 27 promoted, 3 not (see §3 / [recheck-web.md](recheck-web.md)). 0 pending. | Done |
| Original skills | 3 → **7** (add the 4 from §4) | Done |
| Docs | New `docs/expansion.md` (this plan, adapted) + update `docs/verification.md` | To write |
| README + skills/index.md | New domain sections added; counts updated: 37 listed + 27 promoted via web re-check = **64 listed skills** + 7 originals; reference index 156 Lumitome skills; 0 pending. | Done |

**Counts after this expansion (final, 20 Nov 2026):** 37 listed + 27 promoted via web re-check = **64 listed skills**, plus 7 original skills in-repo, plus a 156-skill Lumitome reference index, plus 0 pending. The repo stays link-only for upstream content (no SKILL.md copying), MIT for original content.

## 6. Guardrails to add to the repo (update README/CONTRIBUTING)

- **Health:** research and health-informatics only. No diagnosis, no treatment advice, no clinical decisions, no patient data — ever. Any skill that touches real patient records or live clinical tools is permanently excluded.
- **Security:** defensive only. The Lumitome red-team pack (166 skills) and all offensive/exploit material stay excluded, even as reference.
- **Licenses:** AGPL/GPL and proprietary repos are link-only with a flag, never vendored. Check the license before adding any repo.
- **Verification rule (unchanged):** no repo enters the index until SKILL.md + license are verified directly. Pending items stay in the Pending section, not in the main tables.
- **Academic integrity:** no fabricated citations/data/results; no AI-detection evasion.

## 7. Next steps (in order)

1. ~~Write the 4 new original skills (§4) into `~/workspace/muse-rsi/skills/` + update `skills/index.md`, README.md, `docs/expansion.md` (this plan).~~ Done on 20 November 2026 (commit `4ced01e`, plus follow-up fixes).
2. Push to GitHub `fahmi0812/muse-rsi` (new commit on main; no history rewrite needed — history is already clean).
3. Verify from GitHub: README + index + new skill files read back, no private data in the push.
4. ~~After the GitHub rate limit clears: re-check SKILL.md + license for the 30 pending repos (§3), promote the ones that pass, and update the Pending section.~~ Done the same day via the web — 27 promoted, 3 not (see [recheck-web.md](recheck-web.md)).
