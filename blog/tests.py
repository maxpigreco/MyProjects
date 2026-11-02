from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Post


class PostModelTests(TestCase):
    """Tests for post slugs, publication status, and authorship."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="author",
            password="test-pass-123",
        )

    def _create_post(self, **overrides):
        data = {
            "title": "Test Post",
            "content": "Test content",
            "author": self.user,
        }
        data.update(overrides)
        return Post.objects.create(**data)

    def test_slug_is_generated_from_title(self):
        post = self._create_post(title="Hello World")
        self.assertEqual(post.slug, "hello-world")

    def test_duplicate_titles_get_unique_slugs(self):
        first = self._create_post(title="Same Title")
        second = self._create_post(title="Same Title")

        self.assertEqual(first.slug, "same-title")
        self.assertEqual(second.slug, "same-title-2")

    def test_slug_stays_stable_when_title_changes(self):
        post = self._create_post(title="Original Title")
        original_slug = post.slug

        post.title = "Changed Title"
        post.save()
        post.refresh_from_db()

        self.assertEqual(post.slug, original_slug)

    def test_publishing_sets_published_at(self):
        post = self._create_post(status=Post.Status.PUBLISHED)
        self.assertIsNotNone(post.published_at)

    def test_unpublishing_keeps_published_at(self):
        post = self._create_post(status=Post.Status.PUBLISHED)
        published_at = post.published_at

        post.status = Post.Status.DRAFT
        post.save()
        post.refresh_from_db()

        self.assertEqual(post.published_at, published_at)

    def test_new_post_defaults_to_draft(self):
        post = self._create_post()
        self.assertEqual(post.status, Post.Status.DRAFT)
        self.assertIsNone(post.published_at)

    def test_author_is_required(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Post.objects.create(
                title="No Author",
                content="Content",
                author=None,
            )

    def test_string_representation_is_title(self):
        post = self._create_post(title="Readable Title")
        self.assertEqual(str(post), "Readable Title")
