from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Application, Document

# Register your models here.

@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    readonly_fields = ['application']

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

@admin.register(Application)
class ApplicationAdmin(SimpleHistoryAdmin):
    inlines = [
        DocumentInline,
    ]
    readonly_fields = ['legal_agreement', 'signature']