# Generated by Django 2.1.15 on 2022-05-01 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_slideshow_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='slideshow',
            name='pictures',
            field=models.ManyToManyField(to='core.Picture'),
        ),
    ]
