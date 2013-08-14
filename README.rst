django-csvview
==============

.. image:: https://api.travis-ci.org/fusionbox/django-csvview.png
   :alt: Building Status
   :target: https://travis-ci.org/fusionbox/django-csvview

Class-based view and mixins for responding with CSV in Django.  django-csvview
supports Django 1.3+.


Installation
------------

::

    $ pip install django-csvview


Documentation
-------------

csvview.views.CsvView
~~~~~~~~~~~~~~~~~~~~~

A ListView that returns a ``CsvResponse``.

You can specify the data for each row using the ``headers`` attribute.
``headers`` should be an iterable of 2-tuples where the first index is
the CSV header and the second is an accessor to get the value off of an
object. ::

    class UserCsvView(CsvView):
        model = User
        headers = [
            ('First Name', 'first_name'),
            ('Last Name', 'last_name'),
            ('Email', 'email'),
        ]

The accessor can be a string or a callable.  If it isn't a callable, it
will be passed into attrgetter to turn into a callable.  If the accessor
returns a callable, it will be called.  All of the following are valid
examples of accessors:

-  ``first_name``
-  ``first_name.upper``
-  ``get_absolute_url``
-  ``lambda x: x.upvotes.count() - x.downvotes.count()``

There is a corresponding ``get_headers`` method if you need to have
more dynamic behavior.

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

csvview.views.CsvResponseMixin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

csvview.views.CsvResponse
~~~~~~~~~~~~~~~~~~~~~~~~~

A subclass of HttpResponse that will download as CSV.  ``CsvResponse``
requires a ``filename`` as the first argument of the constructor.
