import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from celery import shared_task
import logging

from unity.models import VisitorEmail, Seller
from unity.constants.visitor_emails import (
    VisitorEmailStatusType,
    VisitorEmailIsSentType,
)

logger = logging.getLogger(__name__)

@shared_task(name="unity__send_analysis_email_task")
def send_analysis_email_task():
    """Sends an email to the seller every Monday and Wednesday including the statistics around the email list."""
    sellers = Seller.objects.filter(
        Q(user__is_active=True),
        Q(is_email_sent=VisitorEmailIsSentType.UNSENT),
        ~Q(is_email_sent=VisitorEmailIsSentType.SENDING),
    )

    for seller in sellers:
        try:
            visitor_emails = VisitorEmail.objects.filter(seller=seller)
            current_date = datetime.date.today().strftime("%B %Y")

            # Analysis
            amount_new_this_month = visitor_emails.filter(
                created_at__month=datetime.date.today().month
            ).count()
            amount_unsubscribed = visitor_emails.filter(
                status=VisitorEmailStatusType.UNSUBSCRIBED
            ).count()

            # Update status this seller to sending
            seller.is_email_sent = VisitorEmailIsSentType.SENDING
            seller.save()

            message = render_to_string(
                "api/mail/celery_mail.html",
                {
                    "current_date": current_date,
                    "emails": visitor_emails,
                    "amount_new_this_month": amount_new_this_month,
                    "amount_unsubscribed": amount_unsubscribed,
                },
            )
            subject = "Email subscription analysis"
            send = EmailMessage(
                subject,
                message,
                from_email=settings.EMAIL_FROM,
                to=[seller.user.email],
            )
            send.content_subtype = "html"
            try:
                send.send()
            finally:
                seller.is_email_sent = VisitorEmailIsSentType.SENT
                seller.save()
        except Exception as e:
            seller.is_email_sent = VisitorEmailIsSentType.ERROR
            seller.save()
            logger.error(f"Cannot send mail analysis with error is {e}")
    return True
