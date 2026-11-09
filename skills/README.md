# Agent Skills by Fast Data

Ready-to-use **Agent Skills** for AI agents (Claude and other agents that support the open `SKILL.md` format) that solve one concrete business task in **sales or finance for Germany/EU**: check an incoming e-invoice, verify a supplier, find public tenders for your industry, watch a competitor's hiring.

Each skill is one folder with a `SKILL.md` (instructions + when to use it) and, where useful, small helper files. The skills call public, pay-per-result [Apify](https://apify.com) Actors by **Fast Data** ([apify.com/fast_data_asap](https://apify.com/fast_data_asap)) through Apify's MCP server or API. Disclosure: we build and maintain these Actors; the skills are free.

## How to use

1. Connect the Fast Data tools to your agent via MCP (see [../mcp/README.md](../mcp/README.md)).
2. Copy a skill folder into your agent's skills directory (e.g. `~/.claude/skills/` for Claude Code) or upload it where your agent supports custom skills.
3. Ask your agent for the task in plain language.

## Skills

| Skill | Task | Tools used |
|---|---|---|
| [find-public-tenders](find-public-tenders/SKILL.md) | Find open public tenders in Germany and the EU, ranked by deadline | `german-public-tenders-bund`, `eu-tenders-ted-api` |

Format rules for contributors: [FORMAT.md](FORMAT.md).
