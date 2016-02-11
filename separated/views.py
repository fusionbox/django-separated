from __future__ import unicode_literals

from email.header import Header

import django
from django.http import HttpResponse
from django.views.generic.list import MultipleObjectMixin, BaseListView
from django.core.exceptions import ImproperlyConfigured

from separated.utils import ColumnSerializer


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
    column_serializer_class = ColumnSerializer
    columns = None
    output_headers = True
    filename = '{model_name}_list.csv'

    def render_to_response(self, context, **kwargs):
        queryset = context['object_list']
        model = queryset.model
        response = self.response_class(
            filename=self.get_filename(model),
        )
        serialize = self.get_column_serializer(model)
        serialize(queryset, file=response)
        return response

    def get_column_serializer_class(self, model):
        return self.column_serializer_class

    def get_column_serializer(self, model):
        return self.get_column_serializer_class(model)(
            self.get_columns(model),
            output_headers=self.output_headers,
        )

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


class CsvView(CsvResponseMixin, BaseListView):
    """
    A ListView that returns a CsvResponse.
    """
