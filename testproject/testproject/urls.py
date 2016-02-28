# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from separated.views import CsvView

from .models import Manufacturer


try:
    from django.conf.urls import url
except ImportError:  # Django 1.3
    from django.conf.urls.defaults import url


class ManufacturerView(CsvView):
    model = Manufacturer
    columns = [
        ('name', 'Name'),
        ('car_set.count', 'Number of models'),
    ]


urlpatterns = [
    url('^foo/$', ManufacturerView.as_view(), name='manufacturers'),
    url('^bar/$', ManufacturerView.as_view(filename='áèïôų.csv'), name='unicode_filename'),
]
