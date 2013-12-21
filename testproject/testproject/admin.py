from separated.admin import CsvExportModelAdmin
from separated.views import CsvView


class OverrideExportColumnsAdmin(CsvExportModelAdmin):
    csv_export_columns = [
        ('name', 'Name'),
        ('car_set.count', 'Number of models'),
    ]


class ExportCsvView(CsvView):
    output_headers = False
    columns = [
        'car_set.count',
        'name',
    ]


class OverrideExportViewAdmin(CsvExportModelAdmin):
    csv_export_view_class = ExportCsvView


class ExportColumnsAndExportViewAdmin(OverrideExportColumnsAdmin, OverrideExportViewAdmin):
    pass


class NoColumnsExportAdmin(CsvExportModelAdmin):
    "This one is invalid on purpose"
