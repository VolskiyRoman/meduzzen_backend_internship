# Generated by Django 4.2.5 on 2023-10-18 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0002_alter_actions_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actions',
            old_name='company_id',
            new_name='company',
        ),
        migrations.RenameField(
            model_name='actions',
            old_name='status',
            new_name='status_id',
        ),
    ]
