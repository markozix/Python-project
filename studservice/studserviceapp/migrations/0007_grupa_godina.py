# Generated by Django 2.1.2 on 2019-01-15 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studserviceapp', '0006_auto_20181204_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupa',
            name='godina',
            field=models.IntegerField(null=True),
        ),
    ]
