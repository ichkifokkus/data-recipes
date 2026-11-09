# Skill format rules (Fast Data skill pipeline)

Researched 2026-11-09 from the open Agent Skills specification (agentskills.io/specification) and
Anthropic's Agent Skills documentation. Every skill in this folder follows these rules.

## Folder layout

```
skills/<name>/
├── SKILL.md          # required: YAML frontmatter + instructions
├── references/       # optional: longer docs the agent loads only when needed
├── scripts/          # optional: small helper scripts (none that need secrets in the repo)
└── assets/           # optional: templates, example inputs/outputs
```

- The folder name **must equal** the `name` field.

## Frontmatter (YAML between `---` lines at the very top)

| Field | Rule |
|---|---|
| `name` | required; max 64 chars; lowercase letters, digits and hyphens; no leading/trailing or double hyphens; must not contain "anthropic" or "claude" |
| `description` | required; non-empty; max 1024 chars; third person; says **what** the skill does **and when** to use it (trigger words the user would actually say) |
| `license` | optional; we use `MIT` |
| `metadata` | optional key/value map; we use `author: fast-data`, `version`, `tested` |
| `compatibility` / `allowed-tools` | optional; only if needed |

## Body

- Keep SKILL.md under ~500 lines / ~5,000 tokens (progressive disclosure: put long material in `references/`).
- Sections we always use: **When to use**, **Tools**, **Steps**, **Output format**, **Limits**, **Cost**, **Tested**, **Disclosure**.
- Use the exact Actor IDs (`fast_data_asap/<actor>`) and exact input field names from the live input schemas.
- Prices only as published on the Actor page on the test date.
- Never: legal, tax or investment advice; collecting personal data (names, emails, phones of individuals); bypassing logins or anti-bot measures.

## Quality gate

A skill is only committed if every Actor call it describes was run once for real (256 MB, smallest input) and the field
names in the skill match the actual output. The date goes into the **Tested** section.
