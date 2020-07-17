from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Application, Document, ForgivenessApplication, EmailCommunication

# Register your models here.

@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    pass

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

@admin.register(Application)
class ApplicationAdmin(SimpleHistoryAdmin):
    inlines = [
        DocumentInline,
    ]

@admin.register(ForgivenessApplication)
class ForgivenessApplicationAdmin(SimpleHistoryAdmin):
    pass

@admin.register(EmailCommunication)
class EmailCommunicationAdmin(SimpleHistoryAdmin):
    pass

admin.site.site_header = "GetWaterWiseBuffalo Admin"