from django.contrib import admin
from .models import Post
from django.utils.text import slugify

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display        = ('id', 'title', 'author', 'published', 'is_public')
    list_filter         = ('is_public', 'published')
    search_fields       = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}  # auto-fills slug
    ordering            = ('-published',)

    # read-only fields
    readonly_fields = ('published', 'updated')

    # save override, lowercase slug force
    def save_model(self, request, obj, form, change):
        obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)