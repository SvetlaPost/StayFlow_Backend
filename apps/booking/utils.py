from django.core.mail import send_mail
from django.conf import settings

def send_booking_notification(booking, to_host=True):
    subject = "New Booking Notification" if to_host else "Your Booking is Confirmed"
    recipient = booking.rent.owner.email if to_host else booking.renter.email
    message = f"""
Hello,

A booking has been {'made for your property' if to_host else 'confirmed'}:

- Property: {booking.rent.title}
- Dates: {booking.start_date} to {booking.end_date}
- Renter: {booking.renter.full_name}

StayFlow Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
