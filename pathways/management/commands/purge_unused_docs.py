import logging

from django.core.management import BaseCommand

from pathways.models import Application, Document

logger = logging.getLogger('django')

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Purge an applicant's documents once they are enrolled"

    def handle(self, *args, **options):
        apps = Application.objects.exclude(status='new')
        apps = apps.exclude(status='in_progress')

        doc_count = 0

        for app in apps:
            docs = Document.objects.filter(application=app)
            for doc in docs:
                doc_count = doc_count + 1
                doc.delete()

        logger.info('Purged %s unnecessary documents', doc_count)