from calendar import HTMLCalendar, SUNDAY
from collections import defaultdict
from django.core.exceptions import MultipleObjectsReturned
from datetime import (
    # datetime as dtime,
    date,
    # time
)
from .models import (
    Event,
    Position,
    # Watch
)
from sailors.models import (
    Qual,
)


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, events=None):
        super(Calendar, self).__init__()
        self.year = year
        self.month = month
        self.setfirstweekday(SUNDAY)
        # print(f'Sunday: {SUNDAY}')
        self.events = events

    # formats a day as a td
    # filter events by day
    def formatday(self, day, weekday, events):
        if day == 0:
            return '<td><span class="noday">&nbsp;</span></td>'
        events_per_day = events.filter(day__day=day, active=True)
        times = defaultdict(list)
        for event in events_per_day:
            times[(event.day, event.position.start_time)].append(event)
        d = ''
        for (_d, _t), events in sorted(times.items()):
            d += f'<li>{_t.strftime("%H%M")}<ul>'
            for event in events:
                _name = f'{event.stander.rate_lname()}'
                if 'Null' in _name:
                    continue
                status = f'{("no_qual","")[any([str(event.position.qual) == "NBP 306", event.stander.quald])]} {("", "ack")[event.acknowledged]}'
                d += f'<li class="{status}">{event.position.qual}</br>'
                d += f'{_name}</li>'  # {event.stander.name.split(",")[0]}</li>'
            d += '</ul>'
        return f'<td><span class="date">{day}</span><ul> {d} </ul></td>'

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, weekday, events)
        return f'<tr>{week}</tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        events = Event.objects.filter(
            day__year=self.year,
            day__month=self.month,
        )

        cal = '<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        cal += '</table>'
        return cal


class Quickview():
    def __init__(self, year=None, month=None, events=None):
        super(Quickview, self).__init__()
        self.year = year
        self.month = month
        self.events = events
        self.quals = Qual.objects.all()
        self.positions = Position.objects.all().order_by('start_time')

    def formatmonthname(self, *args, **kwargs):
        _date = date(year=self.year, month=self.month, day=1)
        formatted = _date.strftime('%b %Y')
        return formatted

    def formatheaders(self):
        _headers = '<div>'
        headers = [u'Date', u'Time']
        for position in self.quals:
            headers.append(f'{position}')
        for header in headers:
            _headers += f'<th scope="col">{header}</th>'
        _headers += '</tr>'
        return _headers

    def formatday(self, day):
        fields = ''
        # events = self.events.filter(day=day).order_by('position__start_time')
        # oods = iter(events.filter(position__qual=1))
        # joods = iter(events.filter(position__qual=2))
        # dd = events.filter(position__qual=3)
        # nbp = events.filter(position__qual=4)
        times = ['0700', '1900', 'SUPER']
        # weekday = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat',)[int(day.strftime("%w"))]
        for i, time in enumerate(times):
            fields += time
        return fields

    def formatmonth(self):
        self.events = Event.objects.filter(
            day__year=self.year,
            day__month=self.month,
            active=True,
        ).order_by('day')
        days = self.events.dates('day', 'day')
        date = self.events.first().day
        table = '<div class="quickview">'
        table += f'<div class="month_label">{self.formatmonthname(date)}</div>'
        for day in days:
            table += f'{self.formatday(day)}\n'
        return table


class Table(
    HTMLCalendar,
):
    def __init__(self, year=None, month=None):
        super(Table, self).__init__()
        self.year = year
        self.month = month
        self.quals = Qual.objects.all()
        self.positions = Position.objects.all().order_by('start_time')

    def formatheaders(self):
        row = '<tr>\n'
        headers = [u'Date', u'Time']
        for position in self.quals:
            headers.append(f'{position}')
        for header in headers:
            row += f'\t<th scope="col">{header}</th>\n'
        row += '</tr>\n'
        return row

    def formatday(self, day):
        events = self.events.filter(day=day)
        data = ''
        times = [
            ('0700', '07'),
            ('1900', '19'),
            ('SUPER', '00'),
        ]
        weekday = (
            'Sun', 'Mon', 'Tue',
            'Wed', 'Thu', 'Fri',
            'Sat',)[int(day.strftime("%w"))]
        for i, (time_label, time) in enumerate(times):
            watches = events.filter(position__start_time__hour=time)
            style = ('class="table-secondary"', '')[day >= date.today()]
            data += f'<tr {style}>\n'
            data += f'\t<td>{(day, weekday, "",)[i]}</td>'
            data += f'<td>{times[i][0]}</td>'
            for position in self.quals:
                _watches = watches.filter(position__qual=list(self.quals).index(position) + 1)
                # warn = ('bg-warning', '')[len(_watches) > 0]
                data += f'<td {("rowspan=3", "")[i<3]} class={("bg-danger font-grey", "")[len(_watches) > 0 or str(position) in ("NBP 306", "Duty Driver")]}>'
                for watch in _watches:
                    name = f'{watch.stander.rate_lname()}'
                    status = f'{("bg-danger","")[watch.stander.quald or str(position) == "NBP 306"]} {("", "ack")[watch.acknowledged]}'
                    data += f'<span class="{status}" >{(name, "")[name[-4:]=="Null"]}</span></br>'
                data += '</td>\n'
            data += '</tr>\n'
        return data

    def formatmonth(self, withyear=True):
        self.events = Event.objects.filter(
            day__year=self.year,
            day__month=self.month,
            active=True,
        ).order_by('day')
        days = self.events.dates('day', 'day')  # set([event.day for event in events])
        cal = '<table cellpadding="0" cellspacing="0" class="table table-sm table-bordered table-striped">\n'

        cal += f'<thead class="thead-dark">{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatheaders()}</thead>\n'
        for day in days:
            cal += f'{self.formatday(day)}'
        cal += '</table>'
        # print(cal)
        return cal


# class EventCalendar(HTMLCalendar):
#     def __init__(self, events=None, year=None, month=None, *args, **kwargs):
#         super(EventCalendar, self).__init__()
#         self.setfirstweekday(SUNDAY)
#         self.year = year
#         self.month = month
#         self.events = events

#     # formats a day as a td
#     # filter events by day
#     # def formatday(self, day, events):
#     #   events_per_day = events.filter(day__day=day)
#     #     d = ''
#     #     for event in events_per_day:
#     #         d += f'<li> {event.title} </li>'
#     #         d += f'<li> {event..get_absolute_url()} </li>'

#     #     if day != 0:
#     # 		return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
#     # 	return '<td></td>'

#     def formatday(self, day, weekday, events):
#         """
#         Return a day as a table cell.
#         """
#         if day == 0:
#             return '<td class="noday">&nbsp;</td>'  # day outside month
#         # events_from_day = events.filter(day__day=day)
#         watches = events.filter(day__day=day, active=True)
#         times = defaultdict(list)
#         for event in watches:
#             times[(event.day, event.position.start_time)].append(event)
#         d = ''
#         for (_d, _t), events in sorted(times.items()):
#             d += f'<li>{_t.strftime("%H%M")}<ul>'
#             for event in events:
#                 d += f'<li>{event.get_absolute_url()}</li>'
#                 d += f'{event.stander.get_absolute_url()}</br>'
#             d += '</ul>'
#         return f'<td><span class="date">{day}</span><ul> {d} </ul></td>'

#     def formatweek(self, theweek, events):
#         """
#         Return a complete week as a table row.
#         """
#         s = ''.join(self.formatday(d, wd, events) for (d, wd) in theweek)
#         return f'<tr>{s}</tr>'

#     def formatmonth(self, theyear, themonth, withyear=True):
#         """
#         Return a formatted month as a table.
#         """
#         events = Event.objects.filter(day__month=themonth)

#         v = []
#         a = v.append
#         a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
#         a('\n')
#         a(self.formatmonthname(theyear, themonth, withyear=withyear))
#         a('\n')
#         a(self.formatweekheader())
#         a('\n')
#         for week in self.monthdays2calendar(theyear, themonth):
#             a(self.formatweek(week, events))
#             a('\n')
#         a('</table>')
#         a('\n')
#         return ''.join(v)
