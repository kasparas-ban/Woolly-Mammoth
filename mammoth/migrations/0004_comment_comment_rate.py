# Generated by Django 2.1.5 on 2020-03-09 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mammoth', '0003_delete_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_rate',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
    ]
