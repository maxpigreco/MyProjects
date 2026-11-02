from django.contrib.auth import logout as auth_logout
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path

from . import views


class LogoutAllowGetView(auth_views.LogoutView):
    """Log out from a GET link as well as the standard POST."""

    http_method_names = ["get", "post", "head", "options", "trace"]

    def get(self, request, *args, **kwargs):
        """Log the user out and redirect to the success URL."""
        auth_logout(request)
        return redirect(self.get_success_url())


urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutAllowGetView.as_view(next_page="login"), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("profile/", views.profile_view, name="profile"),  # optional
    path("profile/edit/", views.edit_profile_view, name="edit_profile")
]