from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0004_migrate_post_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveField(
            model_name="post",
            name="is_public",
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(
                fields=["status", "-published_at"],
                name="post_status_pub_idx",
            ),
        ),
        migrations.AlterModelOptions(
            name="post",
            options={
                "ordering": ["-published_at", "-created_at"],
                "verbose_name_plural": "Posts",
            },
        ),
    ]
