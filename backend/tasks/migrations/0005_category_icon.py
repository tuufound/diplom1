from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0004_task_parent_task_subtask"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="icon",
            field=models.CharField(default="📁", max_length=8),
        ),
    ]
