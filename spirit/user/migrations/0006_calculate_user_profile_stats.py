# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def calculate_user_profile_stats(apps, schema_editor):
    UserProfile = apps.get_model("spirit_user", "UserProfile")
    Topic = apps.get_model("spirit_topic", "Topic")
    Comment = apps.get_model("spirit_comment", "Comment")
    CommentLike = apps.get_model("spirit_comment_like", "CommentLike")
    for profile in UserProfile.objects.all():
        profile.topic_count = Topic.objects.filter(category__is_private=False, user__st=profile).count()
        profile.comment_count = Comment.objects.filter(topic__category__is_private=False, user__st=profile).count()
        profile.given_likes_count = CommentLike.objects.filter(comment__topic__category__is_private=False, user__st=profile).count()
        profile.received_likes_count = CommentLike.objects.filter(comment__topic__category__is_private=False, comment__user__st=profile).count()
        profile.save()


def backwards_migration_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_user', '0005_auto_20151206_1214'),
    ]

    operations = [
        migrations.RunPython(calculate_user_profile_stats, backwards_migration_noop),
    ]
