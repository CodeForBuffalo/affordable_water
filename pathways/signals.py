from django.db.models.signals import post_save
from django.dispatch import receiver
from pathways.models import Application, ForgivenessApplication
from . import tasks

@receiver(post_save, sender=Application, dispatch_uid="confirmation_email_discount")
def send_email_for_discount_application(sender, instance, created, **kwargs):
    if created:
        tasks.send_received_confirmation_on_discount_application(instance)
    elif instance.status == 'enrolled':
        tasks.send_confirmation_email_after_discount_enrolled(instance)

@receiver(post_save, sender=ForgivenessApplication, dispatch_uid="confirmation_email_amnesty")
def send_email_for_amnesty_application(sender, instance, created, **kwargs):
    if created:
        tasks.send_received_confirmation_on_amnesty_application(instance)
    elif instance.status == 'enrolled':
        tasks.send_confirmation_email_after_amnesty_enrolled(instance)