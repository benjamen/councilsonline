# CouncilsOnline Project Memory

## Project Overview
**CouncilsOnline** is a council services platform built on Frappe Framework for Philippine local government units (LGUs). Forked from Lodgeick (NZ lodge management), adapted for Philippine social services workflows.

## Architecture

### Backend
- **Framework**: Frappe Framework (Python)
- **Database**: MariaDB
- **Site**: councilsonline.localhost (dev), councilsonline.com (prod)
- **API**: REST endpoints in `councilsonline/api/`

### Frontend
- **Framework**: Vue 3 (Composition API)
- **State Management**: Pinia
- **UI Library**: frappe-ui
- **Build Tool**: Vite
- **Location**: `frontend/src/`

## Key Features (Philippine-Specific)

### 1. SPISC (Social Pension for Indigent Senior Citizens)
- 5-step application wizard
- Payment method selection (Bank Transfer / Office Pickup)
- Auto-confirmation for appointments
- Request Type Code: `SPISC`

### 2. Configuration Packs System
- Modular fixture installation
- Region-specific data packs (NZ, Philippines)
- Commands: `bench install-config-packs`, `bench list-config-packs`

### 3. Auto-Confirm Features
- **Team Appointments**: `Council Team.auto_confirm_appointments`
- **Council Meetings**: `Request Type.auto_confirm_meetings`
- Skips manual approval workflow when enabled

## Important Files

### Backend API
```
councilsonline/councilsonline/api/
├── requests.py        # Request CRUD, get_request_type_config()
├── scheduling.py      # Team appointment booking, auto-confirm
├── meetings.py        # Council meeting booking, auto-confirm
└── auth.py            # Authentication endpoints
```

### DocTypes
```
councilsonline/councilsonline/councilsonline/doctype/
├── request/               # Main application document
├── request_type/          # Configures form steps/fields (has auto_confirm_meetings)
├── council_team/          # Team config (has auto_confirm_appointments)
├── scheduled_appointment/ # Booked time slots
└── council_meeting/       # Meeting requests
```

### Fixtures
```
councilsonline/councilsonline/fixtures/
├── packs/                 # Config pack system
│   ├── base/             # Always installed (roles, workflows)
│   ├── nz_resource_consent/
│   └── ph_social_services/
└── taytay/               # Taytay council specific
    └── spisc_request_type.json
```

### Frontend Components
```
frontend/src/
├── components/
│   ├── forms/
│   │   ├── DynamicStepRenderer.vue   # Renders form steps
│   │   ├── DynamicFieldRenderer.vue  # Renders individual fields
│   │   └── fields/
│   │       ├── PickupScheduleField.vue  # Office pickup booking
│   │       └── BookSlotModal.vue        # 3-step appointment booking
│   └── RequestWizard.vue             # Main wizard container
├── stores/
│   └── request.js                    # Request state management
└── views/
    └── RequestFormView.vue           # Form view wrapper
```

## Critical Code Patterns

### 1. Section Visibility (depends_on)
The API must include `depends_on` for sections in `get_request_type_config()`:
```python
# requests.py line ~1354
section_data = {
    "section_code": section.section_code,
    "depends_on": section.depends_on if hasattr(section, 'depends_on') else None,
    # ...other fields
}
```

### 2. Auto-Confirm Logic (scheduling.py)
```python
# After appointment.insert()
team_doc = frappe.get_doc("Council Team", team.name)
if team_doc.auto_confirm_appointments:
    appointment.status = "Confirmed"
    appointment.confirmed_at = now_datetime()
    appointment.save(ignore_permissions=True)
```

### 3. Auto-Confirm Logic (meetings.py)
```python
# After meeting_doc.insert()
if request_type_doc.auto_confirm_meetings and preferred_time_slots:
    first_slot = preferred_time_slots[0]
    meeting_doc.scheduled_start = first_slot.get("preferred_start")
    meeting_doc.scheduled_end = first_slot.get("preferred_end")
    meeting_doc.status = "Confirmed"
    meeting_doc.confirmed_at = now_datetime()
    meeting_doc.save(ignore_permissions=True)
```

## Development Workflow

### Starting Development
```bash
# Backend (in Docker container)
cd /workspace/development/frappe-bench && bench start

# Or serve specific site
bench --site councilsonline.localhost serve --port 8000

# Frontend
cd /workspace/development/frappe-bench/apps/councilsonline/frontend
npm run dev
```

### Database Operations
```bash
bench --site councilsonline.localhost migrate
bench --site councilsonline.localhost console
bench --site councilsonline.localhost mariadb
bench --site councilsonline.localhost clear-cache
```

### Config Pack Commands
```bash
bench --site councilsonline.localhost list-config-packs
bench --site councilsonline.localhost install-config-packs --pack ph_social_services
bench --site councilsonline.localhost show-config-pack ph_social_services
```

## Recent Changes (Jan 2026)

### Auto-Confirm Feature
- Added `auto_confirm_appointments` to Council Team DocType
- Added `auto_confirm_meetings` to Request Type DocType
- Implemented auto-confirm logic in scheduling.py and meetings.py
- Database migrated with new columns

### SPISC Payment Method Step
- Added Bank Transfer and Office Pickup options
- Section visibility controlled by `depends_on` expressions
- Uses PickupScheduleField for office pickup booking

### Config Packs System
- Modular fixture installation
- Supports NZ and Philippine configurations
- Custom bench commands for pack management

## Known Issues & Solutions

### Issue: Sections not hiding based on depends_on
**Cause**: API not returning `depends_on` for sections
**Fix**: Add `depends_on` to section_data in requests.py:1354

### Issue: Office pickup uses manual fields
**Solution**: Use PickupScheduleField component with PAYMENTS team

## Environment URLs

| Environment | Backend | Frontend |
|-------------|---------|----------|
| Development | localhost:8000 | localhost:8080 |
| Production | councilsonline.com | councilsonline.com |

## Differences from Lodgeick

| Feature | Lodgeick | CouncilsOnline |
|---------|----------|----------------|
| Target Market | NZ Councils | Philippine LGUs |
| Request Types | Resource Consent, Building | SPISC, Senior Aid |
| Auto-Confirm | No | Yes |
| Config Packs | No | Yes |
| Pickup Scheduling | Municipal Treasury | DSWD Offices |

## Git Workflow
- Main development branch: `main`
- Feature branches: `feature/*`
- Commits follow conventional format: `feat:`, `fix:`, `refactor:`

---

**Last Updated**: 2026-01-23
**Status**: Active Development
