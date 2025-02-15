from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment_like', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentlike',
            name='user',
            field=models.ForeignKey(related_name='st_comment_likes', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
