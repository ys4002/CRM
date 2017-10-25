# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-20 02:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_no', models.CharField(max_length=10)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('location', models.CharField(blank=True, max_length=30)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('avatar', models.ImageField(blank=True, default='logos/anonymous.png', null=True, upload_to='media')),
                ('phone', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('dj', models.DateTimeField(blank=True, null=True)),
                ('dtc', models.DateTimeField(blank=True, null=True)),
                ('dta', models.DateTimeField(blank=True, null=True)),
                ('added_by', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custo_id', models.IntegerField(blank=True, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('ag_nm', models.CharField(blank=True, max_length=40, null=True)),
                ('data', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ag_nm', models.CharField(blank=True, max_length=40, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('agen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.Agent')),
                ('cust', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='RelationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.TextField(blank=True, null=True)),
                ('cus', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
            ],
        ),
    ]
