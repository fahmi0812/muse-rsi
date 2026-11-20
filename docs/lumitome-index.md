# Lumitome — Skill Registry Map (verified from local clone)

Repo: **fahmi0812/Lumitome** — coding assistant built on OpenCode, v0.3.79.
Mapped: 2026-11-20, from the local clone at `~/workspace/lumitome-check/` (no GitHub API, no rate limits).
Method: all 156 `SKILL.md` frontmatter descriptions read locally from `.opencode/skills/*/SKILL.md`;
registry counts from `router/skills-registry.json` (v3); pack dir lists from `packs/`.
This file REPLACES the earlier partial map (26/156 verified via API, rest provisional).

## Retrieval status

- `.opencode/skills/` fully listed: **156 top-level skill dirs, all with a `SKILL.md`** — verified locally.
- **156/156 SKILL.md descriptions verified locally** (frontmatter `description`). Purposes below are copied/trimmed from those descriptions.
- Repo-wide `SKILL.md` files: **1048** (158 under `.opencode/skills/` — 156 top-level + 2 nested — + 888 under `packs/` + 2 test fixtures).
- Pack skill dirs: **841** across 12 packs.

## The 930 claim — reconciled

README says: *"930 skills in one registry … 764 routable; the 166-skill red-team pack stays disabled."*
Verified against `router/skills-registry.json` (v3): **exactly 930 entries**. By pack: core 156, 3d 96, cad 30,
career-extra 2, coding-extra 32, design-extra 28, gamedev 100, misc 102, motion 62, osint-extra 1, penulisan 42,
red-team 166, seo 113 — total 930. And 930 − 166 (red-team) = **764 routable**. The claim reconciles exactly
against the registry. File counts are higher (997 dirs / 1048 `SKILL.md` files) because packs contain nested
sub-skills and `-2`/`-3` variant dirs that are not all separately registered.

## Domain counts — core 156 skills

| Domain | Count | Assessment |
|---|---:|---|
| Full-Stack Development | 31 | STRONG |
| Design & Media | 36 | STRONG |
| Security | 30 | STRONG (incl. 16 `hunt-*` skills; defensive use only) |
| Agent & Orchestration | 28 | STRONG |
| DevOps & Infra | 8 | THIN — 8 skills, no K8s/Terraform/observability depth |
| Office & Corporate | 5 | THIN — 5 skills |
| Writing & Language (ID) | 5 | THIN — 5 skills |
| Finance & Business (ID) | 4 | THIN — 4 skills |
| College & Academic | 4 | THIN — 4 skills (all Indonesian academic writing / modules) |
| Research | 2 | THIN — 2 skills |
| Health & Medical | 0 | MISSING — 0 skills |
| Other | 3 | — |
| **Total** | **156** | — |

## Full table — all 156 core skills (sorted by domain, then name)

Purpose = frontmatter `description` from the local `SKILL.md` (trimmed to ~140 chars).

| Skill | 1-line purpose | Domain |
|---|---|---|
| `antislop` | Anti Slop: Rules for AI Coding Agents. The core filter. Load always to stop generic AI slop. | Full-Stack Development |
| `antislop-code` | Code comment hygiene for AI coding agents: remove generic AI-slop comments, keep the valuable ones, never touch the code. | Full-Stack Development |
| `archify-review` | Review Archify issues, PRs, or code through value, cost, and impact to support evidence-based maintenance decisions. Use for issue triage,… | Full-Stack Development |
| `chrome-devtools-axi` | Control a Chromium session through chrome-devtools-axi after opencode-chromium-cdp start. Use when an observed browser issue needs diagnost… | Full-Stack Development |
| `code-polish` | Polish changed code when the user explicitly asks, or when an active workflow requests post-implementation | Full-Stack Development |
| `code-review` | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo''s do… | Full-Stack Development |
| `commit` | Commit staged or intended changes: compose a Conventional Prefix or Natural Language message, then use ai-commit — | Full-Stack Development |
| `correct` | Find the mistakes agents keep repeating in this repo and make each one impossible. Try architecture first, then types, then a lint whose er… | Full-Stack Development |
| `docs-pack` | Bootstrap a 12-file living documentation pack for a project (PRD, architecture, data model, design system, security, testing, code style, A… *(12 living project docs (PRD, architecture, API spec…).)* | Full-Stack Development |
| `figure-it-out` | Design an auditable playbook when no narrower one fits: a large migration, an ambitious multi-part change, or work a human reviews after st… | Full-Stack Development |
| `finishing-a-development-branch` | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work | Full-Stack Development |
| `floorplan` | Draw a floorplan of an app's codebase (one repo or several side by side), an interactive node-graph map where every subsystem, module, file… | Full-Stack Development |
| `improve-codebase-architecture` | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. | Full-Stack Development |
| `large-file-refactor` | Discover large source-file refactor candidates and propose split plans based on cohesion and risk, using available | Full-Stack Development |
| `latency-optimization` | Make a latency-critical event-driven hot path as fast as possible: measure the baseline, move all I/O after the critical action, send the r… | Full-Stack Development |
| `naming-refactor` | Refactor naming and repository structure exhaustively while preserving behavior and external contracts. | Full-Stack Development |
| `next` | Next.js renderer for json-render that turns JSON specs into full Next.js applications with routes, layouts, SSR, and metadata. Use when wor… | Full-Stack Development |
| `rea-analysis-optimization` | Optimize REA providers and shared analysis workflows for agent context, latency, CPU, and memory while preserving correctness and Evidence.… | Full-Stack Development |
| `rea-changelog-update` | Prepare or rewrite REA release changelogs and GitHub release notes from pinned Git history, with verified contributor thanks and Release Pl… | Full-Stack Development |
| `rea-tool-design` | Audit, investigate, design, or change REA investigation tools, CLI/MCP contracts, provider capabilities, and Evidence semantics. | Full-Stack Development |
| `react` | React renderer for json-render that turns JSON specs into React components. Use when working with @json-render/react, building React UIs fr… | Full-Stack Development |
| `receiving-code-review` | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable… | Full-Stack Development |
| `requesting-code-review` | Use when completing tasks, implementing major features, or before merging to verify work meets requirements | Full-Stack Development |
| `root-cause-gate` | Analyze whether a proposed fix addresses root causes or symptoms, scan for cross-module patterns, and halt before expanding blast radius. | Full-Stack Development |
| `simplify-codebase` | Simplification audit or authorized codebase simplification whose stated objective is to remove accidental complexity. Use for evidence-back… | Full-Stack Development |
| `speckit-code-review` | Reviews Spec Kit code changes for consistency with applicable design documents, positive and negative test coverage, regression evidence fo… | Full-Stack Development |
| `stack-diagram` | Create cloud-architecture-style diagrams of tech stacks, system architectures, infra layouts, and service topologies — with real brand logo… | Full-Stack Development |
| `systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes | Full-Stack Development |
| `tdd-red-green-refactor` | Enforces a disciplined Red-Green-Refactor (TDD) workflow in TypeScript/Node.js. Use this whenever creating new features, fixing bugs, or mi… | Full-Stack Development |
| `test-value` | Improve test value and feedback cost when auditing slow, flaky, redundant or brittle tests; choosing tests during implementation; or review… | Full-Stack Development |
| `typed-service-contracts` | Architecture standard for building robust, type-safe TypeScript services using the "Spec and Handler" pattern. Use when building CLIs, libr… | Full-Stack Development |
| `antislop-human` | Human and accessibility skill for antislop. Contrast, keyboard, focus, states, and interaction affordances for real people. Includes the co… | Design & Media |
| `antislop-layoutmobile` | Mobile layout skill for antislop. Use for layouts that reflow across screen sizes, phone to desktop: grids, overflow, tap targets. Load wit… | Design & Media |
| `antislop-ui` | UI and visual skill for antislop. Use when building or editing any interface: color, layout, components, motion, and page performance. Load… | Design & Media |
| `archify` | Create validated architecture, workflow, sequence, data-flow, lifecycle/state, ERD, class, tree, timeline, and waterfall diagrams as explor… | Design & Media |
| `archify-tuning` | Improve Archify diagram accuracy, visual quality and complete authoring speed with fewer repairs. Use for generation experiments or evaluat… | Design & Media |
| `banner-design` | Design banners for social media, ads, website heroes, creative assets, and print. Multiple art direction options with optional generated or… | Design & Media |
| `big-pics-little-words` | Explain the current subject in HTML with large visuals and minimal text while preserving key details. | Design & Media |
| `brand` | Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Activate for branded content, tone of voice, marke… | Design & Media |
| `design` | Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini, Atlas Cloud, or MuAPI AI), corpo… | Design & Media |
| `design-artifact` | Design principles and creative direction for building HTML artifacts — pages, reports, plans, landing pages, demos, decks, and small tools.… | Design & Media |
| `design-assets` | Cari komponen jadi dan aset desain dari 51 sumber web: shadcn/ui, ReUI, Watermelon UI, 21st.dev, Magic UI, HyperUI, daisyUI, NiceUI, Flowbi… | Design & Media |
| `design-system` | Token architecture, component specifications, and slide generation. Three-layer tokens (primitive→semantic→component), CSS variables, spaci… | Design & Media |
| `design-taste-frontend` | tasteskill v2, the anti-slop frontend skill. Art direction for websites, distilled from a study of 247 curated gallery sites (One Page Love… | Design & Media |
| `diagram-design` | Create branded architecture, architecture delta, IT current-state, flowchart, sequence, state machine, ER/data model, steps, timeline, swim… | Design & Media |
| `drawio-diagram` | Make or edit draw.io (diagrams.net) diagrams — architecture, flowchart, network, cloud (AWS/GCP/Azure icons), ER, sequence, org chart — as… | Design & Media |
| `emil-design-eng` | Emil Kowalski's design-engineering philosophy for UI polish, component design, animation decisions, and the invisible details that make sof… | Design & Media |
| `gsap-core` | Official GSAP skill for the core API — gsap.to(), from(), fromTo(), easing, duration, stagger, defaults, gsap.matchMedia() (responsive, pre… | Design & Media |
| `gsap-scrolltrigger` | Official GSAP skill for ScrollTrigger — scroll-linked animations, pinning, scrub, triggers. Use when building or recommending scroll-based… | Design & Media |
| `hallmark` | Design skill for websites and new pages that look designed, not generated. Use when the user asks to build or design something new, or name… | Design & Media |
| `html` | Create or redesign self-contained single-file HTML artifacts with a visual direction shaped by the user''s brief, project, and subject. Use… | Design & Media |
| `html-diagram` | Direct-invocation specialist for self-contained HTML diagrams whose layout, notation, and interaction clarify relationships, sequence, topo… | Design & Media |
| `html-plan` | Direct-invocation specialist for clear, self-contained HTML plans that preserve source material while improving hierarchy, sequence, owners… | Design & Media |
| `html-prototype` | Direct-invocation specialist for polished, responsive, self-contained HTML mockups and interactive prototypes grounded in the user''s conve… | Design & Media |
| `html-wireframe` | Direct-invocation specialist for low-fidelity, self-contained HTML wireframes that test information hierarchy, content, navigation, task fl… | Design & Media |
| `impeccable` | Use when the user wants to design, redesign, shape, critique, audit, polish, simplify, harden, animate, or otherwise improve a frontend int… | Design & Media |
| `logo-design` | Professional logo and brand-mark design, from brief to production files. Guides discovery and the design brief, concept generation, choosin… | Design & Media |
| `loopdesign` | Perbaiki desain berulang sampai bagus lewat loop render → gate → kritik (loopdesign / desain loop): Maker direction-first (DESIGN.md: arah… | Design & Media |
| `magic-ui` | Use this skill when users want to add, customize, or troubleshoot Magic UI components in React/Next.js projects. It covers component select… | Design & Media |
| `motion-design` | Taste rules for Remotion motion graphics — timing, easing, springs, typography, color, texture, and scene continuity, with concrete numbers… | Design & Media |
| `review-loop` | Visual self-review loop for motion graphics — render a draft, build contact sheets at every timeline beat, look at them, critique against a… | Design & Media |
| `sound-design` | Procedural sound design with the sfx engine — writing a cue sheet against a video's timeline, which sound goes with which visual event, gai… | Design & Media |
| `stitch-ui` | Buat UI dari gambar referensi: audit screenshot jadi design.md + Stitch prompt + index.html, lalu prompting modular di Google Stitch. Use f… | Design & Media |
| `ui-styling` | Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling,… | Design & Media |
| `ui-ux-pro-max` | UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces… | Design & Media |
| `video-demo` | Films a web app as narrated, zooming, cursor-driven demo videos with retina screenshots, either from a repo it builds and mocks or from a l… | Design & Media |
| `web-sims` | Build a simulation-style video (agents, particles, 3D machines, fly-throughs) as one HTML page whose render(t) is a pure function of time,… | Design & Media |
| `audit-context-building` | Understand a codebase before looking for bugs in it - what each function assumes, what it guarantees, and what it depends on elsewhere. Use… | Security |
| `bb-methodology` | Use at the START of any bug bounty hunting session, when switching targets, or when feeling lost about what to do next. Master orchestrator… | Security |
| `c-review` | Performs comprehensive C/C++ security review for memory corruption, integer overflows, race conditions, and platform-specific vulnerabiliti… | Security |
| `code-audit` | Use for authorized source-code security review and SAST workflows including Semgrep, CodeQL patterns, dangerous API hunting, and fix verifi… | Security |
| `cvss-scoring` | Produces CVSS v4.0 vector strings from plain-text vulnerability descriptions by systematically evaluating base metrics. Use when scoring a… | Security |
| `differential-review` | Performs security-focused differential review of code changes. Adapts analysis depth to codebase size, uses git blame for context, calculat… | Security |
| `evidence-hygiene` | Evidence-capture and PoC-redaction discipline for bug-bounty submissions: cookie redaction protocol (which fields to mask, Preview annotati… | Security |
| `fp-check` | Systematically verifies suspected security bugs to eliminate false positives, producing a TRUE POSITIVE or FALSE POSITIVE verdict with docu… | Security |
| `full-audit-keamanan` | Comprehensive security auditing, code vulnerability scanning, and threat surface mapping. | Security |
| `hunt-auth-bypass` | Hunting skill for auth bypass vulnerabilities. Built from 12 public bug bounty reports across SAML XSW / parser-differential (GitHub Enterp… | Security |
| `hunt-csrf` | Hunting skill for csrf vulnerabilities. Built from 15 public bug bounty reports including modern variants — SameSite=Lax sibling-subdomain… | Security |
| `hunt-deserialization` | Hunt Insecure Deserialization — Java gadget chains (ysoserial), PHP object injection (phpggc), Python pickle RCE, .NET BinaryFormatter, Rub… | Security |
| `hunt-graphql` | Hunting skill for graphql vulnerabilities. Built from 12 public bug bounty reports across IDOR via node() / GID, mutation IDOR including AI… | Security |
| `hunt-idor` | Hunting skill for idor vulnerabilities. Built from 26 public bug bounty reports. Use when hunting idor on any target. | Security |
| `hunt-jwt-crypto` | Hunt JWT cryptographic failures — alg:none signature-stripping and RS256→HS256 key-confusion that let an attacker forge a token for any ide… | Security |
| `hunt-lfi` | Hunt Local File Inclusion (LFI), Remote File Inclusion (RFI), and Path Traversal — /etc/passwd read, log poisoning → RCE, PHP filter-chain… | Security |
| `hunt-llm-ai` | Hunt LLM/AI feature bugs — prompt injection, indirect injection, exfiltration via tool-use/markdown, ASCII smuggling, agentic AI security (… | Security |
| `hunt-oauth` | Hunting skill for oauth vulnerabilities. Built from 19 public bug bounty reports. Use when hunting oauth on any target. | Security |
| `hunt-rce` | Hunting skill for rce vulnerabilities. Built from 67 public bug bounty reports. Use when hunting rce on any target. | Security |
| `hunt-session` | Hunt Session Management vulnerabilities — session fixation (no regeneration on login), insufficient invalidation on logout / password-chang… | Security |
| `hunt-sqli` | Hunting skill for sqli vulnerabilities. Built from 12 public bug bounty reports including modern NoSQL injection (Rocket.Chat CVE-2021-2291… | Security |
| `hunt-ssrf` | Hunting skill for ssrf vulnerabilities. Built from 15 public bug bounty reports including AWS metadata SSRF (HackerOne $25k Analytics PDF,… | Security |
| `hunt-ssti` | Hunt server-side template injection (SSTI) across Jinja2 (Flask/Django), Twig (Symfony), Freemarker (Java), ERB (Rails), Spring, Velocity,… | Security |
| `hunt-xss` | Hunting skill for xss vulnerabilities. Built from 174 public bug bounty reports. Use when hunting xss on any target. For markup injection t… | Security |
| `hunt-xxe` | Hunting skill for xxe vulnerabilities. Built from 10 public bug bounty reports including SVG-upload XXE, Office-doc (PPTX/DOCX) XXE, SOAP X… | Security |
| `owasp-security` | Reviews code for security vulnerabilities and guides secure implementation using OWASP Top 10:2025, ASVS 5.0, the OWASP Top 10 for LLM Appl… | Security |
| `redteam-mindset` | Red-team operator discipline — the mindset corrections that separate offensive testing from defensive WAPT. Built from authorized red-team… *(Defensive WAPT discipline; not an offensive pack.)* | Security |
| `reverse-engineer-anything` | Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA, and build agent environments (Agen… | Security |
| `security-audit` | Security guidance and vulnerability review for codebases, APIs, services, CLI tools, libraries, and daemons. Use for security questions, fo… | Security |
| `triage-validation` | Finding validation before writing any report — 7-Question Gate (all 7 questions), 4 pre-submission gates, always-rejected list, conditional… | Security |
| `agents-brain` | Maintain README.md, AGENTS.md/CLAUDE.md, skills, and repo context. Create, scaffold, or initialize AGENTS.md files and | Agent & Orchestration |
| `agents-docs` | (no description in frontmatter) | Agent & Orchestration |
| `agents-introspection` | Use local Codex/Claude Code transcripts to assess recurrence risk for agent behavior. Recommend durable fixes to | Agent & Orchestration |
| `agents-system` | Redesign the assigned repository or repositories for agent understanding, control, and cumulative learning. Use when | Agent & Orchestration |
| `anti-spin-circuit-breaker` | Enforce hardcoded iteration limits (max 3) to break repetitive runaway cycles and trigger Exception Auditor. | Agent & Orchestration |
| `axi` | Agent eXperience Interface (AXI) — ergonomic standards for building CLI tools that agents use via shell execution. Use when building, modif… | Agent & Orchestration |
| `browser-act` | Browser automation CLI for AI agents. NEVER run browser-act commands directly via Bash — always invoke this skill first. Use browser-act wh… *(Browser automation CLI for agents.)* | Agent & Orchestration |
| `dispatching-parallel-agents` | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies | Agent & Orchestration |
| `egm-bootstrap` | Bootstrap directory README.md files across a repository subtree. | Agent & Orchestration |
| `egm-brainstorm` | Interactive ideation and brainstorming skill for the Elephant & Goldfish Model (EGM). Helps turn half-baked concepts into structured hypoth… | Agent & Orchestration |
| `egm-draft` | Drafts a design document section-by-section using the concepts brief from egm-brainstorm (or user notes). This is the second step in the El… | Agent & Orchestration |
| `egm-drift-report` | Runs drift detection on all design documents to check for document and code consistency. Produces an actionable report with differences. Us… | Agent & Orchestration |
| `egm-resolve` | The Elephant resolution skill. Ingests flat deficiency reports from concurrent Goldfish reviewers, applies automated fixes for PROPOSE FIX… | Agent & Orchestration |
| `egm-review` | Orchestrates the EGM Goldfish Review Protocol. Used as part of the EGM process to perform design document reviews. Executes five review pha… | Agent & Orchestration |
| `egm-review-loop` | Executes the Antagonistic-Review process from the Elephant-Goldfish Model (EGM) via an automated multi-agent review loop to audit documents… | Agent & Orchestration |
| `eval-harness` | Requires a named eval set and a pass rule before an agent or prompt change is trusted. | Agent & Orchestration |
| `executing-plans` | Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, o… | Agent & Orchestration |
| `external-tools` | Pasang aplikasi eksternal dan hubungkan ke agent: triage MCP/CLI/API, install per OS (Linux/Windows/macOS) tanpa sudo, daftarkan MCP ke Lum… | Agent & Orchestration |
| `in-your-own-words` | Restate in your own words what you think the user's goals are and what problem they're trying to solve. Use for /in-your-own-words. | Agent & Orchestration |
| `interrogate` | Use for "interrogate", "adversarial review", "multi-model review", "challenge this", "stress test this code", "find blind spots", or "tear… | Agent & Orchestration |
| `mcp-builder` | Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-desig… | Agent & Orchestration |
| `poteto-mode` | poteto's agent style for concise, detailed responses, deliberate subagents, unslopped prose, simple code, and verified work. Use for poteto… | Agent & Orchestration |
| `reflect` | Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill… | Agent & Orchestration |
| `skill-creator` | Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that ext… | Agent & Orchestration |
| `skill-harmonization` | Harmonize a repository's skill portfolio across catalog and user-installed skills. | Agent & Orchestration |
| `subagent-driven-development` | Use when executing implementation plans with independent tasks in the current session | Agent & Orchestration |
| `task-handoff` | Create one decision-complete task handoff in its repository or on the Desktop for cross-repository work, return a | Agent & Orchestration |
| `unified-done-gate` | Enforce deterministic completion checks before marking any task as complete. A missing gate is UNRUN, not PASS. | Agent & Orchestration |
| `automation-audit-ops` | Evidence-first inventory of live automations — cron, GitHub Actions, hooks, MCP servers, wrappers, and connectors — then keep / merge / cut… | DevOps & Infra |
| `gh-axi` | Operate GitHub through the gh-axi CLI - issues, pull requests, workflow runs, workflows, releases, repositories, labels, gists, Projects (v… | DevOps & Infra |
| `git-guardrails-claude-code` | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wa… | DevOps & Infra |
| `mongodb-ops` | Use when the user designs MongoDB schemas, indexes, aggregation, transactions, or Atlas-compatible data access. Not for UI, not for Supabas… | DevOps & Infra |
| `rea-ci-tests-audit` | Audit REA CI and test suites for correctness, fixture drift, false passes, and measured performance; use for suite or workflow investigatio… | DevOps & Infra |
| `release-bumper` | Cut a release: bump versions, write changelogs, commit, tag. | DevOps & Infra |
| `supabase-ops` | Use when the user works on Supabase Auth, RLS, Postgres schema/migrations, Edge Functions, Storage, Realtime, supabase-js, or @supabase/ssr… | DevOps & Infra |
| `vercel-ops` | Use when the user configures Vercel deploy, project env (names only), Next.js app router hosting, preview URLs, or vercel.json. Not for inv… | DevOps & Infra |
| `internal-comms` | A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use… | Office & Corporate |
| `one-pager` | Make a one-pager: one HTML page that shares an idea with teammates early, or recaps work for them, with big pictures and little words. | Office & Corporate |
| `slides` | Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies. *(Strategic HTML presentations (pitch decks, data slides).)* | Office & Corporate |
| `smartdoc` | Per-job document intelligence. Understand attached PDF/DOCX/TXT/MD/images, lock a Document Contract, then answer, create, transform, summar… | Office & Corporate |
| `tableau` | Analisis data Tableau Cloud/Server: cari workbook/view, baca metadata datasource, query data, ambil data & gambar view, baca Pulse metrics.… *(BI dashboards / data analysis at work.)* | Office & Corporate |
| `antislop-copywriting` | Copy and text skill for antislop. Use when writing or editing prose: headlines, tone, CTAs, and anti-AI-writing patterns. Load with the cor… | Writing & Language (ID) |
| `doc-coauthoring` | Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical… | Writing & Language (ID) |
| `humanizer` | Rewrite AI-sounding text so it reads like the writer without changing what it says. Use when editing or reviewing prose for AI tells: not-X… | Writing & Language (ID) |
| `humanizer-indonesia` | Menyunting teks bahasa Indonesia agar tidak terbaca sebagai tulisan AI atau terjemahan, dan kembali ke gaya penulis. Juga untuk mengaudit b… | Writing & Language (ID) |
| `technical-writer` | Write, review, and edit developer documentation for SDKs, libraries, and frameworks, including sites such as agent-browser.dev and portless… | Writing & Language (ID) |
| `akuntansi-umkm` | Use when the user needs bookkeeping for a small business (UMKM) — pencatatan kas masuk/keluar, jurnal sederhana, buku besar, neraca saldo,… | Finance & Business (ID) |
| `analisis-laporan-keuangan` | Use when the user wants to analyze financial statements (laporan keuangan) — rasio likuiditas, solvabilitas, profitabilitas, efisiensi, ana… | Finance & Business (ID) |
| `keuangan-pribadi` | Use when the user wants personal finance help — budgeting (anggaran bulanan), dana darurat, pelunasan utang, tujuan tabungan, arus kas ruma… | Finance & Business (ID) |
| `pajak-dasar-id` | Use when the user asks basic Indonesian tax questions — konsep PPh orang pribadi, NPWP/NIK, SPT Tahunan, bukti potong, kewajiban pajak UMKM… | Finance & Business (ID) |
| `laporan-generator` | Menulis, menyunting, dan memformat dokumen akademik berbahasa Indonesia dari bahan mentah sampai PDF dan DOCX: skripsi, tesis, tugas akhir,… *(Includes an "audit kesehatan" (health audit) of a *document* — not medical.)* | College & Academic |
| `naskah-id` | Menulis dan menyunting karya ilmiah berbahasa Indonesia yang natural, baku (EYD V, KBBI), dan jujur: artikel jurnal SINTA, prosiding, skrip… *(Also serves academic writing (ID).)* | College & Academic |
| `penulis-ilmiah` | Drafts formal scientific prose in Indonesian or English from notes the author already has. | College & Academic |
| `smartbook-ingest` | Compile reusable books, semester modules, manuals, or documentation into a local SmartBook under the resolved SmartDoc root. Use to create,… *(Semester modules / books.)* | College & Academic |
| `deep-research` | Synthesizes a question across sources, separating claims, evidence, and gaps. | Research |
| `research` | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants… | Research |
| `audit` | a user-authored audit skill *(Empty stub — SKILL.md contains only frontmatter + "Not pinned".)* | Other |
| `brainstorming` | You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning… *(Generic creative-thinking workflow (from obra/superpowers).)* | Other |
| `platformio` | Bangun, flash, dan monitor firmware PlatformIO/Arduino/ESP32: validasi proyek, diagnosa build terstruktur, audit pin GPIO, flash + verifika… *(Embedded firmware (ESP32/Arduino), not web full-stack.)* | Other |

## Health & Medical — finding (verified by grep on the clone)

- **0 dedicated health/medical skills** in the core 156 and in all 12 packs (no pack dir name matches health/medical/FHIR/clinical terms).
- No `FHIR` string anywhere in `.opencode/` or `packs/`.
- The only "health" hits are false positives: `laporan-generator` has a *document* health-audit command
  (`laporan doctor` = audit the report, not a person); `naskah-id` lists PubMed only as a *source* for scientific
  writing; `design-assets` / `floorplan` / `hunt-csrf` use "health-check" / `/api/health` for code and services.
- Conclusion: Health & Medical is a genuine gap in Lumitome — it must be filled from outside (research-only,
  health-informatics) or by a new original skill with a strict no-clinical-decision guardrail.

## Packs (12) — registry counts vs dir counts, with samples

Registry counts are authoritative (from `router/skills-registry.json`); dir counts are what exists on disk
(nested variants included). Samples are the first 12 names alphabetically from each pack.

| Pack | Registry | Dirs | What it holds (samples) |
|---|---:|---:|---|
| `3d` | 96 | 97 | `3dviz-pro-max`, `analog-found-footage-horror`, `animation`, `anime-style`, `apocalypse-worlds`, `archviz`, `asset-optimization`, `biome-worlds`, `blender-director`, `blender-modeler`, `body-horror-style`, `brutalist-mood` (+85 more) |
| `cad` | 30 | 30 | `bambu-labs`, `cad`, `cad-skill`, `dfam-check`, `dfm`, `dxf`, `engineering-drawing`, `gcode`, `sdf`, `sendcutsend`, `solidcraft-agent-tools`, `solidcraft-checking` (+18 more) |
| `career-extra` | 2 | 2 | `brag`, `brag-slim` (+-10 more) |
| `coding-extra` | 32 | 33 | `agent-dx-cli-scale`, `codegen`, `core`, `devtools`, `devtools-react`, `devtools-solid`, `devtools-svelte`, `devtools-vue`, `directives`, `hackathon-winner-thinking`, `honey`, `image` (+21 more) |
| `design-extra` | 28 | 58 | `anatomy`, `animate`, `animate-expo`, `animation-performance`, `animation-vocabulary`, `apple-design`, `ask-sonner`, `banner-design-2`, `brand-2`, `break-ui`, `design-2`, `design-system-2` (+46 more) |
| `gamedev` | 100 | 126 | `ai-behavior-trees-utility-ai`, `asset-pipeline`, `asset-pipeline-2`, `asset-pipeline-3`, `audio-design`, `bevy-ecs`, `blitz3d-decomp`, `blitz3d-decomp-2`, `blitz3d-decomp-3`, `camera-systems`, `card-game`, `create-game-assets` (+114 more) |
| `misc` | 102 | 107 | `academy-guide`, `algorithmic-art`, `architect`, `arena`, `ask-matt`, `automate-me`, `benchmark-checklist`, `blast-radius`, `brand-guidelines`, `bro`, `canvas-design`, `chief-of-staff` (+95 more) |
| `motion` | 62 | 62 | `animate-video`, `anime-cel`, `blender-product-film`, `canopy-part-title`, `captions-overlay`, `changelog-video`, `code-slice-hero`, `crayon-storybook`, `cuboid-carousel`, `cut-the-curve`, `directing-stickman-videos`, `embedded-captions` (+50 more) |
| `osint-extra` | 1 | 1 | `geo-sleuth` (+-11 more) |
| `penulisan` | 42 | 42 | `brand-copy`, `budget-planner`, `business-plan`, `business-report`, `campaign-planner`, `contract-drafter`, `course-slides`, `data-analyst`, `data-cleaning`, `email-drafter`, `executive-deck`, `expense-report` (+30 more) |
| `red-team` | 166 | 168 | `api-security`, `apk-reverse`, `apk-reverse-2`, `attack-chain`, `binary-diff`, `binary-ninja-reverse`, `browser-automation`, `browser-extension-reverse`, `case-review`, `cloud-k8s`, `competition-ad-certificate-abuse`, `competition-agent-cloud` (+156 more) |
| `seo` | 113 | 115 | `ads`, `ads-amazon`, `ads-apple`, `ads-attribution`, `ads-audit`, `ads-budget`, `ads-competitor`, `ads-create`, `ads-creative`, `ads-dna`, `ads-generate`, `ads-google` (+103 more) |

Pack notes:
- **`red-team` (166 registered / 168 dirs) stays DISABLED by design** (README, since v0.3.27: "one corpus, no dormant packs").
  It is offensive-security content (reverse engineering, exploit chains, APK/binary reversing). It must NOT be
  recommended for muse-rsi. The defensive subset already in core (`hunt-*`, `code-audit`, `owasp-security`,
  `security-audit`, `fp-check`, `triage-validation`, `cvss-scoring`, `redteam-mindset`) is the only security material to link.
- **`penulisan` (42)** is the Indonesian writing/business pack: `brand-copy`, `business-plan`, `business-report`,
  `contract-drafter`, `course-slides`, `data-analyst`, `budget-planner`, `campaign-planner` — relevant to Office,
  College and Finance domains, but pack skills are not in the core registry list above.
- **`misc` (102)** is mixed: `academy-guide`, `architect`, `automate-me`, `benchmark-checklist`, `blast-radius`, …
  — contains office/academic-adjacent skills worth a second pass when expanding those domains.
- **`coding-extra` (32)** extends the core dev skills (`codegen`, `devtools`, `devtools-react/vue/svelte/solid`, …).
- **`career-extra` (2)** is just `brag` / `brag-slim` (career brag documents). **`osint-extra` (1)** is `geo-sleuth`.
- **`seo` (113)** is ads/SEO content (`ads`, `ads-amazon`, `ads-audit`, …) — overlaps the muse-rsi SEO/GEO gap filler.

## Other skill locations in the repo

- `.opencode/` also has `agents/`, `commands/`, `plugins/`, `rules/` and `lumitome-subagent.json` (not mapped here —
  they are agent/command/plugin definitions, not `SKILL.md` skills).
- `config/mcp-gateway` exists (MCP gateway config). No top-level `skills/` folder.
- `docs/` holds project docs (not a skill registry).

## Gaps for the muse-rsi expansion (summary)

| Target domain | Lumitome core | Verdict for muse-rsi |
|---|---|---|
| Full-Stack Development | 31 | STRONG — link the core dev skills as reference; add external QA/Next.js/React packs after re-check |
| DevOps & Infra | 8 | THIN — external DevOps repos (fully verified) are the main fill |
| Agent & Orchestration | 28 | STRONG — EGM, subagents, MCP, eval harness already covered |
| Office & Corporate | 5 | THIN — external office repos + `penulisan` pack need a second pass |
| College & Academic | 4 | THIN — academic writing (ID) only; external academic repos (fully verified) are the main fill |
| Research | 2 | THIN — `deep-research` + `research` only; 5 external research repos verified via web 20 Nov 2026 and promoted |
| Health & Medical | 0 | MISSING — 7 external research-only repos verified via web 20 Nov 2026 and promoted, plus new original skill `health-research-literacy` with guardrails |
| Security | 30 | STRONG (defensive) — link defensive subset only; never the red-team pack |
| Design & Media | 36 | STRONG — already the biggest core domain |

