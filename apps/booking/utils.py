from django.core.mail import send_mail
from django.conf import settings

#def send_booking_notification(booking, to_host=True):
#    subject = "New Booking Notification" if to_host else "Your Booking is Confirmed"
#    recipient = booking.rent.owner.email if to_host else booking.renter.email
#    message = f"""
#Hello,
#
#A booking has been {'made for your property' if to_host else 'confirmed'}:
#
#- Property: {booking.rent.title}
#- Dates: {booking.start_date} to {booking.end_date}
#- Renter: {booking.renter.full_name}
#
#StayFlow Team
#"""
#    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
#

def send_booking_notification(booking, to_host=True):
    title = booking.rent.title
    start = booking.start_date.strftime("%d %b %Y")
    end = booking.end_date.strftime("%d %b %Y")

    if to_host:
        message = (
            f" [To Host: {booking.rent.owner.email}]\n"
            f"New booking for: '{title}'\n"
            f"Dates: {start} – {end}\n"
            f"Booked by: {booking.renter.full_name} ({booking.renter.email})\n"
            f"Message from renter: {booking.message or '–'}"
        )
    else:
        message = (
            f" [To Renter: {booking.renter.email}]\n"
            f"Your booking is confirmed for: '{title}'\n"
            f"Dates: {start} – {end}\n"
            f"Host: {booking.rent.owner.full_name} ({booking.rent.owner.email})"
        )

    print(message)
    return message
