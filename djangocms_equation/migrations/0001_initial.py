# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-24 18:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquationPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='djangocms_equation_equationpluginmodel', serialize=False, to='cms.CMSPlugin')),
                ('tex_code', models.CharField(blank=True, max_length=512, verbose_name='tex_code')),
                ('is_inline', models.BooleanField(verbose_name='is_inline')),
                ('font_size_value', models.FloatField(default=1, verbose_name='font_size_value')),
                ('font_size_unit', models.CharField(choices=[('cm', 'cm'), ('mm', 'mm'), ('in', 'in'), ('px', 'px'), ('pt', 'pt'), ('pc', 'pc'), ('em', 'em'), ('ex', 'ex'), ('ch', 'ch'), ('rem', 'rem'), ('vw', 'vw'), ('vh', 'vh'), ('vmin', 'vmin'), ('vmax', 'vmax'), ('%', '%')], max_length=5, verbose_name='font_size_unit')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
