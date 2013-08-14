# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from django.conf.urls import patterns, url
except ImportError:  # Django 1.3
    from django.conf.urls.defaults import patterns, url

from separated.views import CsvView

from testproject.testproject.models import Manufacturer


class ManufacturerView(CsvView):
    model = Manufacturer
    headers = [
        ('Name', 'name'),
        ('Number of models', 'car_set.count'),
    ]


urlpatterns = patterns('',
    url('^foo/$', ManufacturerView.as_view(), name='manufacturers'),
    url('^bar/$', ManufacturerView.as_view(filename='áèïôų.csv'), name='unicode_filename'),
)
