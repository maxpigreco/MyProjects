from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path("contact/", views.contact_view, name="contact"),
    path("thanks/", TemplateView.as_view(
        template_name="blog/thanks.html"), name="contact_thanks"),
    path("search/", views.search_view, name="search"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path('', views.index_view, name="index"),
]