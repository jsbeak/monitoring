# Generated by Django 3.1.7 on 2021-04-28 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jwmonitor', '0018_auto_20210420_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectinfo',
            name='pro_ip',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='projectinfo',
            name='pro_active_yn',
            field=models.CharField(choices=[('Y', 'Y'), ('N', 'N')], default='Y', max_length=1),
        ),
    ]