from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    """Create a profile for every user that does not have one yet."""
    Profile = apps.get_model("accounts", "Profile")
    User = apps.get_model("auth", "User")

    profiled_ids = Profile.objects.values_list("user_id", flat=True)
    missing_users = User.objects.exclude(pk__in=profiled_ids)
    Profile.objects.bulk_create(
        Profile(user=user) for user in missing_users.iterator()
    )


def keep_profiles(apps, schema_editor):
    """Profiles are legitimate data, so the reverse migration keeps them."""


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, keep_profiles),
    ]
