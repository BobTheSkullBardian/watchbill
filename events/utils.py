from calendar import HTMLCalendar, SUNDAY
from collections import defaultdict
# from datetime import (
#     datetime as dtime,
#     date,
#     time
# )
from .models import (
    Event,
    # Watch
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
            red = "style='color:red;'"
            for event in events:
                status = f'{(red,"")[event.stander.quald]}'
                # d += f'{("","<b>")[event.acknowledged]}'
                d += f'<li {status}>{event.position}</br>'
                d += f'{event.stander.rate} {event.stander.name.split(",")[0]}</li>'
                # d += f'{("","</b>")[event.acknowledged]}'
                if event.acknowledged: d = f'<b>{d}</b>'
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

        cal = '<table border="0" cellpadding="0" cellspac ng="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        cal += '</table>'
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
