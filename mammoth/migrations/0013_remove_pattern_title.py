# Generated by Django 2.1.5 on 2020-03-03 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mammoth', '0012_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pattern',
            name='title',
        ),
    ]
