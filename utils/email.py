from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

def send_booking_confirmation_email(user, booking, action):
    """
    Sends a booking confirmation email to the user and the service provider.
    :param user: The user who made the booking
    :param booking: The Booking instance
    :param action: 'created' or 'updated'
    """
    subject = 'Booking Confirmation - Fixly'
    context = {
        'user': user,
        'booking': booking,
        'action': action,
        'year': timezone.now().year,
    }
    html_message = render_to_string('booking/email/booking_confirmation.html', context)
    plain_message = strip_tags(html_message)

    # Send to user (fail_silently=False)
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

    # Send to service provider (fail_silently=True)
    if hasattr(booking, 'service_provider') and booking.service_provider and booking.service_provider.email:
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.service_provider.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            pass 