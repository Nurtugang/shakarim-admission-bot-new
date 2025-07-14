import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from api.models import KnowledgeBase
from django.conf import settings

CACHE_PATH = os.path.join(settings.BASE_DIR, "cache", "knowledge_cache.txt")

def update_knowledge_cache_file():
    knowledge_list = KnowledgeBase.objects.values_list("text", flat=True)
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(knowledge_list))

@receiver(post_save, sender=KnowledgeBase)
@receiver(post_delete, sender=KnowledgeBase)
def handle_knowledge_change(sender, **kwargs):
    update_knowledge_cache_file()
