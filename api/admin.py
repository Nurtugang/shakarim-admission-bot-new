from django.contrib import admin
from .models import KnowledgeBase, ChatHistory

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('category', 'text_preview', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('category', 'text')
    list_per_page = 50

    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = "Предварительный просмотр текста"

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'role', 'message_preview', 'timestamp')
    list_filter = ('role', 'timestamp')
    search_fields = ('session_id', 'message')
    list_per_page = 100
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def message_preview(self, obj):
        return obj.message[:80] + "..." if len(obj.message) > 80 else obj.message
    message_preview.short_description = "Сообщение"

    # Добавляем действие для очистки старой истории
    actions = ['delete_old_history']

    def delete_old_history(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = ChatHistory.objects.filter(timestamp__lt=cutoff_date).count()
        ChatHistory.objects.filter(timestamp__lt=cutoff_date).delete()
        
        self.message_user(request, f"Удалено {deleted_count} старых записей (старше 30 дней)")
    
    delete_old_history.short_description = "Удалить историю старше 30 дней"