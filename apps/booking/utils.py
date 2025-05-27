def send_booking_notification(booking, to_host=True, cancelled=False):
    title = booking.rent.title
    start = booking.start_date.strftime("%d %b %Y")
    end = booking.end_date.strftime("%d %b %Y")

    if cancelled:
        message = (
            f"[To Renter: {booking.renter.email}]\n"
            f"Dear {booking.renter.full_name},\n\n"
            f"We appreciate your interest in '{title}' "
            f"from {start} to {end}.\n\n"
            f"Unfortunately, these dates have already been booked by another guest.\n"
            f"We're sorry your request could not be accommodated this time.\n\n"
            f"We hope you'll find another great place on StayFlow soon!"
        )
    elif to_host:
        message = (
            f"[To Host: {booking.rent.owner.email}]\n"
            f"New booking for: '{title}'\n"
            f"Dates: {start} – {end}\n"
            f"Booked by: {booking.renter.full_name} ({booking.renter.email})\n"
            f"Message from renter: {booking.message or '–'}"
        )
    else:
        message = (
            f"[To Renter: {booking.renter.email}]\n"
            f"Your booking is confirmed for: '{title}'\n"
            f"Dates: {start} – {end}\n"
            f"Host: {booking.rent.owner.full_name} ({booking.rent.owner.email})"
        )

    print(message)
    return message

