# Generated by Django 2.1.5 on 2020-01-28 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mammoth', '0003_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]