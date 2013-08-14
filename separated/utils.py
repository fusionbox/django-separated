from operator import attrgetter
from functools import partial


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
