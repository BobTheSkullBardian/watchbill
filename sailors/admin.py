from django.contrib import admin
from .models import Sailor
from events.models import Event
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
import csv


class WatchInline(admin.StackedInline):
    model = Event


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


class ExportMixin:
    def export(self, request, queryset):
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
    export.short_description = "Export Selected"


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


@admin.register(Sailor)
class SailorAdmin(admin.ModelAdmin, ExportMixin):  # , RelatedObjectLinkMixin,):
    actions = ('export',)

    inlines = (WatchInline,)

    list_display = (
        'name',
        'rate',
        'phone',
        'quals',
        # 'quald',
        'report',
        'qualdate',
        'availability',
        'notes',
        'get_watches',
        'dinq_date',
    )

    list_display_links = list_display

    list_filter = (
        # 'active',
        'qual',
        'quald',
        # 'in_teams',
        ActiveFilter,
    )

    fields = (
        (
            'name',
            'rate',
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
        'quald',
        (
            'qualdate',
            'report',
        ),
        'active',
    )


# @admin.register(Qual)
# class QualAdmin(admin.ModelAdmin):
#     pass
