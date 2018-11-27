# Generated by Django 2.0.8 on 2018-11-22 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('juntagrico', '0015_auto_20180924_2053'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('units', models.FloatField(default=0, verbose_name='Grösse')),
                ('unit_multiplier', models.IntegerField(default=1, verbose_name='Grössen multiplikator')),
                ('unit_name', models.CharField(default='', max_length=100, verbose_name='Name Grösse')),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico_custom_sub.Product')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='juntagrico.Subscription')),
            ],
        ),
    ]
