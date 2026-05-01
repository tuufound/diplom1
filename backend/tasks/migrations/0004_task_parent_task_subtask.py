from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0003_project_task_project_projectmembership_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="parent_task",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="subtasks",
                to="tasks.task",
            ),
        ),
    ]
