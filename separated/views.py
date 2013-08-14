from __future__ import unicode_literals

from operator import attrgetter
from email.header import Header

import django
from django.http import HttpResponse
from django.views.generic.list import MultipleObjectMixin, BaseListView
from django.core.exceptions import ImproperlyConfigured

try:
    import unicodecsv as csv
except ImportError:  # unicodecsv is unnecessary on Python 3
    import csv


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
                return column.replace('_', ' ') \
                    .replace('.', ' ') \
                    .capitalize()
            except AttributeError:
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
        return [self._normalize_getter(c[0])(obj)
                for c in self.get_normalized_columns(type(obj))]

    def _normalize_column(self, column):
        if not isinstance(column, (tuple, list)):
            column = (column, self.format_header(column))
        return column

    def get_normalized_columns(self, model):
        return (self._normalize_column(column)
                for column in self.get_columns(model))

    def get_columns(self, model):
        if self.columns is None:
            raise ImproperlyConfigured('Please set the columns.')
        return self.columns

    def get_filename(self, model):
        opts = model._meta
        model_name = getattr(opts, 'model_name', opts.module_name)
        return self.filename.format(
            model_name=model_name,
        )

    _getter_cache = {}

    def _normalize_getter(self, getter):
        if not getter in self._getter_cache:
            getfn = getter
            if not callable(getfn):
                getfn = attrgetter(getfn)

            def get_and_call(obj):
                ret = getfn(obj)
                if callable(ret):
                    ret = ret()
                return ret

            self._getter_cache[getter] = get_and_call
        return self._getter_cache[getter]


class CsvView(CsvResponseMixin, BaseListView):
    """
    A ListView that returns a CsvResponse.
    """
