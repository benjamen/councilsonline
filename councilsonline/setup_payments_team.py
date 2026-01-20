"""Script to create PAYMENTS team for cash pickup scheduling"""

import frappe

def update_locations():
    """Update PAYMENTS team to only have Municipal Treasury Office"""
    if frappe.db.exists('Council Team', 'PAYMENTS'):
        team = frappe.get_doc('Council Team', 'PAYMENTS')
        team.available_locations = 'Municipal Treasury Office'
        team.default_location = 'Municipal Treasury Office'
        team.save()
        frappe.db.commit()
        print(f'Updated locations to: {team.available_locations}')
    else:
        print('PAYMENTS team not found')

def create_payments_team():
    """Create PAYMENTS team if it doesn't exist"""
    if not frappe.db.exists('Council Team', 'PAYMENTS'):
        team = frappe.get_doc({
            'doctype': 'Council Team',
            'team_code': 'PAYMENTS',
            'team_name': 'Payments Team',
            'description': 'Handles cash pickup appointments and payment disbursements',
            'is_active': 1,
            'enable_scheduling': 1,
            'default_appointment_duration': 15,
            'available_appointment_durations': '15,30',
            'appointment_buffer_time': 10,
            'max_daily_appointments': 50,
            'advance_booking_days': 30,
            'min_notice_hours': 24,
            'default_location': 'Municipal Treasury Office',
            'available_locations': 'Barangay Hall\nMunicipal Treasury Office\nOSCA Office',
            'business_hours': [
                {'day_of_week': 'Monday', 'is_open': 1, 'start_time': '08:00:00', 'end_time': '17:00:00'},
                {'day_of_week': 'Tuesday', 'is_open': 1, 'start_time': '08:00:00', 'end_time': '17:00:00'},
                {'day_of_week': 'Wednesday', 'is_open': 1, 'start_time': '08:00:00', 'end_time': '17:00:00'},
                {'day_of_week': 'Thursday', 'is_open': 1, 'start_time': '08:00:00', 'end_time': '17:00:00'},
                {'day_of_week': 'Friday', 'is_open': 1, 'start_time': '08:00:00', 'end_time': '17:00:00'},
                {'day_of_week': 'Saturday', 'is_open': 0, 'start_time': '08:00:00', 'end_time': '12:00:00'},
                {'day_of_week': 'Sunday', 'is_open': 0, 'start_time': '08:00:00', 'end_time': '12:00:00'}
            ]
        })
        team.insert(ignore_permissions=True)
        frappe.db.commit()
        print('PAYMENTS team created successfully')
    else:
        print('PAYMENTS team already exists')
