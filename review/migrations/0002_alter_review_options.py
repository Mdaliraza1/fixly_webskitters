# Generated by Django 5.0.7 on 2025-06-12 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['created_at']},
        ),
    ]
