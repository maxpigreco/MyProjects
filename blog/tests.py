from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .admin import PostAdmin
from .models import ContactMessage, Post


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


class PostAdminTests(TestCase):
    """Tests for the admin slug handling."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin-pass-123",
        )

    def _admin_form(self, data, instance=None):
        model_admin = PostAdmin(Post, AdminSite())
        request = RequestFactory().get("/admin/blog/post/add/")
        request.user = self.admin_user
        form_class = model_admin.get_form(request, obj=instance)
        return form_class(data=data, instance=instance)

    def _form_data(self, title):
        return {
            "title": title,
            "author": self.admin_user.pk,
            "content": "Content",
            "status": Post.Status.DRAFT,
            "views": 0,
        }

    def test_admin_creates_unique_slug_for_duplicate_title(self):
        Post.objects.create(
            title="Same Title",
            content="First",
            author=self.admin_user,
        )

        form = self._admin_form(self._form_data("Same Title"))
        self.assertTrue(form.is_valid(), form.errors)
        post = form.save()

        self.assertEqual(post.slug, "same-title-2")

    def test_admin_keeps_slug_when_title_changes(self):
        post = Post.objects.create(
            title="Original Title",
            content="Content",
            author=self.admin_user,
        )

        form = self._admin_form(self._form_data("Renamed Title"), instance=post)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()

        self.assertEqual(saved.slug, "original-title")


class ContactMessageModelTests(TestCase):
    """Tests for the contact message model."""

    def test_string_representation_and_defaults(self):
        message = ContactMessage.objects.create(
            name="Alice",
            email="alice@example.com",
            message="Hello there",
        )

        self.assertEqual(str(message), "Alice <alice@example.com>")
        self.assertFalse(message.is_read)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_EMAIL="contact@example.com",
)
class ContactViewTests(TestCase):
    """Tests for the public contact form."""

    def _valid_data(self, **overrides):
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "message": "A" * 60,
        }
        data.update(overrides)
        return data

    def test_valid_submission_saves_and_emails(self):
        response = self.client.post(
            reverse("contact"),
            self._valid_data(),
        )

        self.assertRedirects(response, reverse("contact_thanks"))
        message = ContactMessage.objects.get()
        self.assertEqual(message.name, "Alice")
        self.assertEqual(message.email, "alice@example.com")
        self.assertEqual(message.message, "A" * 60)
        self.assertFalse(message.is_read)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["contact@example.com"])
        self.assertEqual(email.reply_to, ["alice@example.com"])
        self.assertIn("Alice", email.subject)
        self.assertIn("alice@example.com", email.body)
        self.assertIn("A" * 60, email.body)

    def test_honeypot_submission_is_ignored(self):
        response = self.client.post(
            reverse("contact"),
            self._valid_data(website="http://spam.example"),
        )

        self.assertRedirects(response, reverse("contact_thanks"))
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_short_message_is_rejected_without_side_effects(self):
        response = self.client.post(
            reverse("contact"),
            self._valid_data(message="too short"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.context["form"].errors)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_authenticated_user_gets_name_prefilled(self):
        user = get_user_model().objects.create_user(
            username="profileuser",
            password="test-pass-123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("contact"))

        self.assertEqual(
            response.context["form"]["name"].value(),
            "profileuser",
        )

    @patch("blog.views.EmailMessage.send", side_effect=Exception("SMTP down"))
    def test_email_failure_keeps_the_message(self, mock_send):
        with self.assertLogs("blog.views", level="ERROR") as logs:
            response = self.client.post(
                reverse("contact"),
                self._valid_data(),
            )

        self.assertRedirects(response, reverse("contact_thanks"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn(
            "Failed to send contact notification",
            logs.output[0],
        )
