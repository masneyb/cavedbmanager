# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cavedb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GisMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('website_url', models.CharField(max_length=255, null=True, blank=True)),
                ('license_url', models.CharField(max_length=255, null=True, blank=True)),
                ('map_label', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'GIS Map',
            },
        ),
        migrations.RemoveField(
            model_name='bulletin',
            name='bw_aerial_map',
        ),
        migrations.RemoveField(
            model_name='bulletin',
            name='color_aerial_map',
        ),
        migrations.RemoveField(
            model_name='gislayer',
            name='aerial_maps',
        ),
        migrations.DeleteModel(
            name='GisAerialMap',
        ),
        migrations.AddField(
            model_name='bulletin',
            name='bw_map1',
            field=models.ForeignKey(related_name='bw_map1', verbose_name=b'Map #1 for the B&W bulletin', blank=True, to='cavedb.GisMap', null=True),
        ),
        migrations.AddField(
            model_name='bulletin',
            name='bw_map2',
            field=models.ForeignKey(related_name='bw_map2', verbose_name=b'Map #2 for the B&W bulletin', blank=True, to='cavedb.GisMap', null=True),
        ),
        migrations.AddField(
            model_name='bulletin',
            name='bw_map3',
            field=models.ForeignKey(related_name='bw_map3', verbose_name=b'Map #3 for the B&W bulletin', blank=True, to='cavedb.GisMap', null=True),
        ),
        migrations.AddField(
            model_name='bulletin',
            name='color_map1',
            field=models.ForeignKey(related_name='color_map1', verbose_name=b'Map #1 for the color bulletin', blank=True, to='cavedb.GisMap', null=True),
        ),
        migrations.AddField(
            model_name='bulletin',
            name='color_map2',
            field=models.ForeignKey(related_name='color_map2', verbose_name=b'Map #2 for the color bulletin', blank=True, to='cavedb.GisMap', null=True),
        ),
        migrations.AddField(
            model_name='bulletin',
            name='color_map3',
            field=models.ForeignKey(related_name='color_map3', verbose_name=b'Map #3 for the color bulletin', blank=True, to='cavedb.GisMap', null=True),
        ),
        migrations.AddField(
            model_name='gislayer',
            name='maps',
            field=models.ManyToManyField(to='cavedb.GisMap'),
        ),
    ]
