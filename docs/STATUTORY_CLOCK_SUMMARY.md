# Statutory Clock Summary Panel - Implementation Guide

## Overview

The **Statutory Clock Summary Panel** provides a comprehensive, real-time view of RMA (Resource Management Act 1991) statutory timeframe compliance for resource consent applications in Lodgeick.

## Visual Features

### Main Display Components

1. **Large Working Days Counter**
   - Prominent display: "X working days"
   - Shows total elapsed working days (excludes weekends & holidays)
   - Primary metric for statutory compliance

2. **Status Badge**
   - **▶ Running** (Green): Clock actively counting, <60% elapsed
   - **▶ Monitor** (Orange): 60-80% of timeframe elapsed, needs attention
   - **▶ Urgent** (Red): >80% elapsed, critical deadline approaching
   - **⏸ Stopped** (Gray): Clock paused during RFI or other exclusion period

3. **Progress Bar**
   - Visual representation of elapsed vs remaining time
   - Color-coded to match status badge
   - Smooth transitions on updates

4. **Clock Details Grid**
   - **Last Started**: Timestamp when clock was initiated/resumed
   - **Last Stopped**: Timestamp when clock was paused (or N/A if running)
   - **Current Status**: Calculated runtime information
     - Running: "Running for X calendar days"
     - Stopped: "Stopped after X calendar days"

5. **Context-Aware Information**
   - Running state: "Clock is actively counting. Working days exclude weekends and public holidays."
   - Stopped state: "Clock is paused. This period is excluded from working days calculation."

## Technical Implementation

### Backend Fields Used (No New Fields Required)

All data comes from existing Resource Consent Application DocType fields:

```python
# Existing fields in resource_consent_application.json
{
    "statutory_clock_started": "Datetime",       # When clock started
    "statutory_clock_stopped": "Datetime",       # When clock paused (null if running)
    "working_days_elapsed": "Int (read-only)",   # Working days counted
    "working_days_remaining": "Int (read-only)"  # Days until deadline
}
```

### Client-Side Logic

**File**: `lodgeick/lodgeick/doctype/resource_consent_application/resource_consent_application.js`

**Function**: `add_statutory_clock_indicator(frm)`

#### Key Calculations

1. **Clock Running State**
   ```javascript
   const is_running = frm.doc.statutory_clock_started && !frm.doc.statutory_clock_stopped;
   ```

2. **Percentage Elapsed**
   ```javascript
   const total_days = days_elapsed + days_remaining;
   const percentage = total_days > 0 ? (days_elapsed / total_days) * 100 : 0;
   ```

3. **Runtime Duration** (Calendar Days)
   ```javascript
   // For running clock
   const now = new Date();
   const started = new Date(frm.doc.statutory_clock_started);
   const calendar_days = Math.floor((now - started) / (1000 * 60 * 60 * 24));

   // For stopped clock
   const stopped = new Date(frm.doc.statutory_clock_stopped);
   const started = new Date(frm.doc.statutory_clock_started);
   const calendar_days = Math.floor((stopped - started) / (1000 * 60 * 60 * 24));
   ```

4. **NZ Date Formatting**
   ```javascript
   const format_datetime = (dt) => {
       if (!dt) return 'N/A';
       const date = new Date(dt);
       return date.toLocaleString('en-NZ', {
           year: 'numeric',
           month: 'short',
           day: 'numeric',
           hour: '2-digit',
           minute: '2-digit'
       });
   };
   ```

### Auto-Refresh Behavior

The summary panel automatically refreshes when:

1. **Form loads** - `refresh` event calls `add_statutory_clock_indicator(frm)`
2. **Clock actions executed** - Start/Stop/Resume buttons trigger `frm.save()` which refreshes form
3. **Manual save** - Any form save operation

### Backend Methods (Existing, Not Modified)

**File**: `lodgeick/lodgeick/doctype/resource_consent_application/resource_consent_application.py`

```python
def start_statutory_clock(self):
    """Start the RMA statutory clock"""
    if not self.statutory_clock_started:
        self.statutory_clock_started = now_datetime()
        self.statutory_clock_stopped = None
        self.save(ignore_permissions=True)

def stop_statutory_clock(self):
    """Stop the RMA statutory clock (RFI issued)"""
    if self.statutory_clock_started and not self.statutory_clock_stopped:
        self.statutory_clock_stopped = now_datetime()
        self.save(ignore_permissions=True)

def restart_statutory_clock(self):
    """Restart the clock after RFI (information received)"""
    if self.statutory_clock_stopped:
        self.statutory_clock_stopped = None
        self.save(ignore_permissions=True)

def calculate_working_days(self):
    """Calculate working days elapsed excluding weekends and holidays"""
    if not self.statutory_clock_started:
        return

    end_date = self.statutory_clock_stopped or now_datetime()
    self.working_days_elapsed = calculate_working_days_between(
        self.statutory_clock_started,
        end_date
    )

    # Get SLA from parent request type
    request = frappe.get_doc("Request", self.request)
    if request.request_type:
        request_type_doc = frappe.get_doc("Request Type", request.request_type)
        sla_days = request_type_doc.processing_sla_days or 20
        self.working_days_remaining = max(0, sla_days - self.working_days_elapsed)
```

## User Workflow

### Starting the Clock

1. Planner opens Resource Consent Application
2. Clicks **"Start Statutory Clock"** button (RMA Process menu)
3. Confirms action
4. `statutory_clock_started` is set to current datetime
5. Summary panel appears at top of form showing running status

### Stopping the Clock (RFI Issued)

1. Planner identifies need for further information
2. Clicks **"Stop Clock (RFI)"** button
3. Confirms action ("Requesting further information from applicant")
4. `statutory_clock_stopped` is set to current datetime
5. Summary panel updates to show "Stopped" status
6. Working days calculation freezes at current value

### Resuming the Clock (Information Received)

1. Applicant provides requested information
2. Planner reviews and accepts information
3. Clicks **"Resume Clock"** button
4. Confirms action ("Information received from applicant")
5. `statutory_clock_stopped` is cleared (set to null)
6. Summary panel updates to show "Running" status
7. Working days calculation resumes from where it left off

## RMA Statutory Timeframes

### Standard Non-Notified Consent
- **Default SLA**: 20 working days from lodgement
- **Excludes**: Weekends, public holidays, RFI periods

### Notified Consent
- **Limited Notification**: 20 working days submission period + processing time
- **Public Notification**: 20 working days submission period + processing time
- **Clock typically stopped** during submission periods

### Working Days Calculation

**File**: `lodgeick/lodgeick/doctype/request/request.py`

```python
def calculate_working_days_between(start_date, end_date):
    """Calculate working days between two dates (excluding weekends and holidays)"""
    start = getdate(start_date)
    end = getdate(end_date)

    working_days = 0
    current_date = start

    while current_date <= end:
        # Skip weekends (Monday=0, Friday=4)
        if current_date.weekday() < 5:
            # Skip public holidays
            if not is_public_holiday(current_date):
                working_days += 1
        current_date = add_days(current_date, 1)

    return working_days
```

## Clock Exclusion Periods

**DocType**: `Clock Exclusion Period` (child table)

Tracks suspension periods with:
- **Exclusion Type**: RFI Issued, Section 37, Section 91, Section 92, Notification Period, Hearing Period, Applicant Delay, Custom
- **Date Range**: started_date, ended_date
- **Calculated**: working_days_excluded (auto-calculated using same working days logic)
- **Reference**: Links to related documents (RFI, notifications, etc.)

## Visual Design Specifications

### Color Palette

```css
/* Status Colors */
Green (On Track):     #10b981
Orange (Monitor):     #f59e0b
Red (Urgent):         #ef4444
Gray (Stopped):       #6b7280

/* Background Gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Progress Bar Background */
rgba(255,255,255,0.2)

/* Info Boxes */
Running: rgba(255,255,255,0.15) with #10b981 left border
Stopped: rgba(255,255,255,0.15) with #f59e0b left border
```

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ 🕐 STATUTORY CLOCK STATUS                    ▶ On Track    │
│                                              75% elapsed    │
│ 15 working days                                            │
│ 5 days remaining of 20 total                              │
│                                                            │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░ (Progress Bar)                      │
│                                                            │
│ ┌──────────────┬──────────────┬──────────────┐           │
│ │ Last Started │ Last Stopped │ Current Status│           │
│ │ 1 Dec 2025   │ N/A          │ Running for   │           │
│ │ 09:30        │              │ 21 days       │           │
│ └──────────────┴──────────────┴──────────────┘           │
│                                                            │
│ ℹ️ Clock is actively counting. Working days exclude      │
│    weekends and public holidays.                          │
└─────────────────────────────────────────────────────────────┘
```

## Testing Scenarios

### Scenario 1: New Application with Clock Start
1. Create new Resource Consent Application
2. Verify no clock summary shown (clock not started)
3. Click "Start Statutory Clock"
4. Verify summary panel appears with:
   - Running status badge
   - 0 working days elapsed
   - Full days remaining
   - Current date/time in "Last Started"
   - "N/A" in "Last Stopped"
   - "Running for 0 calendar days"

### Scenario 2: Stop Clock for RFI
1. Open application with running clock (e.g., 10 days elapsed)
2. Click "Stop Clock (RFI)"
3. Verify summary updates:
   - Status changes to "Stopped"
   - Gray badge color
   - Working days frozen at 10
   - Both "Last Started" and "Last Stopped" show timestamps
   - "Stopped after X calendar days"
   - Warning message about exclusion period

### Scenario 3: Resume Clock After RFI
1. Open application with stopped clock
2. Click "Resume Clock"
3. Verify summary updates:
   - Status changes back to running (green/orange/red based on %)
   - "Last Stopped" returns to "N/A"
   - Working days calculation resumes
   - "Running for X calendar days" (resets from resume point)

### Scenario 4: Monitor Status (60-80%)
1. Create application with 12 elapsed days, 8 remaining (60%)
2. Verify orange "Monitor" badge
3. Verify progress bar shows orange color

### Scenario 5: Urgent Status (>80%)
1. Create application with 17 elapsed days, 3 remaining (85%)
2. Verify red "Urgent" badge
3. Verify progress bar shows red color

### Scenario 6: Weekend and Holiday Exclusion
1. Start clock on Friday
2. Wait until Monday
3. Verify working days shows 1 (Friday only)
4. Calendar days shows 3

### Scenario 7: Multiple Stop/Resume Cycles
1. Start clock
2. Stop after 5 days
3. Resume
4. Stop after 3 more days (total 8)
5. Resume
6. Verify working days correctly accumulates
7. Verify timestamps update appropriately

## Troubleshooting

### Panel Not Appearing
**Cause**: Clock not started yet
**Solution**: Click "Start Statutory Clock" button

### Working Days Not Updating
**Cause**: Clock is stopped
**Solution**: Click "Resume Clock" to restart

### Incorrect Working Days Count
**Cause**: Holiday calendar not configured
**Solution**: Configure Holiday List in Frappe (HR module)

### Panel Shows After Form Save Only
**Expected Behavior**: Panel updates on form refresh
**Solution**: This is normal - ensure form saves after clock actions

## RMA Compliance Notes

### Section 88 - Completeness
Clock does **NOT** start until application deemed complete under s88(3).

### Section 92 - Further Information
Clock **MUST** be stopped when RFI issued. Resumes when satisfactory information received.

### Section 95 - Notification
Clock continues during notification assessment period. May be stopped during submission period for notified consents.

### Section 104 - Decision Timeframes
Decision must be made within statutory timeframe unless:
- Applicant agrees to extension
- Application notified (different timeframes apply)
- Section 37 extension obtained

## Related Documentation

- [Resource Consent Application DocType](../lodgeick/doctype/resource_consent_application/)
- [Clock Exclusion Period DocType](../lodgeick/doctype/clock_exclusion_period/)
- [Request Type Configuration](../lodgeick/doctype/request_type/)
- [Working Days Calculation](../lodgeick/doctype/request/request.py)
- [RMA 1991 Statutory Timeframes](https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM231942.html)

## Changelog

### Version 1.1 (2025-11-25)
- Enhanced clock summary with detailed status grid
- Added calendar days calculation
- Added runtime/stopped duration display
- Improved NZ datetime formatting
- Added context-aware information messages
- Enhanced visual design with gradients and shadows
- Added running/stopped state icons (▶/⏸)

### Version 1.0 (Initial)
- Basic progress bar and status badge
- Working days counter
- Percentage display
