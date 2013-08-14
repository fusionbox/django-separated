from operator import attrgetter
from functools import partial

from django.utils.translation import ugettext_lazy as _


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
        if callable(ret):
            ret = ret()
        return normalizer(ret)

    if short_description:
        getter.short_description = short_description

    return getter


bool2string_map = {True: _('Yes'), False: _('No')}

BooleanGetter = partial(Getter, normalizer=bool2string_map.get)
