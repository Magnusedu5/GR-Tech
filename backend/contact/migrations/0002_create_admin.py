"""
Data migration: creates/updates the admin superuser from env vars.
Runs on every `python manage.py migrate` — safe to re-run (uses get_or_create).
"""
import os
from django.db import migrations


def create_or_update_admin(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
    email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

    if not username or not password:
        print('DJANGO_SUPERUSER_* env vars not set — skipping admin creation.')
        return

    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.email        = email
    user.is_staff     = True
    user.is_superuser = True
    user.is_active    = True
    if not user.first_name:
        user.first_name = 'Magnus'
        user.last_name  = 'Edu'
    user.save()
    print(f"Admin user {'created' if created else 'updated'}: {username}")


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_or_update_admin, migrations.RunPython.noop),
    ]
