from __future__ import unicode_literals

from email.header import Header

import django
from django.http import HttpResponse
from django.views.generic.list import MultipleObjectMixin, BaseListView
from django.core.exceptions import ImproperlyConfigured

try:
    import unicodecsv as csv
except ImportError:  # unicodecsv is unnecessary on Python 3
    import csv

from separated.utils import Getter


def encode_header(value):
    return Header(value, 'utf-8').encode()


class CsvResponse(HttpResponse):
    def __init__(self, filename, content_type='text/csv', **kwargs):
        super(CsvResponse, self).__init__(content_type=content_type, **kwargs)
        disposition = 'attachment; filename="{0}"'.format(filename)
        # BBB: Django 1.4 and earlier didn't support non-ASCII headers.  Later
        # versions do this for us.
        if django.VERSION < (1, 5):
            disposition = encode_header(disposition)
        self['Content-Disposition'] = disposition


class CsvResponseMixin(MultipleObjectMixin):
    """
    A ListView mixin that returns a CsvResponse.
    """
    response_class = CsvResponse
    columns = None
    output_headers = True
    filename = '{model_name}_list.csv'

    def render_to_response(self, context, **kwargs):
        queryset = context['object_list']
        model = queryset.model
        response = self.response_class(
            filename=self.get_filename(model),
        )

        writer = csv.writer(response)

        if self.output_headers:
            writer.writerow(self.get_header_row(model))

        for obj in queryset:
            writer.writerow(self.get_row(obj))

        return response

    def format_header(self, column):
        if self.output_headers:
            try:
                return column.short_description
            except AttributeError:
                raise ImproperlyConfigured(
                    "If you pass a function as an accessor,"
                    " please provide a column title."
                )

    def get_header_row(self, model):
        return [c[1] for c in self.get_normalized_columns(model)]

    def get_row(self, obj):
        return [c[0](obj)
                for c in self.get_normalized_columns(type(obj))]

    def get_normalized_columns(self, model):
        return map(self._normalize_column, self.get_columns(model))

    def get_columns(self, model):
        if self.columns is None:
            raise ImproperlyConfigured('Please set the columns.')
        return self.columns

    def get_filename(self, model):
        opts = model._meta
        try:
            model_name = opts.model_name
        except AttributeError:
            # for Django < 1.6. Deprecated in 1.6 & removed in 1.8.
            model_name = opts.module_name
        return self.filename.format(
            model_name=model_name,
        )

    def _normalize_column(self, column):
        # column can either be a 2-tuple of (accessor, header), or just an
        # accessor.  accessor will be passed to Getter, and we will get the
        # header off of the Getter. Returns a 2-tuple of (Getter, header).
        if isinstance(column, (tuple, list)):
            column = self._normalize_getter(column[0]), column[1]
        else:
            column = self._normalize_getter(column)
            column = (column, self.format_header(column))
        return column

    _getter_cache = {}

    def _normalize_getter(self, getter):
        if not getter in self._getter_cache:
            self._getter_cache[getter] = Getter(getter)
        return self._getter_cache[getter]


class CsvView(CsvResponseMixin, BaseListView):
    """
    A ListView that returns a CsvResponse.
    """
