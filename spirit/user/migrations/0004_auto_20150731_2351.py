# -*- coding: utf-8 -*-
from django.db import models, migrations


def migrate_profiles(apps, schema_editor):
    from ...core.conf import settings

    User = apps.get_model(settings.AUTH_USER_MODEL)
    UserProfile = apps.get_model('spirit_user', 'UserProfile')

    users = User.objects.filter(st=None)

    # Avoid using bulk_create coz there are things setted on save
    for user in users:
        st = UserProfile()
        st.user = user
        st.is_verified = True
        st.save()


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_user', '0003_auto_20150728_0448'),
    ]

    operations = [
        migrations.RunPython(migrate_profiles),
    ]
