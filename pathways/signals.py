from django.db.models.signals import post_save
from django.dispatch import receiver

from pathways.models import Application, ForgivenessApplication
from pathways.tasks import send_automatic_email

@receiver(post_save, sender=Application, dispatch_uid="confirmation_email_discount")
def send_email_for_discount_application(sender, instance, created, **kwargs):
    del sender, kwargs # unused
    # No email to send without an email address
    if instance.email_address == '':
        return

    recipient_list = [(instance.first_name, instance.email_address)]

    if created:
        subject = 'We received your application for the Buffalo Water Affordability Program'
        template_name = 'pathways/emails/discount_confirmation_no_docs_now.html'
        send_automatic_email(email_address=instance.email_address, 
                                    email_type='discount_receive',
                                    subject=subject,
                                    template_name=template_name,
                                    recipient_list=recipient_list
                                    )
    elif instance.status == 'enrolled':
        subject = 'You have been successfully enrolled in the Buffalo Water Affordability Program'
        template_name = 'pathways/emails/discount_enrolled.html'
        send_automatic_email(email_address=instance.email_address, 
                                    email_type='discount_enroll',
                                    subject=subject,
                                    template_name=template_name,
                                    recipient_list=recipient_list
                                    )

@receiver(post_save, sender=ForgivenessApplication, dispatch_uid="confirmation_email_amnesty")
def send_email_for_amnesty_application(sender, instance, created, **kwargs):
    del sender, kwargs # unused
    # No email to send without an email address
    if instance.email_address == '':
        return

    recipient_list = [(instance.first_name, instance.email_address)]

    if created:
        subject = 'We received your application for the Buffalo Water Amnesty Program'
        template_name = 'pathways/emails/amnesty_confirmation.html'
        send_automatic_email(email_address=instance.email_address, 
                                    email_type='amnesty_receive',
                                    subject=subject,
                                    template_name=template_name,
                                    recipient_list=recipient_list
                                    )
    elif instance.status == 'enrolled':
        subject = 'You have been successfully enrolled in the Buffalo Water Amnesty Program'
        template_name = 'pathways/emails/amnesty_enrolled.html'
        send_automatic_email(email_address=instance.email_address, 
                                    email_type='amnesty_enroll',
                                    subject=subject,
                                    template_name=template_name,
                                    recipient_list=recipient_list
                                    )