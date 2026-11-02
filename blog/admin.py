from django.contrib import admin

from .models import ContactMessage, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "status",
        "published_at",
        "created_at",
    )
    list_filter = ("status", "published_at")
    search_fields = ("title", "content", "author__username", "author_name")
    ordering = ("-published_at", "-created_at")
    readonly_fields = (
        "slug",
        "created_at",
        "published_at",
        "updated",
        "author_name",
    )
    list_select_related = ("author",)
    view_on_site = True


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "message")
    ordering = ("-created_at",)
    readonly_fields = ("name", "email", "message", "created_at")
