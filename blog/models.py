from django.db import models

# Create your models here.
# Post Model

class Post(models.Model):
    title           = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True)
    author          = models.CharField(max_length=100)
    content         = models.TextField()
    published       = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    is_public       = models.BooleanField(default=True)
    views           = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-published']
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title
        