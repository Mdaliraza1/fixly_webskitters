import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

def export_as_csv_action(description="Export selected objects as CSV file", fields=None):
    """
    This function returns an export csv action.
    """
    def export_as_csv(modeladmin, request, queryset):
        # Get model fields if not specified
        if not fields:
            field_names = [field.name for field in modeladmin.model._meta.fields]
        else:
            field_names = fields

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=export.csv'
        writer = csv.writer(response)

        # Write header row
        writer.writerow(field_names)

        # Write data rows
        for obj in queryset:
            row = []
            for field in field_names:
                # Handle nested attributes using get_FOO_display() for choices
                if hasattr(obj, f'get_{field}_display'):
                    value = getattr(obj, f'get_{field}_display')()
                else:
                    value = getattr(obj, field)
                row.append(smart_str(value))
            writer.writerow(row)

        return response

    export_as_csv.short_description = description
    return export_as_csv
