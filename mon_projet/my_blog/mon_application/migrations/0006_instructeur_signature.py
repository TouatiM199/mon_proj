# Generated by Django 4.1.7 on 2023-03-17 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mon_application', '0005_remove_signature_signature_signature_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructeur',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to='signatures/'),
        ),
    ]
