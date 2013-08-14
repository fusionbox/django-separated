# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from separated.views import CsvView, encode_header

from testproject.testproject.models import Car, Manufacturer


class AttrGetterTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='Jeep',
        )
        self.car = self.manufacturer.car_set.create(
            name='Grand Cherokee',
        )

    def test_lambda(self):
        class View(CsvView):
            model = Car
            columns = [lambda x: x.name]
            output_headers = False

        self.assertEqual(View().get_row(self.car), ['Grand Cherokee'])

    def test_simple_attr(self):
        class View(CsvView):
            model = Car
            columns = ['name']

        self.assertEqual(View().get_row(self.car), ['Grand Cherokee'])

    def test_dotted_path(self):
        class View(CsvView):
            model = Car
            columns = ['manufacturer.name']

        self.assertEqual(View().get_row(self.car), ['Jeep'])

    def test_callable(self):
        class View(CsvView):
            model = Car
            columns = ['get_display_name']

        self.assertEqual(View().get_row(self.car), ['GRAND CHEROKEE'])


class ColumnNormalizerTest(TestCase):
    def test_generate_header(self):
        def getter(obj):
            return obj.thing
        getter.short_description = 'A Getter'

        class View(CsvView):
            columns = ['name', 'manufacturer.name', 'display_name', getter]

        self.assertEqual(View().get_header_row(Manufacturer), [
            'Name',
            'Manufacturer name',
            'Display name',
            'A Getter',
        ])

    def test_raises_exception_when_column_header_cannot_be_generated(self):
        class View(CsvView):
            columns = [lambda x: x.name]

        self.assertRaises(ImproperlyConfigured, View().get_header_row, Manufacturer)

        class SuppressView(View):
            output_headers = False

        # Doesn't raise
        SuppressView().get_header_row(Manufacturer)

    def test_can_supply_headers(self):
        class View(CsvView):
            columns = [
                'name',
                ('manufacturer.name', 'Thing'),
                'display_name',
                ('get_absolute_url', 'Description'),
            ]

        self.assertEqual(View().get_header_row(Manufacturer), [
            'Name',
            'Thing',
            'Display name',
            'Description',
        ])


class CsvViewTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='你好凯兰',
        )

    def test_unicode_csv_output(self):
        # In Python 2, the built-in csv library doesn't handle unicode.
        response = self.client.get(reverse('manufacturers'))
        expected = "Name,Number of models\r\n你好凯兰,0\r\n".encode('utf8')
        self.assertEqual(response.content, expected)

    def test_content_type(self):
        response = self.client.get(reverse('manufacturers'))
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_filename_autogenerated(self):
        response = self.client.get(reverse('manufacturers'))
        expected = 'attachment; filename="manufacturer_list.csv"'
        self.assertEqual(response['Content-Disposition'], expected)

    def test_unicode_filename(self):
        response = self.client.get(reverse('unicode_filename'))
        # It is kinda weird to have Unicode in the headers.  Copied the encoder
        # from Django.
        expected = encode_header('attachment; filename="áèïôų.csv"')
        self.assertEqual(response['Content-Disposition'], expected)