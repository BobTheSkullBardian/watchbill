from django.db import models

from django.urls import reverse
from sailors.models import Sailor, Qual


class Event(models.Model):
    class Meta:
        verbose_name = u'Duty Day'
        verbose_name_plural = u'Duty Days'
        ordering = (
            'day',
            'position__qual',
            'position__label',
        )

    def __str__(self):
        display = f'{self.position} {self.day} {self.stander}'
        return display

    def __retr__(self):
        return f'{self.position} {self.day} {self.stander}'

    def get_stander(self):
        return self.stander

    def get_position(self):
        return self.position

    def absolute_url(self):
        label = self._meta.app_label
        name = self._meta.model_name
        url = reverse(f'admin:{label}_{name}_change', args=[self.id])
        return f'<a href="{url}">{str(self.position)}</a>'

    def get_absolute_url(self, nostyle=False, auth=False):
        label = self._meta.app_label
        name = self._meta.model_name
        if not auth:
            return f'{self.position}'
        style = ' style="color: black; text-decoration: none;"'
        url = reverse(f'admin:{label}_{name}_change', args=[self.id])
        return f'<a href="{url}"{("", style)[nostyle]}>{self.position}</a>'
        # return f'<a href="{url}" style="{flat}">{str(self.position)}</a>'

    def get_day_url(self, day, watches, npstyle=False):
        label = self._meta.app_label
        name = self._meta.model_name
        url = reverse(f'admin:{label}_{name}_change', args=[self.id])
        return f'<a href="{url}">{day}</a>'

    def popups(self):
        # print(dir(self))
        pass

    day = models.DateField(
        u'Day of the Watch', help_text=u'Day of the Watch')
    position = models.ForeignKey(
        'Position', verbose_name='Position', on_delete=models.CASCADE)
    notes = models.CharField(
        u'Watch Notes', max_length=100, blank=True, null=True)
    stander = models.ForeignKey(
        Sailor, verbose_name='Watch Stander', on_delete=models.CASCADE)
    acknowledged = models.BooleanField(
        'Watch Acknowledged', default=False, blank=True)
    active = models.BooleanField('Active', default=True)


class Position(models.Model):
    POS = (
        ('OOD Day', 'OOD Day'),
        ('OOD Mid', 'OOD Mid'),
        ('JOOD Day', 'JOOD Day'),
        ('JOOD Mid', 'JOOD Mid'),
        ('Duty Driver', 'Duty Driver'),
        ('NBP 306', 'NBP 306'),
    )

    class Meta:
        ordering = ('qual',
                    'label',
                    )

    def __str__(self):
        return f'{self.qual}{("", f" {self.label}")[len(self.label)>0]}'

    def __retr__(self):
        return self

    position = models.CharField(
        u'Watch Position', max_length=15, blank=True, null=True,)
    qual = models.ForeignKey(
        Qual, on_delete=models.CASCADE,
        verbose_name='Watch Position', blank=True)
    label = models.CharField(
        u'Label', max_length=15, default="", blank=True)
    start_time = models.TimeField(
        u'Watch starting time', help_text=u'Watch starting time')
    duration = models.IntegerField(default=12, blank=True, null=True)
