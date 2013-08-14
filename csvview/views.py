from __future__ import unicode_literals

from operator import attrgetter
from email.header import Header

from django.http import HttpResponse
from django.views.generic.list import MultipleObjectMixin, BaseListView
from django.core.exceptions import ImproperlyConfigured

try:
    import unicodecsv as csv
except ImportError:  # unicodecsv is unnecessary on Python 3
    import csv


def encode_header(value):
    """
    BBB: Django 1.3 doesn't support non ASCII Headers.  Later versions do this
    for us.
    """
    return Header(value, 'utf-8').encode()


class CsvResponse(HttpResponse):
    def __init__(self, filename, content_type='text/csv', **kwargs):
        super(CsvResponse, self).__init__(content_type=content_type, **kwargs)
        disposition = 'attachment; filename="{0}"'.format(filename)
        self['Content-Disposition'] = encode_header(disposition)


class CsvResponseMixin(MultipleObjectMixin):
    """
    A ListView mixin that returns a CsvResponse.
    """
    response_class = CsvResponse
    headers = None
    output_headers = True
    filename = '{model_name}_list.csv'

    def render_to_response(self, context, **kwargs):
        queryset = context['object_list']
        response = self.response_class(
            filename=self.get_filename(queryset),
        )

        writer = csv.writer(response)

        if self.output_headers:
            writer.writerow(self.get_header_row())

        for obj in queryset:
            writer.writerow(self.get_row(obj))

        return response

    def get_header_row(self):
        return [h[0] for h in self.get_headers()]

    def get_row(self, obj):
        return [self._normalize_getter(h[1])(obj)
                for h in self.get_headers()]

    def get_headers(self):
        if self.headers is None:
            raise ImproperlyConfigured('Please set the headers.')
        return self.headers

    def get_filename(self, queryset):
        opts = queryset.model._meta
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
