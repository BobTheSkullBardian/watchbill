# Generated by Django 3.1.7 on 2021-05-27 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sailors', '0007_sailor_in_teams'),
    ]

    operations = [
        migrations.CreateModel(
            name='UA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_dt', models.DateTimeField(help_text='Start Day/Time', verbose_name='Beginning of Unavailability')),
                ('end_dt', models.DateTimeField(help_text='End Day/Time', verbose_name='End of Unavailability')),
                ('desc', models.CharField(blank=True, max_length=100, null=True, verbose_name='Description')),
                ('sailor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sailors.sailor', verbose_name='Watch Stander')),
            ],
        ),
    ]
