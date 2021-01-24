import csv
from operator import attrgetter
from django.http import HttpResponse

DEEP_SEPARATOR = '__'


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        if hasattr(self, 'csv_fields'):
            field_names = [x.replace(DEEP_SEPARATOR, '.') for x in self.csv_fields]
        else:
            field_names = self.list_display

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([attrgetter(field)(obj) for field in field_names])

        return response

    export_as_csv.short_description = 'Export selected as csv'
