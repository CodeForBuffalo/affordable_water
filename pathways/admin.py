from django.contrib import admin
from .models import Application, Document

# Register your models here.

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    inlines = [
        DocumentInline,
    ]
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('legal_agreement','signature','income_photo')
        return self.readonly_fields