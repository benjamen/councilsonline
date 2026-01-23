# CouncilsOnline - Claude Code Instructions

## Quick Context
Philippine council services platform (forked from Lodgeick). Key focus: SPISC applications, auto-confirm bookings, config packs.

## Token Optimization
- **Read first**: `.claude/PROJECT_MEMORY.md` for full context
- **Skip**: `docs/`, `node_modules/`, `*.test.js`
- **Use memory MCP**: Search before reading large files

## Key Paths
| Area | Path |
|------|------|
| API | `councilsonline/api/` |
| DocTypes | `councilsonline/councilsonline/doctype/` |
| Fixtures | `councilsonline/fixtures/` |
| Frontend | `frontend/src/` |

## Common Commands
```bash
# Site operations
bench --site councilsonline.localhost migrate
bench --site councilsonline.localhost console

# Config packs
bench --site councilsonline.localhost list-config-packs
bench --site councilsonline.localhost install-config-packs --pack ph_social_services

# Frontend dev
cd frontend && npm run dev
```

## Current Features
- SPISC 5-step wizard with payment method selection
- Auto-confirm for appointments (Council Team) and meetings (Request Type)
- Config packs system for modular fixtures
- Section visibility via `depends_on` expressions

## Code Style
- Python: Frappe conventions, `frappe.db.get_value()`, `frappe.throw()`
- Vue 3: Composition API, Pinia stores
- No emojis in code
