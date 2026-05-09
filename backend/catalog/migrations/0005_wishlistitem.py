import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_item_collection'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('collection_type', models.CharField(choices=[('video_games', 'Video Games'), ('trading_cards', 'Trading Cards'), ('comics', 'Comics'), ('funko_pops', 'Funko Pops'), ('lego_sets', 'LEGO Sets'), ('sports_cards', 'Sports Cards'), ('music', 'Music'), ('movies', 'Movies')], default='video_games', max_length=50)),
                ('notes', models.TextField(blank=True, default='')),
                ('price_target', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('link', models.URLField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
