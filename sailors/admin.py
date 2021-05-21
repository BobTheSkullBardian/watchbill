from datetime import date, timedelta
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from django.db.models import Count  # , Q
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from .models import Sailor, Qual
from events.models import Event
import csv

admin.site.unregister(Group)


# @admin.register(Qual)
# class QualAdmin(admin.ModelAdmin):
#     pass


class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'action_time',
        'object_repr',
        'user',
        'content_type',
        # 'object_id',
        'action_flag',
        'change_message',
    )

    list_filter = (
        'user',
        'content_type',
        'action_flag',
    )

    readonly_fields = (
        'object_repr',
        'content_type',
        'user',
        'action_time',
        # 'object_id',
        'action_flag',
        'change_message',
    )

    fields = (
        (
            'object_repr',
            'content_type',
        ),
        'user',
        'action_time',
        # 'object_id',
        'action_flag',
        'change_message',
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        # del actions['delete_selected']
        return actions


admin.site.register(LogEntry, LogEntryAdmin)


class WatchInline(admin.StackedInline):
    model = Event
    ordering = (
        "-day",
        'active',
    )

class DefaultListFilter(SimpleListFilter):
    all_value = '_all'

    def default_value(self):
        raise NotImplementedError()

    def queryset(self, request, queryset):
        if self.parameter_name in request.GET and request.GET[self.parameter_name] == self.all_value:
            return queryset

        if self.parameter_name in request.GET:
            return queryset.filter(**{self.parameter_name: request.GET[self.parameter_name]})

        return queryset.filter(**{self.parameter_name: self.default_value()})

    def choices(self, cl):
        yield {
            'selected': self.value() == self.all_value,
            'query_string': cl.get_query_string({self.parameter_name: self.all_value}, []),
            'display': _('All'),
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup) or (self.value() is None and force_text(self.default_value()) == force_text(lookup)),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class ActiveFilter(DefaultListFilter):
    title = _('Active ')
    parameter_name = 'active__exact'

    def lookups(self, request, model_admin):
        return (
            (0, 'No'),
            (1, 'Yes'),
        )

    def default_value(self):
        return 1


class Qual_count(SimpleListFilter):
    title = 'Watch Qualification'
    parameter_name = 'qual'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        for i, qual in enumerate(list(Qual.objects.all())):
            count = qs.filter(qual=qual).count()
            if count:
                yield (i + 1, f'{qual} ({count})')

    def queryset(self, request, queryset):
        # Apply the filter selected, if any
        qual = self.value()
        if qual:
            return queryset.filter(qual=qual)


class Quald_count(SimpleListFilter):
    title = _('Qualified')
    parameter_name = 'quald'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)  # .filter(**request.GET.dict())
        for pk, count in qs.values_list('quald').annotate(total=Count('quald')).order_by('-total'):
            if count:
                yield pk, f'{("No", "Yes")[pk]} ({count})'

    def queryset(self, request, queryset):
        quald = self.value()
        if quald:
            return queryset.filter(quald=quald)


def export_selected_sailors(self, request, queryset):
    filename = 'WB_Roster'
    meta = self.model._meta
    field_names = [field.name for field in meta.get_fields()]
    field_names.pop(field_names.index('id'))
    field_names.pop(field_names.index('event'))
    field_names.pop(field_names.index('qual'))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={filename}.csv'.format(meta)
    writer = csv.writer(response)
    header_row = [name.capitalize() for name in field_names]
    qualdate_index = header_row.index("Qualdate")
    header_row.insert(qualdate_index + 1, "Quals")
    header_row.insert(qualdate_index + 2, "Dinq")
    header_row.insert(len(header_row), "Watches")
    writer.writerow(header_row)
    for obj in queryset:
        row = [getattr(obj, field) for field in field_names]
        row.insert(header_row.index("Quals"), ", ".join(obj.quals()))
        row.insert(header_row.index("Watches"), ", ".join(obj.get_watches()))
        row.insert(header_row.index("Dinq"), obj.dinq_date())
        writer.writerow(row)
    return response


@admin.register(Sailor)
class SailorAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _watch_count=Count(
                "event",
            ),
        )
        return queryset

    def get_watches(self, obj):
        today = date.today()
        delta = timedelta(days=100)
        start = today - delta
        events = obj.event_set.filter(
            day__gte=start,
            active=True,
            # ).exclude(
            #     position__label="Super",
        ).order_by(
            '-day',
        )
        watches = [
            f'{watch.day.strftime("%d%b")} {watch.position}' for watch in events
        ]
        return watches  # [f'{watch.day.strftime("%d%b")} {watch.position}' for watch in obj.event_set.filter(active=True).order_by('day')]#[-3:]
    get_watches.short_description = "Watch History"
    get_watches.allow_tags = True

    def watch_count(self, obj):
        today = date.today()
        delta = timedelta(days=100)
        start = today - delta
        watches = obj.event_set.filter(
            day__gte=start,
            active=True,
        ).exclude(
            position__label="Super",
        )
        count = watches.count()
        return count
    # watch_count.short_description = "Watch Count"
    watch_count.admin_order_field = '_watch_count'

    actions = (
        export_selected_sailors,
        # ack,
    )

    inlines = (WatchInline,)

    list_display = (
        'name',
        'rate',
        'phone',
        'quals',
        # 'quald',
        # 'report',
        'qualdate',
        'availability',
        'notes',
        'get_watches',
        'watch_count',
        # 'dept',
        # 'div',
        'dept_div',
        'dinq_date',
        # 'off_wb_date',
    )

    list_display_links = list_display

    list_filter = (
        # 'active',
        # 'qual',
        Qual_count,
        # Quald_count,
        'quald',
        ActiveFilter,
        'dept',
        'in_teams',
        # 'coversheet',
    )

    fields = (
        (
            'name',
            'rate',
            'dept',
            'div',
        ),
        (
            'phone',
            'work_email',
        ),
        (
            'email',
            'in_teams',
        ),
        (
            'availability',
            'notes',
        ),
        'qual',
        (
            'quald',
            'coversheet',
        ),
        (
            'qualdate',
            'report',
        ),
        'active',
    )
