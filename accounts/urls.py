from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

class LogoutAllowGetView(auth_views.LogoutView):
    http_method_names = ["get", "post", "head", "options", "trace"]

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutAllowGetView.as_view(next_page="login"), name="logout"),
    path("profile/", views.profile_view, name="profile"),  # optional
    path("profile/edit/", views.edit_profile_view, name="edit_profile")
]