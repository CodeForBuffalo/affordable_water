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
    readonly_fields = ['email_address','discount_application_received', 
                        'amnesty_application_received', 'enrolled_in_amnesty_program', 
                        'enrolled_in_discount_program']

    list_display = ['email_address','discount_application_received', 
                        'amnesty_application_received', 'enrolled_in_amnesty_program', 
                        'enrolled_in_discount_program']

    list_filter = ['discount_application_received', 
                        'amnesty_application_received', 'enrolled_in_amnesty_program', 
                        'enrolled_in_discount_program']

admin.site.site_header = "GetWaterWiseBuffalo Admin"