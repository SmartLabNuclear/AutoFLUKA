# AutoFLUKA skill policy

This document defines how AutoFLUKA loads **bundled** skills from `<app>/fluka_skills/` and **additive user-defined** skill packs from the Settings **User skills path** (or `AUTOFLUKA_SKILLS_DIR`).

Bundled content is **never replaced** by configuring a user path—that path only **stacks** extra packs on top.

## Tiers

### Tier 0 — Global policy (always on)

- `core/SKILL.md` — short must-follow rules, injected first on every turn (keep it under ~2,000 characters)
- `SKILL.md` — global FLUKA workflow contract and skills map

Each turn's skill text has a character budget (20,000 in the normal preset) and per-file caps. A file that does not fit is cut at a line break and ends with where to read the rest (`SkillLookupTool('<pack>')` or a file path); routed files that got no room are listed under "Skills not fully loaded this turn". Put each file's must-follow rules near its top. The troubleshooting lane injects the KB entries that match the request, not the start of `Error_Resolution_KB.md`.

Optional: a root `SKILL.md` directly under your **user skills path** loads as an **addon global contract** after tier-0 bundled content.

Each bundled module uses a single canonical **`SKILL.md`** entrypoint. Auxiliary `.md` files (guides, examples, rules) load only via **Extended discovery** (query-ranked excerpts) or on-demand tools (`SkillLookupTool`, `text_file_reader_tool`).

**Subroutines** (`fluka_subroutines/SKILL.md`) is the router for all user Fortran routines; per-routine `*_GUIDE.md` and `examples/*.md` are auxiliary files under that tree.

### Tier 1 — Bundled modules (Settings checkboxes; Full context preset)

| Module | Folder | Purpose |
|--------|--------|---------|
| Authoring | `fluka-authoring/` | `.inp` creation, rules, templates |
| Execution | `fluka-execution/`, `fluka-troubleshooting/` | Runs, logs, ERKB-style troubleshooting |
| Post-processing | `fluka-post-processing/` | Decrypt, plots, reports, structured JSON |
| Working examples | `working_examples/` | Validated templates and README-style notes |
| Subroutines | `fluka_subroutines/` | User Fortran (`source_newgen.f`, etc.) |

All bundled modules are **on by default** in Full context. **Chat only** preset disables tier-1 bundled lanes (tier-0 bundled still loads).

### Tier 2 — User-defined skill packs (additive)

Point **User skills path** at a folder containing one subdirectory per pack:

```text
GenAI_FrameWorkTests/Skills/
  MermaidDiagrams/
    SKILL.md
    reference/
    scripts/
  Reviewer/
    SKILL.md
    DEFAULT_RUBRIC.md
```

Each pack requires `SKILL.md`. Optional YAML frontmatter (see below).

User addon packs are **query-ranked** and load **even in Chat only** when the query matches pack name, description, or body tokens. Bundled tier-1 lanes still require FLUKA intent + enabled modules.

## YAML frontmatter (`SKILL.md`)

AutoFLUKA recognizes only these scalar keys in the opening `---` block:

```yaml
---
name: Human-readable pack title
description: One sentence describing when AutoFLUKA should load this pack.
skills_build: YYYY-MM-DD   # bundled fluka_skills/SKILL.md only -- see "Bundle version & license" below
---
```

Rules:

- **`name`** and **`description`** are required on registered bundled entrypoints and **strongly recommended** on user packs (routing uses slug, description, path tokens, and body).
- Frontmatter is **metadata only**. It does not control execution, tool invocation, safety policy, or routing overrides.
- The loader parses **scalar `key: value` lines only**; complex YAML stays in the body and has no routing authority.

## User skill pack layout

```text
<user_skills_path>/
  <pack_slug>/
    SKILL.md            (* required)
    reference/          (optional helper .md files)
    scripts/            (optional; not auto-executed)
    requirements.txt    (optional pip notes for script workflows)
```

**Pack slug:** lowercase letters, digits, hyphens (`[a-z0-9-]`), 3–40 characters, start/end with letter or digit.

Use `{PACK_ROOT}` in `SKILL.md` as a portable placeholder for the pack directory (e.g. `{PACK_ROOT}/scripts/render_mermaid.py`). When following a skill, resolve `{PACK_ROOT}` to the absolute path of that pack folder before calling file or REPL tools.

In `system_prompt_autofluka.yml`, write `{{PACK_ROOT}}` (doubled braces) so LangChain does not treat it as a prompt input variable.

## SKILL.md body contract (recommended)

1. **Scope** — cases, assumptions, prerequisites
2. **When to use** — query phrases that should trigger this pack
3. **Guidance** — concise rules, checklists, file expectations
4. **Limits** — what this pack does not override (bundled policy, safety)
5. **Evidence** (optional) — paths to validated inputs or logs in the working directory

Keep packs focused. Pre-loaded bodies are truncated by char budgets (`normal` / `large` / `unlimited` in Settings).

## How the agent consults skills and auxiliary files

When skills load for a request, AutoFLUKA uses this unified phrasing:

- Consulting: Global Workflow Skills
- Consulting: Authoring Skills
- Consulting: `<user_pack_name>` Skills

The loader prepends a matching bulleted summary to injected skill context. The agent should reuse the same phrasing in reasoning traces when skills guide the task.

**Auxiliary file access:**

- **Query-ranked `SKILL.md`** — top matching user pack entrypoints when the user skills path is set and the query matches
- **Extended discovery** (Settings toggle) — extra `.md` helpers under the user or bundled tree; query-ranked; capped by budget
- **`text_file_reader_tool`** — explicit reads of paths listed in `SKILL.md`, `reference/`, templates, rules, `.inp`, `.yaml`, `.json`, `.md`, etc.
- **`python_repl_tool`** — scripts under `scripts/` only when `SKILL.md` instructs; never auto-run

**Not auto-injected:** `.py`, `.inp`, `.f`, binaries, images. Describe them in `SKILL.md` so the agent reads or runs them via tools.

**Bundled helpers:** module folders use relative paths in skill bodies (e.g. `fluka-authoring/rules/*.md`, `working_examples/`). With tier-1 modules on and matching FLUKA intent, the loader injects ranked bundled slices; otherwise use `text_file_reader_tool` on paths under `<app>/fluka_skills/`.

## Precedence

If instructions conflict:

1. System prompt and safety guardrails
2. Bundled `fluka_skills/` (tier-0 + enabled tier-1 modules)
3. User addon packs (tool-use workflow rules are **binding for that skill's task**)
4. Generic model heuristics

User packs cannot override safety, disclosure, or core FLUKA workflow policy.

## When to create a user skill

Create a user skill when:

- You repeat the same FLUKA or research guidance across sessions
- You have facility- or project-specific conventions not in bundled skills
- You validated a troubleshooting or post-processing pattern worth reusing

Do **not** create a user skill for one-off answers, unvalidated failed runs, or secrets/credentials.

## Bundled skill metadata and registration

- Bundled registered modules use the same frontmatter schema as user packs.
- Dropping a new top-level folder under `fluka_skills/` does **not** make it a routable bundled module until its slug is registered in `utils/skill_loader.py` (`FLUKA_AVAILABLE_SKILL_MODULES` / module map).
- Unregistered bundled folders are discovered, warned, and **inert** for auto-routing.

## Vendored packs inside the repo

You may also keep notes under `fluka_skills/user_defined_skills/<pack>/SKILL.md` inside the app tree; those follow bundled discovery allowlists.

## Docker and paths

| Environment | Bundled skills | User skills path | Working directory |
|-------------|----------------|------------------|-------------------|
| Local dev | repo `fluka_skills/` | host path in Settings | case folder |
| Docker | image `/autofluka/fluka_skills` (+ optional mount) | mount e.g. `/skills` | mount e.g. `/workdir` |

Use container paths inside Docker, host paths on native Windows/Linux/WSL.

## Bundle version & license

The bundled `fluka_skills/` tree carries a single version stamp for the **entire tree, all subdirectories included** — not one per module. There is no per-folder or per-file version; `fluka-authoring/SKILL.md`, `fluka-execution/SKILL.md`, and every other bundled file are all covered by the one stamp below, the same way a single Docker image tag covers every layer inside it.

- **Current build**: see `skills_build` in the top-level `fluka_skills/SKILL.md` frontmatter (always loaded, so the agent itself can report it).
- **Per-file integrity**: `fluka_skills/MANIFEST.json` records a sha256 hash of every bundled file as of that same build, generated by `maintenance_scripts/generate_skill_manifest.py`. Re-run that script (and bump `skills_build` to match) every time any file under `fluka_skills/` changes — see `maintenance_scripts/check_skill_manifest_freshness.py` for the enforced check.
- **Enforcement in the AutoFLUKA-MS repo**: a pre-commit hook blocks committing a `fluka_skills/` change without a matching manifest regeneration. One-time setup per clone: `git config core.hooksPath .githooks`.
- **A regenerated manifest does not transfer across a CRLF/LF boundary.** Git's `.gitattributes` (`eol=lf`) normalizes line endings on checkout/commit, which changes a file's hash even when its content is otherwise identical — so a manifest generated against one `fluka_skills/` copy will not verify a different copy that went through that normalization (e.g. this repo's copy vs. dev root's). Regenerate directly against each tree (`generate_skill_manifest.py --root <path>`) rather than copying `MANIFEST.json` between them.
- **License**: TBD. Not yet decided for this bundle's own authored content (rules, templates, working examples, `SKILL.md`/`SKILL_POLICY.md` files). This is separate from, and does not change, the narrower licensing note in `fluka-user-manual-and-relevant-guides/README.md`, which only disclaims bundling third-party FLUKA/FLAIR manual content — that note stands on its own regardless of how this bundle's own license is eventually decided.

## Security

- User-defined skill files are scanned before injection. Content that does not pass is blocked and surfaced in **Alerts**.
- Do not place secrets, credentials, or prompt-injection payloads in user packs.
- When explaining a blocked pack, describe the **content concern**, not the scanning mechanism.

## User template

Copy [`user_defined_skills/_template/SKILL.md`](user_defined_skills/_template/SKILL.md) into a new folder under your **User skills path** and edit the body.

## Skill loading roadmap

Today AutoFLUKA **pre-loads** query-ranked user packs and enabled bundled module lanes into skill context at query time. **On-demand `SkillLookupTool` with catalog injection** is planned for a future release so the agent can fetch pack entrypoints and auxiliary files only when a task requires them.
