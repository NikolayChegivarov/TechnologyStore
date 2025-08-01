# Generated by Django 5.2.1 on 2025-07-17 09:48

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='store_app.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_products', to='store_app.customer')),
            ],
            options={
                'verbose_name': 'Избранный товар',
                'verbose_name_plural': 'Избранные товары',
                'ordering': ['-added_at'],
                'indexes': [models.Index(fields=['user', 'product'], name='store_app_f_user_id_0e40a2_idx')],
                'unique_together': {('user', 'product')},
            },
        ),
    ]
