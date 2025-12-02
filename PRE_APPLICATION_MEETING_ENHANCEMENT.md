# Pre-Application Meeting Enhancement Documentation

## Overview

Enhanced the Pre-Application Meeting feature with a complete workflow for time slot preferences, planner responses, and attendee management. The system now supports:

1. **Applicant selects 3 preferred meeting times** using calendar/time pickers
2. **Add attendees from contacts** with a professional contact selector
3. **Planner workflow** to accept, decline, or propose alternative times
4. **Automated notifications** for all state changes
5. **End-to-end meeting scheduling** with draft event management

## Architecture

### Backend Components

#### New Child DocTypes

**1. Meeting Preferred Time Slot** (`meeting_preferred_time_slot`)
- **Location**: `lodgeick/lodgeick/doctype/meeting_preferred_time_slot/`
- **Purpose**: Store applicant's preferred meeting times with planner responses
- **Fields**:
  - `preference_order` (Int): 1, 2, or 3
  - `preferred_start` (Datetime): Applicant's preferred start time
  - `preferred_end` (Datetime): Applicant's preferred end time
  - `planner_response` (Select): Pending | Accepted | Declined | Proposed Alternative
  - `planner_notes` (Small Text): Notes from planner
  - `alternative_start` (Datetime): Planner's proposed alternative start
  - `alternative_end` (Datetime): Planner's proposed alternative end

**2. Meeting Attendee** (`meeting_attendee`)
- **Location**: `lodgeick/lodgeick/doctype/meeting_attendee/`
- **Purpose**: Store additional meeting attendees (contacts)
- **Fields**:
  - `attendee_name` (Data): Full name *
  - `attendee_email` (Data): Email address *
  - `attendee_phone` (Data): Phone number
  - `organization` (Data): Company/organization
  - `role` (Data): Role/title

#### Enhanced Pre-Application Meeting DocType

**New Fields Added**:
- `preferred_time_slots` (Table): Child table for Meeting Preferred Time Slot
- `meeting_attendees` (Table): Child table for Meeting Attendee
- Replaced `additional_attendees` (Small Text) with structured table

**Field Order Changes**:
- Added "Preferred Time Slots" section after meeting details
- Shows only when status is "Requested"
- Restructured attendees section to use child table

#### API Endpoints

**File**: `pre_application_meeting.py`

All endpoints decorated with `@frappe.whitelist()` for frontend access:

1. **`accept_time_slot(meeting_id, slot_index)`**
   - Planner accepts one of the applicant's preferred times
   - Schedules the meeting automatically
   - Declines other time slots
   - Sends confirmation email to applicant
   - Returns: `{success: True, message: str, meeting: dict}`

2. **`decline_time_slot(meeting_id, slot_index, planner_notes=None)`**
   - Planner declines a specific time slot
   - Optional notes explaining why
   - Checks if all slots are declined
   - Returns: `{success: True, message: str, all_declined: bool, meeting: dict}`

3. **`propose_alternative_time(meeting_id, slot_index, alternative_start, alternative_end, planner_notes=None)`**
   - Planner proposes alternative time for a slot
   - Sends notification email to applicant
   - Applicant can then accept or reject
   - Returns: `{success: True, message: str, meeting: dict}`

4. **`accept_alternative_time(meeting_id, slot_index)`**
   - Applicant accepts planner's proposed alternative
   - Schedules meeting with alternative time
   - Sends confirmation email
   - Returns: `{success: True, message: str, meeting: dict}`

5. **`send_alternative_time_notification(meeting, slot_index)`**
   - Helper function to send emails
   - Shows original requested time vs proposed alternative
   - Includes planner's notes

### Frontend Components

#### New Reusable Components

**1. ContactSelector** (`components/common/ContactSelector.vue`)
- **Location**: `frontend/src/components/common/ContactSelector.vue`
- **Purpose**: Modal for selecting existing contacts or adding new ones
- **Features**:
  - Tab interface: "Existing Contacts" | "Add New Contact"
  - Search existing contacts by name, email, or organization
  - Add new contact form with all fields
  - "Save to contacts" checkbox for new contacts
  - Returns selected contact via `@select` event
- **Props**:
  - `isOpen` (Boolean): Control modal visibility
  - `existingContacts` (Array): List of available contacts
- **Events**:
  - `@close`: User closes modal
  - `@select`: User selects/creates contact

**2. DateTimePicker** (`components/common/DateTimePicker.vue`)
- **Location**: `frontend/src/components/common/DateTimePicker.vue`
- **Purpose**: Calendar and time picker for meeting slots
- **Features**:
  - Date picker with minimum date validation (default: tomorrow)
  - Time picker with quick presets (9 AM - 4 PM)
  - Live preview of formatted date/time
  - v-model binding for easy integration
- **Props**:
  - `modelValue` (String): ISO datetime string
  - `label` (String): Field label
  - `required` (Boolean): Required validation
  - `showPresets` (Boolean): Show quick time buttons
  - `minDate` (String): Minimum selectable date
- **Events**:
  - `@update:modelValue`: Datetime changed

#### Component Integration

These components will be integrated into the Pre-Application Meeting modal (future task) to provide:
- Selection of 3 preferred time slots using DateTimePicker
- Adding attendees using ContactSelector
- Displaying planner responses for each slot
- Accepting alternative times proposed by planner

## User Workflows

### Workflow 1: Applicant Requests Meeting

```
1. Applicant clicks "Request Pre-Application Meeting"
2. Modal opens with DateTimePicker components
3. Select 1st preferred time → Add to slot #1
4. Select 2nd preferred time → Add to slot #2
5. Select 3rd preferred time → Add to slot #3
6. Click "Add Attendee" → ContactSelector opens
7. Search/select existing contact OR add new contact
8. Contact added to attendees list
9. Repeat for all attendees
10. Fill meeting purpose and discussion points
11. Click "Request Meeting"
12. System creates Pre-Application Meeting with status="Requested"
13. Creates draft Event in calendar
14. Sends notification to planner
```

### Workflow 2: Planner Reviews and Responds

```
1. Planner receives notification
2. Opens meeting request
3. Views 3 preferred time slots

Option A - Accept a Time Slot:
4a. Clicks "Accept" on slot #2
5a. API: accept_time_slot(meeting_id, 1)
6a. Meeting scheduled with that time
7a. Other slots marked as "Declined"
8a. Applicant receives confirmation email
9a. Status changes to "Scheduled"

Option B - Decline and Propose Alternative:
4b. Clicks "Decline" on slot #1
5b. Clicks "Propose Alternative" on slot #2
6b. Opens DateTimePicker to select alternative time
7b. Adds planner notes explaining why
8b. API: propose_alternative_time(meeting_id, 1, alt_start, alt_end, notes)
9b. Applicant receives notification email
10b. Slot shows "Proposed Alternative" status

Option C - Decline All:
4c. Clicks "Decline" on all 3 slots
5c. Adds notes explaining conflicts
6c. System detects all_declined=True
7c. Applicant notified to propose new times
```

### Workflow 3: Applicant Responds to Alternative

```
1. Applicant receives email notification
2. Opens meeting request
3. Sees slot with "Proposed Alternative"
4. Reviews proposed time and planner's notes

Option A - Accept Alternative:
5a. Clicks "Accept Alternative Time"
6a. API: accept_alternative_time(meeting_id, slot_index)
7a. Meeting scheduled with alternative time
8a. Confirmation email sent
9a. Status changes to "Scheduled"

Option B - Reject and Propose New:
5b. Clicks "Propose Different Time"
5c. Back to Workflow 1 (request new meeting)
```

## Database Schema

### New Tables Created

**`tabMeeting Preferred Time Slot`**
```sql
CREATE TABLE `tabMeeting Preferred Time Slot` (
  `name` VARCHAR(140) PRIMARY KEY,
  `parent` VARCHAR(140),  -- Link to Pre-Application Meeting
  `parenttype` VARCHAR(140),
  `parentfield` VARCHAR(140),
  `preference_order` INT NOT NULL,
  `preferred_start` DATETIME NOT NULL,
  `preferred_end` DATETIME NOT NULL,
  `planner_response` VARCHAR(140) DEFAULT 'Pending',
  `planner_notes` TEXT,
  `alternative_start` DATETIME,
  `alternative_end` DATETIME,
  `creation` DATETIME,
  `modified` DATETIME,
  INDEX `parent_idx` (`parent`)
);
```

**`tabMeeting Attendee`**
```sql
CREATE TABLE `tabMeeting Attendee` (
  `name` VARCHAR(140) PRIMARY KEY,
  `parent` VARCHAR(140),  -- Link to Pre-Application Meeting
  `parenttype` VARCHAR(140),
  `parentfield` VARCHAR(140),
  `attendee_name` VARCHAR(140) NOT NULL,
  `attendee_email` VARCHAR(140) NOT NULL,
  `attendee_phone` VARCHAR(140),
  `organization` VARCHAR(140),
  `role` VARCHAR(140),
  `creation` DATETIME,
  `modified` DATETIME,
  INDEX `parent_idx` (`parent`),
  INDEX `email_idx` (`attendee_email`)
);
```

### Modified Tables

**`tabPre-Application Meeting`**
- Added field: `preferred_time_slots` (points to Meeting Preferred Time Slot)
- Added field: `meeting_attendees` (points to Meeting Attendee)
- Removed field: `additional_attendees` (replaced with structured table)

## Testing

### Manual Testing Steps

**1. Test Time Slot Creation**
```python
# In Frappe console
meeting = frappe.get_doc({
    "doctype": "Pre-Application Meeting",
    "request": "REQ-XXX-XXXX",
    "meeting_type": "Pre-Application Meeting",
    "status": "Requested",
    "preferred_time_slots": [
        {
            "preference_order": 1,
            "preferred_start": "2025-12-10 10:00:00",
            "preferred_end": "2025-12-10 11:00:00"
        },
        {
            "preference_order": 2,
            "preferred_start": "2025-12-11 14:00:00",
            "preferred_end": "2025-12-11 15:00:00"
        },
        {
            "preference_order": 3,
            "preferred_start": "2025-12-12 09:00:00",
            "preferred_end": "2025-12-12 10:00:00"
        }
    ]
})
meeting.insert()
frappe.db.commit()
print(f"Meeting created: {meeting.name}")
```

**2. Test Accept Time Slot**
```python
from lodgeick.lodgeick.doctype.pre_application_meeting.pre_application_meeting import accept_time_slot

result = accept_time_slot("PAM-REQ-XXX-0001", 1)  # Accept 2nd slot
print(result)
# Should schedule meeting and send email
```

**3. Test Propose Alternative**
```python
from lodgeick.lodgeick.doctype.pre_application_meeting.pre_application_meeting import propose_alternative_time

result = propose_alternative_time(
    "PAM-REQ-XXX-0001",
    0,  # First slot
    "2025-12-10 15:00:00",  # Alternative start
    "2025-12-10 16:00:00",  # Alternative end
    "Original time conflicts with council meeting"
)
print(result)
# Should send notification email to applicant
```

**4. Test Attendee Management**
```python
meeting = frappe.get_doc("Pre-Application Meeting", "PAM-REQ-XXX-0001")
meeting.append("meeting_attendees", {
    "attendee_name": "John Smith",
    "attendee_email": "john@example.com",
    "attendee_phone": "+64 21 123 4567",
    "organization": "Smith Consulting",
    "role": "Planning Consultant"
})
meeting.save()
print(f"Attendees: {len(meeting.meeting_attendees)}")
```

### Automated Testing (To Be Implemented)

**Test File**: `test_pre_application_meeting.py`

Required test cases:
- ✓ Create meeting with 3 preferred time slots
- ✓ Accept time slot schedules meeting
- ✓ Decline time slot updates status
- ✓ Propose alternative sends notification
- ✓ Accept alternative schedules meeting
- ✓ All slots declined triggers applicant notification
- ✓ Add attendees to meeting
- ✓ Event creation and updates work correctly
- ✓ Permissions are enforced correctly

## Email Notifications

### 1. Meeting Request Notification (to Planner)
**Trigger**: When applicant submits meeting request
**Recipient**: Assigned council planner
**Content**:
- Request number and applicant details
- Meeting purpose
- 3 preferred time slots
- Link to review and respond

### 2. Meeting Confirmation (to Applicant)
**Trigger**: When planner accepts a time slot
**Recipient**: Applicant
**Content**:
- Confirmed date and time
- Meeting format (In Person / Video / Phone)
- Location or meeting link
- Planner details
- Calendar invite attachment

### 3. Alternative Time Proposed (to Applicant)
**Trigger**: When planner proposes alternative time
**Recipient**: Applicant
**Content**:
- Original requested time
- Proposed alternative time
- Planner's notes explaining why
- Link to accept or propose different time

### 4. All Slots Declined (to Applicant)
**Trigger**: When planner declines all 3 time slots
**Recipient**: Applicant
**Content**:
- Notification that proposed times don't work
- Planner's notes with explanation
- Request to propose new times
- Link to submit new request

## Files Created/Modified

### Backend Files Created
- ✓ `lodgeick/lodgeick/doctype/meeting_preferred_time_slot/meeting_preferred_time_slot.json`
- ✓ `lodgeick/lodgeick/doctype/meeting_preferred_time_slot/meeting_preferred_time_slot.py`
- ✓ `lodgeick/lodgeick/doctype/meeting_preferred_time_slot/__init__.py`
- ✓ `lodgeick/lodgeick/doctype/meeting_attendee/meeting_attendee.json`
- ✓ `lodgeick/lodgeick/doctype/meeting_attendee/meeting_attendee.py`
- ✓ `lodgeick/lodgeick/doctype/meeting_attendee/__init__.py`

### Backend Files Modified
- ✓ `lodgeick/lodgeick/doctype/pre_application_meeting/pre_application_meeting.json`
  - Added `preferred_time_slots` field
  - Added `meeting_attendees` field
  - Updated field order
- ✓ `lodgeick/lodgeick/doctype/pre_application_meeting/pre_application_meeting.py`
  - Added `accept_time_slot()` API
  - Added `decline_time_slot()` API
  - Added `propose_alternative_time()` API
  - Added `accept_alternative_time()` API
  - Added `send_alternative_time_notification()` helper

### Frontend Files Created
- ✓ `frontend/src/components/common/ContactSelector.vue`
- ✓ `frontend/src/components/common/DateTimePicker.vue`

### Frontend Files To Be Modified (Next Phase)
- ⏳ `frontend/src/components/request-steps/Step1ApplicantProposal.vue`
  - Integrate DateTimePicker for 3 time slots
  - Integrate ContactSelector for attendees
  - Update pre-application meeting modal
  - Add planner response UI
  - Wire up API calls

### Documentation
- ✓ `PRE_APPLICATION_MEETING_ENHANCEMENT.md` (this file)

## Migration Steps

**Run Migrations**:
```bash
cd /workspace/development/frappe-bench
bench --site lodgeick.localhost migrate
bench --site lodgeick.localhost clear-cache
bench restart
```

**Status**: ✓ Migrations completed successfully

## Next Steps

### Phase 1: Frontend Integration (Next)
1. Create/update Pre-Application Meeting modal
2. Add 3x DateTimePicker components for time slots
3. Add ContactSelector integration for attendees
4. Wire up API endpoints
5. Add planner response UI
6. Test end-to-end workflow

### Phase 2: Planner Portal
1. Create planner dashboard view
2. Show pending meeting requests
3. Quick accept/decline/propose buttons
4. Bulk operations support
5. Calendar integration view

### Phase 3: Enhanced Features
1. Calendar sync (Google Calendar, Outlook)
2. SMS notifications (optional)
3. Meeting reminders (24hr, 1hr before)
4. Meeting cancellation/rescheduling
5. Meeting feedback and ratings
6. Analytics dashboard

### Phase 4: Mobile Optimization
1. Responsive design for mobile
2. Touch-optimized date/time pickers
3. Push notifications
4. Offline support

## Security Considerations

### Permission Model
- **Applicants**: Can create meetings for their requests, view their meetings
- **Planners**: Can view all meetings, respond to time slots, schedule meetings
- **Council Staff**: Can view meetings for their council
- **System Managers**: Full access

### API Security
- All endpoints use `@frappe.whitelist()` - require authentication
- Permissions checked via `has_permission()` function
- User can only accept alternatives for their own meetings
- Planner can only respond to meetings in their council

### Data Validation
- Time slot dates validated (must be future dates)
- Email addresses validated
- Slot index validated before access
- Status transitions validated

## Performance Considerations

### Database Optimization
- Indexes on:
  - `meeting_preferred_time_slot.parent`
  - `meeting_attendee.parent`
  - `meeting_attendee.attendee_email`
  - `pre_application_meeting.status`
  - `pre_application_meeting.requested_by`
  - `pre_application_meeting.council_planner`

### Caching Strategy
- Meeting list cached per user
- Contact list cached per session
- Planner dropdown cached

### Email Queue
- All emails sent via Frappe's email queue
- Async processing prevents blocking
- Retry logic for failed sends

## Support and Troubleshooting

### Common Issues

**Issue**: Time slots not showing in modal
- **Fix**: Check that meeting status is "Requested"
- **Fix**: Verify preferred_time_slots field exists

**Issue**: Planner can't accept time slot
- **Fix**: Check user has "Consent Planner" role
- **Fix**: Verify meeting permissions

**Issue**: Emails not sending
- **Fix**: Check email configuration in Frappe
- **Fix**: Check email queue: `bench --site lodgeick.localhost console` → `frappe.get_all("Email Queue", filters={"status": "Error"})`

**Issue**: Alternative time not saving
- **Fix**: Verify datetime format is ISO 8601
- **Fix**: Check alternative_start/end fields exist

### Debugging

Enable developer mode:
```bash
bench --site lodgeick.localhost set-config developer_mode 1
bench restart
```

View logs:
```bash
tail -f /workspace/development/frappe-bench/logs/lodgeick.localhost.log
```

Check email queue:
```python
# In Frappe console
emails = frappe.get_all("Email Queue",
    filters={"reference_doctype": "Pre-Application Meeting"},
    fields=["name", "status", "error", "creation"]
)
for email in emails:
    print(email)
```

## Version History

- **v1.0** (Current): Initial enhanced meeting workflow
  - 3 preferred time slots
  - Structured attendee management
  - Planner accept/decline/propose workflow
  - Email notifications
  - Backend API complete
  - Frontend components created (not yet integrated)

## Contributors

- Backend Development: Claude Code
- Frontend Components: Claude Code
- Documentation: Claude Code

## License

Same as Lodgeick project license
