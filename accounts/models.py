from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    #  add more fields as needed:
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # birthdate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile."
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


    # request.user.profile.bio

    # <p>{{ user.profile.bio }}</p>