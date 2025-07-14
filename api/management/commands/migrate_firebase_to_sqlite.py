from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from api.models import KnowledgeBase
from shakarim_admission_bot.firebase_config import firebase_db
import time

class Command(BaseCommand):
    help = 'Перенос данных из Firebase в SQLite'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет перенесено, без фактического переноса',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Очистить существующие данные в SQLite перед переносом',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clear_existing = options['clear_existing']

        self.stdout.write("🚀 Начинаем миграцию данных из Firebase в SQLite...")

        # Проверяем количество существующих записей в SQLite
        existing_count = KnowledgeBase.objects.count()
        if existing_count > 0:
            self.stdout.write(
                f"⚠️  В SQLite уже есть {existing_count} записей"
            )
            if clear_existing:
                if not dry_run:
                    KnowledgeBase.objects.all().delete()
                    self.stdout.write("🗑️  Существующие данные удалены")
                else:
                    self.stdout.write("🗑️  [DRY RUN] Будут удалены существующие данные")

        # Получаем данные из Firebase
        try:
            self.stdout.write("📥 Получаем данные из Firebase...")
            start_time = time.time()
            
            docs = firebase_db.collection("knowledge-base").get()
            firebase_data = []
            
            for doc in docs:
                doc_data = doc.to_dict()
                if 'category' in doc_data and 'text' in doc_data:
                    firebase_data.append({
                        'firebase_id': doc.id,
                        'category': doc_data['category'],
                        'text': doc_data['text']
                    })
                else:
                    self.stdout.write(
                        f"⚠️  Пропускаем документ {doc.id}: отсутствуют обязательные поля"
                    )

            fetch_time = time.time() - start_time
            self.stdout.write(
                f"✅ Получено {len(firebase_data)} записей из Firebase за {fetch_time:.2f} сек"
            )

        except Exception as e:
            raise CommandError(f"Ошибка при получении данных из Firebase: {e}")

        if not firebase_data:
            self.stdout.write("⚠️  Нет данных для переноса")
            return

        # Показываем статистику по категориям
        categories = {}
        for item in firebase_data:
            category = item['category']
            categories[category] = categories.get(category, 0) + 1

        self.stdout.write("\n📊 Статистика по категориям:")
        for category, count in categories.items():
            self.stdout.write(f"   • {category}: {count} записей")

        # Dry run - показываем примеры данных
        if dry_run:
            self.stdout.write("\n📋 Примеры данных для переноса:")
            for i, item in enumerate(firebase_data[:3]):  # Показываем первые 3
                self.stdout.write(
                    f"   {i+1}. [{item['category']}] {item['text'][:100]}..."
                )
            if len(firebase_data) > 3:
                self.stdout.write(f"   ... и еще {len(firebase_data) - 3} записей")
            
            self.stdout.write(
                f"\n✅ [DRY RUN] Будет перенесено {len(firebase_data)} записей"
            )
            return

        # Фактический перенос данных
        self.stdout.write(f"\n💾 Переносим {len(firebase_data)} записей в SQLite...")
        
        try:
            with transaction.atomic():
                start_time = time.time()
                
                # Создаем записи пакетно для лучшей производительности
                sqlite_objects = []
                for item in firebase_data:
                    sqlite_objects.append(
                        KnowledgeBase(
                            category=item['category'],
                            text=item['text']
                        )
                    )
                
                # Сохраняем все записи одним запросом
                KnowledgeBase.objects.bulk_create(sqlite_objects)
                
                transfer_time = time.time() - start_time
                self.stdout.write(
                    f"✅ Перенос завершен за {transfer_time:.2f} сек"
                )

        except Exception as e:
            raise CommandError(f"Ошибка при переносе данных: {e}")

        # Проверяем результат
        final_count = KnowledgeBase.objects.count()
        self.stdout.write(
            f"\n🎉 Миграция завершена! В SQLite теперь {final_count} записей"
        )

        # Показываем статистику по категориям в SQLite
        from django.db.models import Count
        sqlite_categories = KnowledgeBase.objects.values('category').annotate(
            count=Count('category')
        ).order_by('category')

        self.stdout.write("\n📊 Статистика в SQLite:")
        for item in sqlite_categories:
            self.stdout.write(f"   • {item['category']}: {item['count']} записей")