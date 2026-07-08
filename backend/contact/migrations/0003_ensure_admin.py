"""
Ensure the admin superuser exists on every fresh database.
Reads from DJANGO_SUPERUSER_* env vars; falls back to the
values from the render.yaml build command so deploys always
produce a working admin account even without manual env var setup.
"""
import os
from django.db import migrations


def ensure_admin(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'magnus')
    email    = os.environ.get('DJANGO_SUPERUSER_EMAIL',    'magnusedu5@gmail.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Mag123456789@')

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
        ('contact', '0002_create_admin'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(ensure_admin, migrations.RunPython.noop),
    ]
