# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate
import json


class Payment(Document):
    def autoname(self):
        """Generate payment number"""
        # Get request short name for better identification
        request = frappe.db.get_value("Request", self.request, "request_number")
        if request:
            # Count existing payments for this request
            count = frappe.db.count("Payment", {"request": self.request})
            self.payment_number = f"PAY-{request}-{count + 1:04d}"
            self.name = self.payment_number

    def validate(self):
        """Validation before saving"""
        # Ensure parent Request exists
        if not frappe.db.exists("Request", self.request):
            frappe.throw("Parent Request does not exist")

        # Calculate GST and total
        self.calculate_totals()

        # Validate amounts
        if self.amount <= 0:
            frappe.throw("Payment amount must be greater than 0")

    def before_submit(self):
        """Actions before submitting payment"""
        # Ensure payment is completed before submission
        if self.payment_status not in ["Completed", "Refunded"]:
            frappe.throw("Payment must be completed before submission")

    def on_submit(self):
        """Actions when payment is submitted"""
        # Update parent Request
        self.update_request_payment_status()

        # Send payment confirmation
        self.send_payment_confirmation()

    def calculate_totals(self):
        """Calculate GST and total amount"""
        # GST is 15% in New Zealand
        self.gst = flt(self.amount) * 0.15
        self.total_amount = flt(self.amount) + flt(self.gst)

    def update_request_payment_status(self):
        """Update payment status on parent Request"""
        request = frappe.get_doc("Request", self.request)

        # Get all submitted payments for this request
        total_paid = frappe.db.sql("""
            SELECT SUM(total_amount)
            FROM `tabPayment`
            WHERE request = %s
            AND docstatus = 1
            AND payment_status = 'Completed'
        """, (self.request,))[0][0] or 0

        # Get total fees from request
        total_fees = frappe.db.sql("""
            SELECT SUM(amount)
            FROM `tabRequest Fee`
            WHERE parent = %s
        """, (self.request,))[0][0] or 0

        # Update request payment status
        if total_paid >= total_fees:
            request.payment_status = "Paid"
        elif total_paid > 0:
            request.payment_status = "Partially Paid"
        else:
            request.payment_status = "Unpaid"

        request.total_paid = total_paid
        request.save(ignore_permissions=True)

    def send_payment_confirmation(self):
        """Send payment confirmation email"""
        request = frappe.get_doc("Request", self.request)
        if not request.applicant_email:
            return

        message = f"""
        <h3>Payment Confirmation</h3>
        <p>Dear {request.applicant_name},</p>
        <p>We have received your payment for application <strong>{request.request_number}</strong>.</p>

        <h4>Payment Details:</h4>
        <ul>
            <li><strong>Payment Number:</strong> {self.payment_number}</li>
            <li><strong>Payment Type:</strong> {self.payment_type}</li>
            <li><strong>Amount:</strong> ${flt(self.amount):.2f} (excl GST)</li>
            <li><strong>GST:</strong> ${flt(self.gst):.2f}</li>
            <li><strong>Total:</strong> ${flt(self.total_amount):.2f}</li>
            <li><strong>Payment Date:</strong> {frappe.utils.format_datetime(self.payment_date)}</li>
            <li><strong>Payment Method:</strong> {self.payment_method}</li>
        """

        if self.transaction_id:
            message += f"<li><strong>Transaction ID:</strong> {self.transaction_id}</li>"

        if self.stripe_receipt_url:
            message += f'<li><a href="{self.stripe_receipt_url}">View Receipt</a></li>'

        message += """
        </ul>

        <p>Thank you for your payment. Your application is now being processed.</p>

        <p>Best regards,<br>
        Lodgeick Team</p>
        """

        try:
            frappe.sendmail(
                recipients=[request.applicant_email],
                subject=f"Payment Confirmation for Application {request.request_number}",
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )
        except Exception as e:
            frappe.log_error(f"Failed to send payment confirmation: {str(e)}")


@frappe.whitelist()
def create_stripe_payment_intent(request, amount, payment_type="Application Fee"):
    """Create a Stripe Payment Intent"""
    # This would integrate with Stripe API
    # For now, just create a pending payment record
    payment = frappe.get_doc({
        "doctype": "Payment",
        "request": request,
        "payment_type": payment_type,
        "payment_method": "Credit Card",
        "payment_gateway": "Stripe",
        "payment_status": "Pending",
        "amount": amount,
        "currency": "NZD"
    })
    payment.insert()

    return {
        "payment_name": payment.name,
        "payment_number": payment.payment_number,
        "amount": payment.total_amount
    }


@frappe.whitelist()
def confirm_stripe_payment(payment_name, payment_intent_id, stripe_data=None):
    """Confirm Stripe payment"""
    payment = frappe.get_doc("Payment", payment_name)

    # Update Stripe fields
    payment.stripe_payment_intent_id = payment_intent_id
    if stripe_data:
        if isinstance(stripe_data, str):
            stripe_data = json.loads(stripe_data)
        payment.stripe_charge_id = stripe_data.get("charge_id")
        payment.stripe_customer_id = stripe_data.get("customer_id")
        payment.stripe_receipt_url = stripe_data.get("receipt_url")
        payment.stripe_status = stripe_data.get("status")
        payment.payment_gateway_response = json.dumps(stripe_data, indent=2)

    payment.payment_status = "Completed"
    payment.transaction_id = payment_intent_id
    payment.save()

    # Submit if all details are complete
    if payment.payment_status == "Completed":
        payment.submit()

    return {"success": True, "message": "Payment confirmed successfully"}


@frappe.whitelist()
def get_request_payments(request):
    """Get all payments for a request"""
    payments = frappe.get_all(
        "Payment",
        filters={"request": request},
        fields=[
            "name",
            "payment_number",
            "payment_type",
            "payment_method",
            "payment_status",
            "amount",
            "gst",
            "total_amount",
            "payment_date",
            "transaction_id"
        ],
        order_by="payment_date desc"
    )
    return payments


@frappe.whitelist()
def calculate_outstanding_amount(request):
    """Calculate outstanding payment for a request"""
    # Get total fees
    total_fees = frappe.db.sql("""
        SELECT SUM(amount)
        FROM `tabRequest Fee`
        WHERE parent = %s
    """, (request,))[0][0] or 0

    # Get total paid
    total_paid = frappe.db.sql("""
        SELECT SUM(total_amount)
        FROM `tabPayment`
        WHERE request = %s
        AND docstatus = 1
        AND payment_status = 'Completed'
    """, (request,))[0][0] or 0

    outstanding = flt(total_fees) - flt(total_paid)

    return {
        "total_fees": total_fees,
        "total_paid": total_paid,
        "outstanding": outstanding
    }
