from operator import attrgetter
from functools import partial
from io import BytesIO

import unicodecsv as csv

from django.core.exceptions import ImproperlyConfigured

try:
    from django.utils.encoding import force_text
except ImportError:  # Django < 1.4
    from django.utils.encoding import force_unicode as force_text


def get_pretty_name(accessor):
    return accessor.replace('_', ' ') \
        .replace('.', ' ') \
        .capitalize()


def Getter(accessor, normalizer=lambda x: x):
    """
    Returns a function that will access an attribute off of an object.  If that
    attribute is callable, it will call it.  Accepts a normalizer to call on
    the value at the end.
    """
    if not callable(accessor):
        short_description = get_pretty_name(accessor)
        accessor = attrgetter(accessor)
    else:
        short_description = getattr(accessor, 'short_description', None)

    def getter(obj):
        ret = accessor(obj)
        # handle things like get_absolute_url
        if callable(ret):
            ret = ret()
        return normalizer(ret)

    if short_description:
        getter.short_description = short_description

    return getter


# Should these be i18nized?
bool2string_map = {True: 'Yes', False: 'No'}

BooleanGetter = partial(Getter, normalizer=bool2string_map.get)


def DisplayGetter(accessor, *args, **kwargs):
    """
    Returns a Getter that gets the display name for a model field with choices.
    """
    short_description = get_pretty_name(accessor)
    accessor = 'get_%s_display' % accessor
    getter = Getter(accessor, *args, **kwargs)
    getter.short_description = short_description
    return getter


class ColumnSerializer(object):
    output_headers = True

    def __init__(self, columns, **kwargs):
        self.output_headers = kwargs.get('output_headers', self.output_headers)
        self.normalized_columns = list(map(self._normalize_column, columns))

    def __call__(self, queryset, file=None):
        """
        Serializes a queryset to CSV. If you pass in a file, it will write to
        that file, otherwise, it will just return a string.
        """
        if file is None:
            output = BytesIO()
            writer = csv.writer(output)
        else:
            writer = csv.writer(file)

        if self.output_headers:
            writer.writerow(self.get_header_row())

        for obj in queryset:
            writer.writerow(self.get_row(obj))

        if file is None:
            output.seek(0)
            return output.read().decode('utf-8')

    def format_header(self, column):
        if self.output_headers:
            try:
                return column.short_description
            except AttributeError:
                raise ImproperlyConfigured(
                    "If you pass a function as an accessor,"
                    " please provide a column title."
                )

    def get_header_row(self):
        return [force_text(c[1]) for c in self.normalized_columns]

    def get_row(self, obj):
        return [force_text(c[0](obj)) for c in self.normalized_columns]

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
        if getter not in self._getter_cache:
            self._getter_cache[getter] = Getter(getter)
        return self._getter_cache[getter]
