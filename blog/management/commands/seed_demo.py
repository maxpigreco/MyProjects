"""Seed the demo blog content in an idempotent way."""

from datetime import datetime, timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from blog.models import Post

DEMO_USERNAME = "user"
DEMO_AUTHOR_NAME = "Zenva Academy"

DEMO_POSTS = [
    {
        "slug": "the-rise-of-ai-in-everyday-life",
        "title": "The Rise of AI in Everyday Life",
        "author_name": DEMO_AUTHOR_NAME,
        "status": Post.Status.PUBLISHED,
        "published_at": datetime(2025, 6, 28, 0, 42, 7, tzinfo=dt_timezone.utc),
        "content": (
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data."
        ),
    },
    {
        "slug": "understanding-blockchain",
        "title": "Understanding Blockchain",
        "author_name": DEMO_AUTHOR_NAME,
        "status": Post.Status.PUBLISHED,
        "published_at": datetime(2025, 6, 28, 0, 47, 7, tzinfo=dt_timezone.utc),
        "content": (
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data."
        ),
    },
    {
        "slug": "10-habits-of-highly-productive-developers",
        "title": "10 Habits of Highly Productive Developers",
        "author_name": DEMO_AUTHOR_NAME,
        "status": Post.Status.PUBLISHED,
        "published_at": datetime(2025, 6, 28, 0, 47, 28, tzinfo=dt_timezone.utc),
        "content": (
            "Some Data.Some Data.Some Data.Some Data.Some Data. "
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data."
        ),
    },
    {
        "slug": "how-dark-mode-took-over-ui-design",
        "title": "How Dark Mode Took Over UI Design",
        "author_name": DEMO_AUTHOR_NAME,
        "status": Post.Status.PUBLISHED,
        "published_at": datetime(2025, 6, 28, 0, 47, 40, tzinfo=dt_timezone.utc),
        "content": (
            "Some Data.Some Data.Some Data.Some Data.Some Data. "
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data."
        ),
    },
    {
        "slug": "why-you-should-learn-rust-in-2025",
        "title": "Why You Should Learn Rust in 2025",
        "author_name": DEMO_AUTHOR_NAME,
        "status": Post.Status.PUBLISHED,
        "published_at": datetime(2025, 6, 28, 0, 47, 52, tzinfo=dt_timezone.utc),
        "content": (
            "Some Data.Some Data.Some Data.Some Data.Some Data. "
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data.\n\n"
            "Some Data.Some Data.Some Data.Some Data.Some Data."
        ),
    },
    {
        "slug": "draft",
        "title": "Draft",
        "author_name": "Admin",
        "status": Post.Status.DRAFT,
        "published_at": None,
        "content": "",
    },
]


class Command(BaseCommand):
    """Create or refresh the demo user, profile and posts."""

    help = "Create or refresh the demo blog content idempotently."

    def handle(self, *args, **options):
        """Create the demo user and upsert each demo post by slug."""
        user = self._ensure_demo_user()

        created = 0
        updated = 0
        for data in DEMO_POSTS:
            defaults = {
                key: value for key, value in data.items() if key != "slug"
            }
            defaults["author"] = user
            _, was_created = Post.objects.update_or_create(
                slug=data["slug"],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Demo data ready: user '{DEMO_USERNAME}'; "
                    f"posts created {created}, updated {updated}."
                )
            )

    def _ensure_demo_user(self):
        """Return the demo author, always with an unusable password."""
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username=DEMO_USERNAME,
        )
        user.set_unusable_password()
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        user.save()
        return user
