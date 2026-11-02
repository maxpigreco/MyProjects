from django.contrib import admin

from .models import Post


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
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at", "-created_at")
    readonly_fields = ("created_at", "published_at", "updated", "author_name")
    list_select_related = ("author",)

    # The public post detail route is added in WP5.
    view_on_site = False
