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


class PublicPostViewTests(TestCase):
    """Tests for the public home, detail, and search views."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="writer",
            password="test-pass-123",
        )

    def _create_post(self, **overrides):
        data = {
            "title": "Published Post",
            "content": "Body of the post",
            "author": self.user,
            "status": Post.Status.PUBLISHED,
        }
        data.update(overrides)
        return Post.objects.create(**data)

    def test_home_lists_only_published_posts(self):
        self._create_post(title="Visible Post")
        self._create_post(title="Hidden Draft", status=Post.Status.DRAFT)

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visible Post")
        self.assertNotContains(response, "Hidden Draft")

    def test_home_shows_empty_state(self):
        response = self.client.get(reverse("index"))

        self.assertContains(response, "No published posts yet.")

    def test_home_paginates_six_posts(self):
        for index in range(7):
            self._create_post(title=f"Post number {index}")

        response = self.client.get(reverse("index"))

        self.assertEqual(len(response.context["page_obj"]), 6)
        self.assertTrue(response.context["page_obj"].has_next())

    def test_post_detail_shows_published_post_and_counts_view(self):
        post = self._create_post(author_name="Zenva Academy")

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.title)
        self.assertContains(response, "Zenva Academy")
        post.refresh_from_db()
        self.assertEqual(post.views, 1)

    def test_post_detail_falls_back_to_username(self):
        post = self._create_post(author_name="")

        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, "writer")

    def test_post_detail_returns_404_for_draft(self):
        post = self._create_post(status=Post.Status.DRAFT)

        response = self.client.get(
            reverse("post_detail", kwargs={"slug": post.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_post_detail_returns_404_for_unknown_slug(self):
        response = self.client.get(
            reverse("post_detail", kwargs={"slug": "missing"})
        )

        self.assertEqual(response.status_code, 404)

    def test_search_matches_title_and_excludes_drafts(self):
        self._create_post(title="Django tips", content="Unrelated body")
        self._create_post(
            title="Draft about Django",
            status=Post.Status.DRAFT,
        )

        response = self.client.get(reverse("search"), {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django tips")
        self.assertNotContains(response, "Draft about Django")

    def test_search_matches_content(self):
        self._create_post(title="Other title", content="Unique needle here")

        response = self.client.get(reverse("search"), {"q": "needle"})

        self.assertContains(response, "Other title")

    def test_search_without_term_lists_all_published_posts(self):
        self._create_post(title="First article")
        self._create_post(title="Second article")

        response = self.client.get(reverse("search"), {"q": ""})

        self.assertContains(response, "First article")
        self.assertContains(response, "Second article")

    def test_search_paginates_results(self):
        for index in range(7):
            self._create_post(title=f"Matching {index}", content="match")

        response = self.client.get(reverse("search"), {"q": "Matching"})

        self.assertEqual(len(response.context["page_obj"]), 6)
        self.assertTrue(response.context["page_obj"].has_next())

    def test_search_links_to_post_detail(self):
        post = self._create_post(title="Linked post")

        response = self.client.get(reverse("search"), {"q": "Linked"})

        self.assertContains(response, post.get_absolute_url())


class PostUrlTests(TestCase):
    """Tests for the canonical post URL."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="author",
            password="test-pass-123",
        )

    def test_get_absolute_url_uses_post_detail_route(self):
        post = Post.objects.create(
            title="Hello World",
            content="Body",
            author=self.user,
            status=Post.Status.PUBLISHED,
        )

        self.assertEqual(post.get_absolute_url(), f"/posts/{post.slug}/")


class SeedDemoCommandTests(TestCase):
    """Tests for the idempotent demo data command."""

    def _run_seed(self):
        from django.core.management import call_command

        call_command("seed_demo", verbosity=0)

    def test_seed_creates_demo_data_on_empty_database(self):
        self._run_seed()

        user = get_user_model().objects.get(username="user")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(hasattr(user, "profile"))

        self.assertEqual(Post.objects.count(), 6)
        published = Post.objects.filter(status=Post.Status.PUBLISHED)
        self.assertEqual(published.count(), 5)
        self.assertTrue(published.exclude(published_at=None).count(), 5)

        draft = Post.objects.get(status=Post.Status.DRAFT)
        self.assertEqual(draft.title, "Draft")
        self.assertIsNone(draft.published_at)

    def test_seed_is_idempotent(self):
        self._run_seed()
        first_slugs = list(Post.objects.order_by("pk").values_list("slug", flat=True))

        self._run_seed()

        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(Post.objects.count(), 6)
        self.assertEqual(
            list(Post.objects.order_by("pk").values_list("slug", flat=True)),
            first_slugs,
        )

    def test_seed_restores_demo_content(self):
        self._run_seed()
        post = Post.objects.get(slug="understanding-blockchain")
        post.title = "Edited title"
        post.save()

        self._run_seed()

        post.refresh_from_db()
        self.assertEqual(post.title, "Understanding Blockchain")
        self.assertEqual(post.slug, "understanding-blockchain")

    def test_home_shows_seeded_published_posts(self):
        self._run_seed()

        response = self.client.get(reverse("index"))

        self.assertContains(response, "Why You Should Learn Rust in 2025")
        self.assertNotContains(response, ">Draft<")

    def test_fixture_loads_demo_data(self):
        from django.core.management import call_command

        call_command("loaddata", "demo", verbosity=0)

        self.assertEqual(Post.objects.count(), 6)
        self.assertEqual(
            Post.objects.filter(status=Post.Status.PUBLISHED).count(),
            5,
        )
        user = get_user_model().objects.get(username="user")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(hasattr(user, "profile"))

    def test_fixture_contains_no_password_hash(self):
        from django.conf import settings

        fixture = (settings.BASE_DIR / "blog/fixtures/demo.json").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("pbkdf2_", fixture)
        self.assertNotIn("argon2", fixture)
        self.assertIn('"password": "!"', fixture)


class DashboardViewTests(TestCase):
    """Tests for the authenticated user dashboard."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.owner = user_model.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="test-pass-123",
        )
        cls.other = user_model.objects.create_user(
            username="other",
            password="test-pass-123",
        )
        cls.published_one = Post.objects.create(
            title="Owner published one",
            content="Body",
            author=cls.owner,
            status=Post.Status.PUBLISHED,
        )
        cls.published_two = Post.objects.create(
            title="Owner published two",
            content="Body",
            author=cls.owner,
            status=Post.Status.PUBLISHED,
        )
        cls.owner_draft = Post.objects.create(
            title="Owner draft",
            content="Body",
            author=cls.owner,
            status=Post.Status.DRAFT,
        )
        cls.other_post = Post.objects.create(
            title="Other user post",
            content="Body",
            author=cls.other,
            status=Post.Status.PUBLISHED,
        )

    def _login_owner(self):
        self.client.force_login(self.owner)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )

    def test_shows_only_the_users_own_posts(self):
        self._login_owner()

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Owner published one")
        self.assertContains(response, "Owner draft")
        self.assertNotContains(response, "Other user post")
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_shows_account_summary(self):
        self._login_owner()

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "owner@example.com")
        self.assertContains(response, "owner")
        self.assertContains(response, "Member since")

    def test_stats_count_total_published_and_drafts(self):
        self._login_owner()

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(
            response.context["stats"],
            {"total": 3, "published": 2, "drafts": 1},
        )

    def test_draft_has_badge_and_no_public_link(self):
        self._login_owner()

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Owner draft")
        self.assertContains(response, "Draft")
        self.assertNotContains(
            response,
            self.owner_draft.get_absolute_url(),
        )
        self.assertContains(
            response,
            self.published_one.get_absolute_url(),
        )

    def test_paginates_six_posts_per_page(self):
        for index in range(5):
            Post.objects.create(
                title=f"Extra owner post {index}",
                content="Body",
                author=self.owner,
                status=Post.Status.PUBLISHED,
            )
        self._login_owner()

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(len(response.context["page_obj"]), 6)
        self.assertTrue(response.context["page_obj"].has_next())

    def test_empty_state_for_user_without_posts(self):
        empty_user = get_user_model().objects.create_user(
            username="empty",
            password="test-pass-123",
        )
        self.client.force_login(empty_user)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "You have no posts yet.")
