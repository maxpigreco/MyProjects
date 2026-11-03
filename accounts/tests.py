import re
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Profile


class ProfileSignalTests(TestCase):
    """Tests for automatic profile creation on user save."""

    def test_profile_is_created_for_new_user(self):
        user = get_user_model().objects.create_user(
            username="newuser",
            password="test-pass-123",
        )

        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_saving_user_twice_does_not_duplicate_profile(self):
        user = get_user_model().objects.create_user(
            username="repeatuser",
            password="test-pass-123",
        )
        profile = user.profile
        profile.bio = "Original bio"
        profile.save()

        user.save()
        user.refresh_from_db()
        profile.refresh_from_db()

        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
        self.assertEqual(profile.bio, "Original bio")

    def test_user_without_profile_gets_one_on_save(self):
        user = get_user_model().objects.create_user(
            username="orphanuser",
            password="test-pass-123",
        )
        Profile.objects.filter(user=user).delete()

        user.save()

        self.assertTrue(Profile.objects.filter(user=user).exists())


class EditProfileViewTests(TestCase):
    """Tests for the login protection and feedback of the profile form."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="profileuser",
            password="test-pass-123",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("edit_profile"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('edit_profile')}",
        )

    def test_logged_in_user_can_update_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("edit_profile"),
            {"bio": "Updated bio"},
            follow=True,
        )

        self.assertRedirects(response, reverse("profile"))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, "Updated bio")
        self.assertIn(
            "Profile updated.",
            [str(message) for message in response.context["messages"]],
        )

    def test_user_without_profile_can_open_the_form(self):
        Profile.objects.filter(user=self.user).delete()
        self.client.force_login(self.user)

        response = self.client.get(reverse("edit_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())


class SignupTests(TestCase):
    """Tests for profile creation during signup."""

    def test_signup_creates_profile(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "signupuser",
                "email": "signup@example.com",
                "password1": "Str0ng-Pass-123",
                "password2": "Str0ng-Pass-123",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = get_user_model().objects.get(username="signupuser")
        self.assertTrue(Profile.objects.filter(user=user).exists())


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class PasswordResetFlowTests(TestCase):
    """Tests for the complete password reset flow."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="Old-pass-123",
        )

    def test_full_password_reset_flow(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "reset@example.com"},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password reset", mail.outbox[0].subject)

        match = re.search(r"https?://\S+", mail.outbox[0].body)
        self.assertIsNotNone(match)
        token_path = urlparse(match.group(0)).path

        response = self.client.get(token_path)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(response["Location"])
        self.assertEqual(response.status_code, 200)
        set_password_path = response.request["PATH_INFO"]

        response = self.client.post(
            set_password_path,
            {
                "new_password1": "New-pass-456",
                "new_password2": "New-pass-456",
            },
        )

        self.assertRedirects(response, reverse("password_reset_complete"))
        self.assertTrue(
            self.client.login(
                username="resetuser",
                password="New-pass-456",
            )
        )
        self.assertFalse(
            self.client.login(
                username="resetuser",
                password="Old-pass-123",
            )
        )

    def test_unknown_email_sends_no_message(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "missing@example.com"},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)


class LogoutTests(TestCase):
    """Tests for the GET- and POST-compatible logout view."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="logoutuser",
            password="test-pass-123",
        )

    def _assert_logged_out(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_get_logout_logs_out_and_redirects(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self._assert_logged_out()

    def test_post_logout_logs_out_and_redirects(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self._assert_logged_out()
