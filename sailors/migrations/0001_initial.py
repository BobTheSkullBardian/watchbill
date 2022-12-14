# Generated by Django 3.1.3 on 2020-12-10 16:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Qual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qual', models.CharField(max_length=30, unique=True, verbose_name='Watch Qual')),
                ('jqr', models.BooleanField(default=True, verbose_name="JQR Req'd"))
            ],
            options={
                'verbose_name': 'Qualification',
                'verbose_name_plural': 'Qualifications',
            },
        ),
        migrations.CreateModel(
            name='Sailor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('name', models.CharField(max_length=40, verbose_name='Name')),
                ('quald', models.BooleanField(default=False, verbose_name='Qualified')),
                ('rate', models.CharField(choices=[('CTN1', 'CTN1'), ('CTN2', 'CTN2'), ('CTN3', 'CTN3'), ('CTNSN', 'CTNSN'), ('CTNSA', 'CTNSA'), ('CTNSR', 'CTNSR'), ('CTR1', 'CTR1'), ('CTR2', 'CTR2'), ('CTR3', 'CTR3'), ('CTRSN', 'CTRSN'), ('CTRSA', 'CTRSA'), ('CTRSR', 'CTRSR'), ('CTI1', 'CTI1'), ('CTI2', 'CTI2'), ('CTI3', 'CTI3'), ('CTISN', 'CTISN'), ('CTISA', 'CTISA'), ('CTISR', 'CTISR'), ('IT1', 'IT1'), ('IT2', 'IT2'), ('IT3', 'IT3'), ('ITSN', 'ITSN'), ('ITSA', 'ITSA'), ('ITSR', 'ITSR'), ('IS1', 'IS1'), ('IS2', 'IS2'), ('IS3', 'IS3'), ('ISSN', 'ISSN'), ('ISSA', 'ISSA'), ('ISSR', 'ISSR')], max_length=5, verbose_name='Rate')),
                ('dept', models.CharField(default='', choices=[('31', '31'), ('32', '32'), ('33', '33'), ('34', '34'), ('35', '35')], max_length=2, verbose_name='Department')),
                ('phone', models.CharField(blank=True, default='', max_length=12, validators=[django.core.validators.RegexValidator(regex='^(\\d{3}-\\d{3}-\\d{4})?')], verbose_name='Phone #')),
                ('email', models.EmailField(blank=True, default='', max_length=50, verbose_name='Email')),
                ('work_email', models.EmailField(blank=True, max_length=50, null=True, verbose_name='Professional Email')),
                ('in_teams', models.CharField(default='', choices=[('CVR', 'CVR'), ('Guest', 'Guest')], max_length=5, verbose_name='Teams Access')),
                ('report', models.DateField(blank=True, null=True, verbose_name='Report Date')),
                ('qualdate', models.DateField(blank=True, null=True, verbose_name="Date Qual'd")),
                ('notes', models.CharField(blank=True, default='', max_length=100, verbose_name='Notes')),
                ('availability', models.CharField(blank=True, default='', max_length=100, verbose_name='Availability')),
                ('qual', models.ManyToManyField(blank=True, default=None, to='sailors.Qual', verbose_name='Watch Qualification')),
            ],
            options={
                'ordering': ('-qual__qual', 'name'),
            },
        ),
    ]
