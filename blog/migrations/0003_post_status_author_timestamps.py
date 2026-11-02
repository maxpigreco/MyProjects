from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("blog", "0002_post_views"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="published",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="post",
            old_name="author",
            new_name="author_name",
        ),
        migrations.AlterField(
            model_name="post",
            name="author_name",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="post",
            name="slug",
            field=models.SlugField(max_length=200, unique=True),
        ),
        migrations.AddField(
            model_name="post",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("published", "Published")],
                default="draft",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name="post",
            options={
                "ordering": ["-created_at"],
                "verbose_name_plural": "Posts",
            },
        ),
    ]
