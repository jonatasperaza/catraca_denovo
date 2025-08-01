# Generated by Django 5.2.4 on 2025-07-17 14:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessRule',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('type', models.IntegerField(default=1)),
                ('priority', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TimeZone',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PortalAccessRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portal_id', models.IntegerField()),
                ('access_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='control_id_django_app.accessrule')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('template', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='templates', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimeSpan',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
                ('sun', models.BooleanField(default=False)),
                ('mon', models.BooleanField(default=False)),
                ('tue', models.BooleanField(default=False)),
                ('wed', models.BooleanField(default=False)),
                ('thu', models.BooleanField(default=False)),
                ('fri', models.BooleanField(default=False)),
                ('sat', models.BooleanField(default=False)),
                ('hol1', models.BooleanField(default=False)),
                ('hol2', models.BooleanField(default=False)),
                ('hol3', models.BooleanField(default=False)),
                ('time_zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spans', to='control_id_django_app.timezone')),
            ],
        ),
        migrations.CreateModel(
            name='AccessRuleTimeZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='control_id_django_app.accessrule')),
                ('time_zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='control_id_django_app.timezone')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccessRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='control_id_django_app.accessrule')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
