# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import trusts.models


class Migration(migrations.Migration):

    dependencies = [
        ('trusts', '0001_initial'),
        ('spirit_category', '0003_category_is_global'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryJunction',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
            ],
            options={
                'content_permission_conditions': (),
                'abstract': False,
                'default_permissions': (),
            },
            bases=(trusts.models.ReadonlyFieldsMixin, models.Model),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories', 'verbose_name': 'category', 'ordering': ['title', 'pk'], 'default_permissions': ('add', 'change', 'delete', 'read', 'add_topic_to')},
        ),
        migrations.AddField(
            model_name='categoryjunction',
            name='content',
            field=models.ForeignKey(related_name='trust_junction', to='spirit_category.Category'),
        ),
        migrations.AddField(
            model_name='categoryjunction',
            name='trust',
            field=models.ForeignKey(to='trusts.Trust', default=999000000000001L, related_name='spirit_category_categoryjunction'),
        ),
        migrations.AlterUniqueTogether(
            name='categoryjunction',
            unique_together=set([('content',)]),
        ),
    ]
