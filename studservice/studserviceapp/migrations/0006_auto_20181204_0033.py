# Generated by Django 2.1.2 on 2018-12-03 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studserviceapp', '0005_auto_20181204_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='slika',
            field=models.ImageField(upload_to='djangouploads'),
        ),
    ]
