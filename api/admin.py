from django.contrib import admin
from .models import KnowledgeBase

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('category', 'text_preview', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('category', 'text')
    list_per_page = 50

    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = "Предварительный просмотр текста"