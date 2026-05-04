# Seed default task priorities (RU labels, levels 1–4 for UI chips).

from django.db import migrations


def seed_priorities(apps, schema_editor):
    Priority = apps.get_model("tasks", "Priority")
    rows = [
        {"name": "Низкий", "level": 1, "color": "#63c799"},
        {"name": "Средний", "level": 2, "color": "#9b7bff"},
        {"name": "Высокий", "level": 3, "color": "#ff6db8"},
        {"name": "Критический", "level": 4, "color": "#e55353"},
    ]
    for row in rows:
        Priority.objects.get_or_create(
            level=row["level"],
            defaults={"name": row["name"], "color": row["color"]},
        )


def unseed_priorities(apps, schema_editor):
    Priority = apps.get_model("tasks", "Priority")
    names = ("Низкий", "Средний", "Высокий", "Критический")
    Priority.objects.filter(name__in=names, level__in=(1, 2, 3, 4)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0007_taskcollaborator"),
    ]

    operations = [
        migrations.RunPython(seed_priorities, unseed_priorities),
    ]
