# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-18 12:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaint', '0003_auto_20160518_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='Image',
            field=models.ImageField(upload_to=b'/home/testbed/pothole/newserver/pothole-server/media/images', verbose_name=b'Image'),
        ),
    ]