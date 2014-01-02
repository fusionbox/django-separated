django-separated
================

.. image:: https://api.travis-ci.org/fusionbox/django-separated.png
   :alt: Building Status
   :target: https://travis-ci.org/fusionbox/django-separated

Class-based view and mixins for responding with CSV in Django.  django-separated
supports Django 1.3+.


Installation
------------

::

    $ pip install django-separated


Documentation
-------------

Views
`````

separated.views.CsvView
~~~~~~~~~~~~~~~~~~~~~~~

A ListView that returns a ``CsvResponse``.

You can specify the data for each row using the ``columns`` attribute.
``columns`` should be an iterable of 2-tuples where the first index is
an accessor to get the value off of an object and the second is a column
header. ::

    class UserCsvView(CsvView):
        model = User
        columns = [
            ('first_name', 'First name'),
            ('last_name', 'Last name'),
            ('email', 'Email'),
        ]

The accessor can be a string or a callable.  If it isn't a callable, it
will be passed into attrgetter to turn into a callable.  If the accessor
returns a callable, it will be called.  All of the following are valid
examples of accessors:

-  ``first_name``
-  ``first_name.upper``
-  ``get_absolute_url``
-  ``lambda x: x.upvotes.count() - x.downvotes.count()``

There is a corresponding ``get_columns`` method if you need to have
more dynamic behavior.

The header index is optional, if you want a header to be generated from the
accessor, you can write a simpler ``columns`` declaration::

    class UserCsvView(CsvView):
        model = User
        columns = [
            'first_name',
            'last_name',
            'email',
        ]

Additionally, you can specify the filename of the CSV file that will be
downloaded.  It will default to the model name + ``_list.csv`` if you don't
provide one. For example::

    class UserCsvView(CsvView):
        model = User

will have a filename of ``user_list.csv``.  But you can override it by
settings the ``filename`` attribute.  There is a corresponding
``get_filename`` that you can override for more complicated behavior.

By default, ``CsvView`` will output the headers as the first line.  If you
want to suppress this behavior, set ``output_headers`` to ``False``.

separated.views.CsvResponseMixin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A MultipleObjectMixin subclass that returns a ``CsvResponse``.

This is useful in instances where you want to substitute BaseListView for a
ListView of your own.  ``CsvResponseMixin`` supports all the behavior
mentioned in ``CsvView``, the only machinery you need to hook it up is a
View class that calls ``render_to_response`` with a context that has a
queryset available in the ``object_list`` key. ::

    class MyWeirdBaseListView(View):
        def get(self, request, *args, **kwargs):
            return self.render_to_response({
                'object_list': User.objects.all(),
            })

    class MyWeirdCsvView(CsvResponseMixin, MyWeirdBaseListView):
        pass

separated.views.CsvResponse
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A subclass of HttpResponse that will download as CSV.  ``CsvResponse``
requires a ``filename`` as the first argument of the constructor.


Admin
`````

You can use django-separated in the admin center to export CSV from the admin
site. ::

    from separated.admin import CsvExportModelAdmin

    class NewsAdmin(CsvExportModelAdmin):
        csv_export_columns = [
            'title',
            'pub_date',
            'author.full_name',
        ]

This adds an action to the change list.

``csv_export_columns`` corresponds to the ``CsvView.columns`` attribute.  If
you want more fine-grained control, you can override ``csv_export_view_class``
instead::

    from datetime import datetime

    from separated.admin import CsvExportModelAdmin
    from separated.views import CsvView

    class NewsCsvView(CsvView):
        columns = [
            'title',
            'pub_date',
            'author.full_name',
        ]
        output_headers = False

        def get_filename(self, model):
            return '%s-news-export.csv' % datetime.today().strftime('Y-m-d')

    class NewsAdmin(CsvExportModelAdmin):
        csv_export_view_class = NewsCsvView

``csv_export_columns`` and ``csv_export_view_class`` also exist as methods
(``get_csv_export_columns`` and ``get_csv_export_view_class`` respectively) if
you need change them based on request. ::


    from separated.admin import CsvExportModelAdmin

    class NewsAdmin(CsvExportModelAdmin):
        staff_export_columns = (
            'title',
            'pub_date',
            'author.full_name',
        )

        superuser_export_columns = staff_export_columns + (
            'secret_column',
        )

        def get_csv_export_columns(self, request):
            if request.user.is_superuser:
                return self.superuser_export_columns
            else:
                return self.staff_export_columns


Getters
```````
django-separated provides a couple of helpers for normalizing the data that
comes off of the model before sending it to the CSV writer.  These are all
based on a ``Getter`` class which handles the different types of accessors.


separated.utils.BooleanGetter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a boolean value that you wish to be transformed into ``Yes`` or
``No``, you can use the ``BooleanGetter``::

    from separated.utils import BooleanGetter

    class UserCsvView(CsvView):
        model = User
        columns = [
            BooleanGetter('is_admin'),
        ]

separated.utils.DisplayGetter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a model field that has choices and you want the human readable
display to appear in the CSV, you can use the ``DisplayGetter``::

    from separated.utils import BooleanGetter

    class User(models.Model):
        favorite_color = models.CharField(max_length=255,
            choices=(
                ('blue', 'Blue'),
                ('green', 'Green'),
                ('red', 'Red'),
            ))

    class UserCsvView(CsvView):
        model = User
        columns = [
            DisplayGetter('favorite_color'),
        ]

This will end up using the ``get_favorite_color_display`` method that Django
automatically adds.
