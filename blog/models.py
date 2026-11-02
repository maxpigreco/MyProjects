from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Post(models.Model):
    """A blog post with an explicit publication status."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author_name = models.CharField(max_length=100, blank=True, default="")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(
                fields=["status", "-published_at"],
                name="post_status_pub_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Return the public URL for this post."""
        return reverse("post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs) -> None:
        """Generate a unique slug and set published_at on first publication."""
        self.slug = self._unique_slug()
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def _unique_slug(self) -> str:
        """Return a unique slug based on the current slug or the title."""
        base = slugify(self.slug or self.title) or "post"
        base = base[:190]
        candidate = base
        suffix = 2
        while (
            Post.objects.filter(slug=candidate)
            .exclude(pk=self.pk)
            .exists()
        ):
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate


class ContactMessage(models.Model):
    """A message submitted through the public contact form."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Contact messages"

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
