# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-25 23:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_companycustomerrelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='Image',
            field=models.ImageField(default='logos/anonymous.png', upload_to=''),
        ),
    ]
