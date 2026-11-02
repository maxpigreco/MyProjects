from django.conf import settings
from django.db import migrations


def forwards(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    author, _ = User.objects.get_or_create(
        username="user",
        defaults={
            "email": "",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "password": "!",
        },
    )

    for post in Post.objects.order_by("pk").iterator():
        is_published = post.is_public
        published_at = post.created_at if is_published else None
        status = "published" if is_published else "draft"

        # The empty "Draft" post becomes the demo draft.
        if post.title == "Draft" and not post.content.strip():
            status = "draft"
            published_at = None

        Post.objects.filter(pk=post.pk).update(
            author_id=author.pk,
            status=status,
            published_at=published_at,
        )


def backwards(apps, schema_editor):
    Post = apps.get_model("blog", "Post")

    for post in Post.objects.order_by("pk").iterator():
        Post.objects.filter(pk=post.pk).update(
            is_public=post.status == "published",
            author_id=None,
            status="draft",
            published_at=None,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0003_post_status_author_timestamps"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
