# -*- coding: utf-8 -*-
from django.db import models, migrations


def default_categories(apps, schema_editor):
    from ...core.conf import settings

    Category = apps.get_model("spirit_category", "Category")

    if not Category.objects.filter(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK).exists():
        private_category = Category.objects.create(
            title="Private",
            slug="private",
            is_private=True)

        # Check the user has the right setting,
        # if the migration is re-ran with a bad
        # setting again then a duplicated is created
        # and it can be manually removed later
        if private_category.pk != settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
            raise ValueError(
                'ST_TOPIC_PRIVATE_CATEGORY_PK setting does not matches '
                'the private category. The expected value was: {pk}'.format(
                    pk=private_category.pk))

    # Create a dummy category in case
    # there are no categories other than
    # the Private one
    if len(Category.objects.all()[:2]) == 1:
        Category.objects.create(
            title="Uncategorized",
            slug="uncategorized")


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_category', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(default_categories),
    ]
