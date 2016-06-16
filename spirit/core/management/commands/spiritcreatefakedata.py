# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand


# word_file = "/etc/dictionaries-common/words"
# WORDS = open(word_file).read().splitlines()

CATEGORIES_NUM = 1
TOPIC_NUM = 1000
COMMENTS_NUM = 1000
COMMENT_TXT = (
    'Lorem ipsum dolor sit amet, '
    'consectetur adipiscing elit. '
    'Curabitur vulputate eget lectus '
    'vel pretium. Maecenas pretium '
    'volutpat scelerisque. In at orci felis. '
    'Mauris sed finibus lorem, pharetra '
    'ultricies sapien. Integer a venenatis '
    'risus. Aliquam id efficitur eros. '
    'Vestibulum diam neque, fermentum '
    'ac diam ut, pharetra placerat nunc. '
    'Aenean sed lorem tortor. Vestibulum '
    'ante ipsum primis in faucibus orci '
    'luctus et ultrices posuere cubilia Curae; '
    'Integer sollicitudin purus ac est tempus, '
    'ac posuere lacus placerat. Quisque faucibus '
    'at massa pretium posuere. Nulla quam leo, '
    'ullamcorper non nunc ac, viverra blandit est. '
    'Nullam eget tellus at metus gravida dignissim. '
    'Pellentesque commodo pulvinar est quis '
    'pulvinar. Pellentesque ut velit condimentum, '
    'commodo orci nec, venenatis nisi. '
    'Nam non mollis ex. ')


class Command(BaseCommand):
    help = 'Populate the DB with fake data.'

    def handle(self, *args, **options):
        import random

        from django.contrib.auth import get_user_model

        from ....category.models import Category
        from ....topic.models import Topic
        from ....comment.models import Comment

        User = get_user_model()

        if (User.objects.all().count() or
                Topic.objects.all().count()):
            raise Exception(
                'This must be done in '
                'a clean database')

        user = User.objects.create(
            username='ST_fake',
            email='fake@fake.com',
            password='fake')

        Category.objects.bulk_create(
            Category(title='title %d' % i)
            for i in range(CATEGORIES_NUM))

        for category in Category.objects.all().order_by('-pk')[:CATEGORIES_NUM]:
            Topic.objects.bulk_create(
                Topic(
                    user=user,
                    category=category,
                    title='title %d' % i)
                for i in range(TOPIC_NUM))

        for topic in Topic.objects.all():
            Comment.objects.bulk_create(
                Comment(
                    user=user,
                    topic=topic,
                    comment='',
                    comment_html=COMMENT_TXT)  # ' '.join(random.choice(WORDS) for _ in range(100))
                for _ in range(COMMENTS_NUM))

        self.stdout.write('ok')
