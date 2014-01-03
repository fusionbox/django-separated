from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from separated.views import CsvView


class CsvExportAdminMixin(object):
    """
    Adds an Export to CSV action for ModelAdmins.  You can specify which
    columns to display in the CSV with the csv_export_columns attribute.
    csv_export_columns corresponds to CsvView.columns.  For more control, you
    can override csv_export_view_class to get all of the flexibility that
    CsvView provides.
    """
    csv_export_columns = None
    csv_export_view_class = CsvView

    def get_csv_export_columns(self, request):
        return self.csv_export_columns

    def get_csv_export_view_class(self, request):
        return self.csv_export_view_class

    def export_csv_action(self, request, queryset):
        initkwargs = {
            'queryset': queryset,
        }

        columns = self.get_csv_export_columns(request)
        # maybe they already set the columns on the view.
        if columns is not None:
            initkwargs['columns'] = columns

        csv_view_class = self.get_csv_export_view_class(request)
        viewfn = csv_view_class.as_view(**initkwargs)
        # The base CsvView does not respond to POST requests, actions are only
        # ever POST requests.
        request.method = 'GET'
        return viewfn(request)
    export_csv_action.short_description = _("Export to CSV")


class CsvExportModelAdmin(CsvExportAdminMixin, admin.ModelAdmin):
    actions = ['export_csv_action']
