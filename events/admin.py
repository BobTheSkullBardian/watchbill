from django.contrib import admin
from .models import Event, Position
from sailors.models import Sailor
from datetime import date, timedelta
import calendar
import json
from collections import defaultdict
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import (
    render,
    redirect,
)
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.contrib.admin import SimpleListFilter
from django.http import QueryDict
from sailors.admin import DefaultListFilter


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


class AckFilter(DefaultListFilter):
    title = _('Watch Acknowledged ')
    parameter_name = 'acknowledged__exact'
    today = date.today()

    def lookups(self, request, model_admin):
        return (
            (0, 'No'),
            (1, 'Yes'),
            # ('_all', 'All'),
        )

    def default_value(self):
        return all_value

    def queryset(self, request, queryset):
        # querysey = queryset.filter(day__gte=today)
        if self.parameter_name in request.GET and request.GET[self.parameter_name] == self.all_value:
            return queryset.filter(day__gte=today)

        if self.parameter_name in request.GET:
            return queryset.filter(day__gte=today, **{self.parameter_name: request.GET[self.parameter_name]})

        return queryset.filter(day__gte=today, **{self.parameter_name: self.default_value()})


class DayFilter(SimpleListFilter):
    title = _('Day ')
    parameter_name = 'day'  # __gte'
    all_value = '_all'
    day_diff = timedelta(days=1)
    today = date.today()
    a_week = day_diff * 6
    next_month = add_months(today, 1)
    last_month = add_months(today, -1)

    def dutyday(self):
        day = Event.objects.filter(
            day__gte=self.today,
            day__lte=self.today + self.a_week).first().day
        while True:
            yield day
            day += self.a_week

    def lookups(self, request, model_admin):
        # dates = []
        dates = sorted(list(set(event.day for _, event in enumerate(Event.objects.filter(day__gte=self.today)))))
        for retval in (('day', date, date) for date in dates):
            yield retval
        months = sorted(list(set(
            (event.day.year, event.day.month) for _, event in enumerate(
                Event.objects.filter(day__gte=self.today)))))
        for retval in (('day__month', month, date(year, month, 1).strftime("%B %Y")) for year, month in months):
            yield retval

    # def default_value(self):
        # return self.today

    def queryset(self, request, queryset):
        request_GET = request.GET.dict()
        if 'day' in request_GET and 'day__gte' in request_GET:
            request_GET.pop('day__gte')
        if self.parameter_name in request.GET and request.GET[self.parameter_name] == self.all_value:
            return queryset  #.filter(**request_GET)

        if self.parameter_name in request.GET:
            return queryset.filter(
                **{self.parameter_name: request.GET[self.parameter_name]})
        return queryset.filter(
            # **{self.parameter_name: self.default_value()},
            )

    def choices(self, cl):
        yield {
            'selected': self.value() == self.all_value,
            'query_string': cl.get_query_string({
                self.parameter_name: self.all_value}, [self.parameter_name, 'day_gte']),
            'display': _('All'),
        }
        yield {
            'selected': self.value() == self.all_value,
            'query_string': cl.get_query_string({
                'day__gte': self.today}, [self.parameter_name]),
            'display': _('Future'),
        }
        for parameter, lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    parameter: lookup}, [self.parameter_name]),
                'display': title,
            }


def ack(modeladmin, request, queryset):
    queryset.update(acknowledged=True)


def make_month(modeladmin, request, queryset):
    positions = Position.objects.all()
    # print(positions)
    month = queryset.first().day.month
    day = Event.objects.filter(day__month=month-1).order_by('day').last().day
    day += timedelta(days=6)
    null_stander = Sailor.objects.get(name='Null, Null')
    while day.month == month:
        # print(day)
        for position in positions:
            # print(position)
            events = Event.objects.filter(day=day, position=position)
            if not len(events):
                event = Event(position=position, day=day, stander=null_stander)
                # print(event)
                event.save()
            # else:
            #     print(events)
        day += timedelta(days=6)

    # print(Position.objects.all().aggregate())
    # if (day - timedelta(days=6)).month != day.month:
    #     print('first day')
    # # month = queryset.order_by('day').last().day.month
    # print(day)


def show_messages(modeladmin, request, queryset):
    watches = [watch for watch in queryset]
    # print(dir(watches[0]))
    return render(request, 'recall.html', {'watches': watches})


def show_quickview(modeladmin, request, queryset):
    data = defaultdict(lambda: defaultdict(list))
    for i, watch in enumerate(queryset):
        day = watch.day
        qual = watch.position.qual
        # stander = f'{watch.stander.rate} {watch.stander.name.split(",")[0]}'
        data[f'{day}'][f'{qual}'].append(watch)
        # # print(watch.day)
        # data[watch.day][watch.position.label].append(watch)
        # for watch in dutyday.watch_set.all():
        #     data[dutyday].append(watch.get_data())
    # for date, watches in data.items():
    #     print(date)
    #     for watch in watches:
    #         print(f'{watch.stander.rate} {watch.stander.name.split(",")[0]}')
    data = dict(data.items())
    _data = {}
    for _day, _quals in data.items():
         for _qual, _watches in _quals.items():
            _data[_day] = {_qual: [_watch for _watch in _watches]}
    # print(json.dumps(data)) 
    return render(
        request, 'quickview.html',
        {'data': data},
        # data,
    )


# @admin.register(Position)
# class PositionAdmin(admin.ModelAdmin):
#     pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'day',
        # 'day_weekday',
        # 'get_pos_label',
        'position',
        # 'stander',
        'link_to_stander',
        'acknowledged',
        'stander_quald',
        'link_to_stander_avail',
        'notes',
    ]

    actions = (
        show_messages,
        show_quickview,
        ack,
        make_month,
    )

    list_filter = [
        DayFilter,
        'position__qual',
        # AckFilter,
        'acknowledged',
        'stander__quald',
        'active',
    ]

    fields = [
        'active',
        ('day', 'position',),
        'stander',
        'notes',
        'acknowledged',
    ]

    list_display_links = (
        'day',
        'notes',
    )

    def get_pos_label(self, obj):
        return obj.position.label
    get_pos_label.short_description = 'Position'
    get_pos_label.admin_order_field = 'position__label'

    def link_to_stander(self, obj):
        link = reverse("admin:sailors_sailor_change", args=[obj.stander_id])
        return format_html('<a href="{}">{}</a>', link, obj.stander)
    link_to_stander.short_description = 'Watchstander'
    link_to_stander.admin_order_field = 'stander__name'

    def link_to_stander_avail(self, obj):
        link = reverse("admin:sailors_sailor_change", args=[obj.stander_id])
        return format_html('<a href="{}">{}</a>', link, obj.stander.availability)
    link_to_stander_avail.short_description = 'Availability'
    link_to_stander_avail.admin_order_field = 'stander__availability'

    def stander_quald(self, obj):
        return obj.stander.quald
    stander_quald.short_description = 'Qual\'d'
    stander_quald.admin_order_field = 'stander__quald'
    stander_quald.boolean = True
