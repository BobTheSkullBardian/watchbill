from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse
from datetime import date, timedelta
from string import ascii_uppercase
import calendar
import json

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def create_sailor(data):
    try:
        sailor = Sailor.objects.get(
            name=data['name'],
        )
        sailor.update(**data)
        return False

    except Sailor.DoesNotExist:
        return True


class Sailor(models.Model):
    class Meta:
        ordering = (
            # '-qual__qual',
            'name',
            # 'qualdate',
        )

    def __str__(self):
        display_fields = [
            self.name,
            self.rate,
            # self.phone,
            # *self.quals(),
        ]
        display = ", ".join([field for field in display_fields])
        return display

    def rate_lname(self):
        return f'{self.rate} {self.name.split(",")[0]}'

    def __retr__(self):
        return self

    def get_absolute_url(self, nostyle=False, auth=False):
        label = self._meta.app_label
        name = self._meta.model_name
        styledict = {}
        if not auth:
            styledict["pointer-events"] = "none"
        if nostyle:
            styledict["color"] = "black"
            styledict["text-decoration"] = "none"
        style = 'style="' + json.dumps(styledict).replace(',', ';').strip('{}').replace('"', '') + '"'
        url = reverse(f'admin:{label}_{name}_change', args=[self.id])
        return f'<a href="{url}" {style}>{self.rate_lname()}</a>'

    def quals(self):
        return [str(q) for q in self.qual.all()]

    def dept_div(self):
        if self.div:
            return self.dept + self.div
        else:
            return self.dept
    dept_div.admin_order_field = 'dept'

    def dinq_date(self):
        if self.quald:
            return f'{self.off_wb_date()} months left on WB'
        if self.report:
            days_to_qual = 30
            today = date.today()
            delta = timedelta(days=days_to_qual)
            dinq = self.report + delta
            if today > dinq:
                return f'{(today - dinq).days} days past {dinq.strftime("%b. %d, %Y")}'
            else:
                return f'{(dinq - today).days} days until {dinq.strftime("%b. %d, %Y")}'

        else:
            return None
    dinq_date.admin_order_field = 'qualdate'

    def off_wb_date(self):
        today = date.today()
        if not all((self.quald, self.qualdate)):
            return
        else:
            # delta = timedelta(days=365)
            done = self.qualdate.replace(day=1, year=self.qualdate.year + 1)
            months = round((done - today.replace(day=1)).days / 30)
            return f'{months}'
    off_wb_date.admin_order_field = 'qualdate'
    off_wb_date.short_description = 'Months left on WB'

    DEPTS = (
        ('31', '31'),
        ('32', '32'),
        ('33', '33'),
        ('34', '34'),
        ('35', '35'),
    )

    DIVS = [
        (
            y, y
        )
        for y in [
            '',
            *list(ascii_uppercase)[:5]
        ]
    ]

    RATES = [
        (x + y, x + y) for x in [
            'CTN',
            'CTR',
            'CTI',
            'IT',
            'IS',
        ] for y in [
            '1',
            '2',
            '3',
            'SN',
            'SA',
            'SR',
        ]
    ]

    active = models.BooleanField('Active', default=True)
    name = models.CharField('Name', max_length=40)
    qual = models.ManyToManyField(
        'Qual', verbose_name='Watch Qualification', blank=True, default=None)
    quald = models.BooleanField('Qualified', default=False)
    rate = models.CharField(
        'Rate', max_length=5, choices=RATES)
    dept = models.CharField(
        'Department', max_length=2, choices=DEPTS, default="35", null=True, blank=True)
    div = models.CharField(
        'Division', max_length=1,
        choices=DIVS,
        blank=True,
        default="")
    phone_regex = RegexValidator(regex=r'^(\d{3}-\d{3}-\d{4})?')
    phone = models.CharField(
        'Phone #', validators=(phone_regex,), max_length=12,
        blank=True, default='')
    email = models.EmailField('Email', max_length=50, default="", blank=True)
    work_email = models.EmailField(
        'Professional Email', max_length=50, null=True, blank=True)
    teams_type = models.CharField(
        'Teams Access', choices=[('CVR', 'CVR'), ('Guest', 'Guest')],
        max_length=5, default="")
    in_teams = models.BooleanField("In Teams", default=False)
    slack_inv = models.BooleanField("Slack Invite", default=False)
    slack_act = models.BooleanField("Active Slack", default=False)
    report = models.DateField("Report Date", null=True, blank=True)
    qualdate = models.DateField("Date Qual'd", null=True, blank=True)
    coversheet = models.BooleanField('Cover Sheet Uploaded', default=False)
    notes = models.CharField(
        'Notes',
        max_length=100,
        default="", blank=True)
    availability = models.CharField(
        'Availability', max_length=100, default="", blank=True)


class Qual(models.Model):
    class Meta:
        verbose_name = u'Qualification'
        verbose_name_plural = u'Qualifications'

    def __str__(self):
        return str(self.qual)

    def __retr__(self):
        return self.qual

    def admin_filter(self, nostyle=False):
        style = ' style="color: black; text-decoration: none; font-weight: bold;"'
        url = f'/admin/sailors/sailor/?qual={self.id}'
        return f'<a href="{url}"{("", style)[nostyle]}>{self}</a>'

    qual = models.CharField('Watch Qual', max_length=30, unique=True)
    jqr = models.BooleanField(
        "JQR Req'd", default=True)


class UA(models.Model):
    sailor = models.ForeignKey(
        Sailor, verbose_name='Watch Stander', on_delete=models.CASCADE)
    start = models.DateField(
        u'Beginning of Unavailability', help_text=u'Start Day', null=True)
    end = models.DateField(
        u'End of Unavailability', help_text=u'End Day/Time', null=True)
    desc = models.CharField(
        u'Description', max_length=100, blank=True, null=True,)
