# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from separated.views import CsvView

from django.urls import re_path

from .models import Manufacturer


class ManufacturerView(CsvView):
    model = Manufacturer
    columns = [
        ('name', 'Name'),
        ('car_set.count', 'Number of models'),
    ]


urlpatterns = [
    re_path('^foo/$', ManufacturerView.as_view(), name='manufacturers'),
    re_path('^bar/$', ManufacturerView.as_view(filename='áèïôų.csv'), name='unicode_filename'),
]
