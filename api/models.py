from django.db import models

class KnowledgeBase(models.Model):
    category = models.CharField(max_length=255, verbose_name="Категория")
    text = models.TextField(verbose_name="Текст знания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "База знаний"
        verbose_name_plural = "База знаний"
        indexes = [
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.category}: {self.text[:50]}..."
    

class ChatHistory(models.Model):
    session_id = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('model', 'Model')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session_id} ({self.role}): {self.message[:50]}"