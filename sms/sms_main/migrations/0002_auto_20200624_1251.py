# Generated by Django 3.0.6 on 2020-06-24 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuserprofile',
            name='profile_pic',
            field=models.ImageField(blank=True, default='/default.png', upload_to='photos/%Y/%m/%d'),
        ),
    ]
