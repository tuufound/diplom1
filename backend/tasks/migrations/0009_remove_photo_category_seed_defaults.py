# Remove the "фото" demo category and ensure a sensible default set of categories.

from django.db import migrations


PHOTO_NAMES = ("фото", "Фото", "photo", "Photo")

DEFAULT_CATEGORIES = [
    ("Работа", "📋", "Рабочие задачи и проекты"),
    ("Учёба", "📚", "Курсы, экзамены, диплом"),
    ("Дом", "🏠", "Быт, ремонт, семья"),
    ("Здоровье", "💪", "Спорт, врачи, сон"),
    ("Финансы", "💳", "Счета, покупки, бюджет"),
    ("Досуг", "🎮", "Хобби, отдых, планы"),
]


def forward(apps, schema_editor):
    Category = apps.get_model("tasks", "Category")
    for raw in PHOTO_NAMES:
        Category.objects.filter(name=raw).delete()
    Category.objects.filter(name__iexact="фото").delete()

    for name, icon, description in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            defaults={"icon": icon, "description": description},
        )


def backward(apps, schema_editor):
    Category = apps.get_model("tasks", "Category")
    seeded = {row[0] for row in DEFAULT_CATEGORIES}
    Category.objects.filter(name__in=seeded).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0008_seed_default_priorities"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
