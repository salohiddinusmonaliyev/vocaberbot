# Generated by Django 5.0.4 on 2024-04-05 05:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.telegramuser')),
            ],
        ),
        migrations.CreateModel(
            name='TestItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField()),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.test')),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.word')),
            ],
        ),
    ]
