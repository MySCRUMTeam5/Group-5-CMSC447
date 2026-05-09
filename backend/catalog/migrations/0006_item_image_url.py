from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_wishlistitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image_url',
            field=models.URLField(blank=True, default=''),
        ),
    ]
