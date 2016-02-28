# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tempfile

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from separated.views import encode_header
from separated.utils import ColumnSerializer, Getter, BooleanGetter

from testproject.testproject.models import Manufacturer
from testproject.testproject.admin import (
    OverrideExportColumnsAdmin, OverrideExportViewAdmin,
    NoColumnsExportAdmin, ExportColumnsAndExportViewAdmin,
)


def utf8(text):
    return text.encode('utf8')


class StringAccessorTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='Jeep',
        )
        self.car = self.manufacturer.car_set.create(
            name='Grand Cherokee',
        )

    def test_lambda(self):
        serializer = ColumnSerializer([lambda x: x.name], output_headers=False)
        self.assertEqual(serializer.get_row(self.car), ['Grand Cherokee'])

    def test_simple_attr(self):
        serializer = ColumnSerializer(['name'], output_headers=False)
        self.assertEqual(serializer.get_row(self.car), ['Grand Cherokee'])

    def test_dotted_path(self):
        serializer = ColumnSerializer(['manufacturer.name'])
        self.assertEqual(serializer.get_row(self.car), ['Jeep'])

    def test_callable(self):
        serializer = ColumnSerializer(['get_display_name'])
        self.assertEqual(serializer.get_row(self.car), ['GRAND CHEROKEE'])


class GetterTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='Jeep',
        )
        self.car = self.manufacturer.car_set.create(
            name='Grand Cherokee',
        )

    def test_lambda(self):
        get = Getter(lambda x: x.name)
        self.assertEqual(get(self.car), 'Grand Cherokee')

    def test_simpleattr(self):
        get = Getter('name')
        self.assertEqual(get(self.car), 'Grand Cherokee')
        self.assertEqual(get.short_description, 'Name')

    def test_dotted_path(self):
        get = Getter('manufacturer.name')
        self.assertEqual(get(self.car), 'Jeep')

    def test_callable(self):
        get = Getter('get_display_name')
        self.assertEqual(get(self.car), 'GRAND CHEROKEE')

    def test_normalizer(self):
        get = Getter('name', normalizer=lambda x: x.upper())
        self.assertEqual(get(self.car), 'GRAND CHEROKEE')

    def test_boolean_getter(self):
        get = BooleanGetter('is_admin')
        # Administrator car??
        self.car.is_admin = True
        self.assertEqual(get(self.car), 'Yes')
        self.car.is_admin = False
        self.assertEqual(get(self.car), 'No')

    def test_nested_getters(self):
        get = BooleanGetter('is_admin')
        get = Getter(get)
        self.car.is_admin = True
        self.assertEqual(get(self.car), 'Yes')
        self.assertEqual(get.short_description, 'Is admin')


class ColumnNormalizerTest(TestCase):
    def test_generate_header(self):
        def getter(obj):
            return obj.thing
        getter.short_description = 'A Getter'

        serializer = ColumnSerializer([
            'name',
            'manufacturer.name',
            'display_name',
            getter,
        ])

        self.assertEqual(serializer.get_header_row(), [
            'Name',
            'Manufacturer name',
            'Display name',
            'A Getter',
        ])

    def test_raises_exception_when_column_header_cannot_be_generated(self):
        self.assertRaises(ImproperlyConfigured, ColumnSerializer, [lambda x: x.name])

        # Doesn't raise
        ColumnSerializer([lambda x: x.name], output_headers=False)

    def test_can_be_given_headers(self):
        serializer = ColumnSerializer([
            'name',
            ('manufacturer.name', 'Manufacturer'),
            'display_name',
            ('get_absolute_url', 'Link'),
        ])

        self.assertEqual(serializer.get_header_row(), [
            'Name',
            'Manufacturer',
            'Display name',
            'Link',
        ])


class SerializerTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='My Manufacturer',
        )

    def test_serializer(self):
        serialize = ColumnSerializer([
            ('name', 'Name'),
            ('car_set.count', 'Number of models'),
        ])
        output = serialize(Manufacturer.objects.all())
        self.assertEqual(output, 'Name,Number of models\r\nMy Manufacturer,0\r\n')

    def test_serializer_unicode(self):
        serialize = ColumnSerializer([
            ('name', 'Name'),
            ('car_set.count', 'Number of models'),
        ])
        Manufacturer.objects.create(name='你好凯兰')
        output = serialize(Manufacturer.objects.all())
        self.assertEqual(output, 'Name,Number of models\r\nMy Manufacturer,0\r\n你好凯兰,0\r\n')

    def test_serializer_file(self):
        serialize = ColumnSerializer([
            ('name', 'Name'),
            ('car_set.count', 'Number of models'),
        ])
        with tempfile.TemporaryFile() as f:
            output = serialize(Manufacturer.objects.all(), file=f)
            self.assertIsNone(output)
            f.seek(0)
            self.assertEqual(f.read(), b'Name,Number of models\r\nMy Manufacturer,0\r\n')


class CsvViewTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='你好凯兰',
        )

    def test_unicode_csv_output(self):
        # In Python 2, the built-in csv library doesn't handle unicode.
        response = self.client.get(reverse('manufacturers'))
        expected = utf8("Name,Number of models\r\n你好凯兰,0\r\n")
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


class CsvExportAdminTest(TestCase):
    def setUp(self):
        Manufacturer.objects.create(
            name='Manufacturer A',
        )
        Manufacturer.objects.create(
            name='Manufacturer B',
        )
        self.factory = RequestFactory()

    def test_csv_export_columns(self):
        admin = OverrideExportColumnsAdmin(Manufacturer, 'testproject')
        # actions are only ever POSTed to.
        request = self.factory.post('/')
        queryset = Manufacturer.objects.all()
        response = admin.export_csv_action(request, queryset)
        self.assertEqual(response.status_code, 200)
        expected = utf8("Name,Number of models\r\nManufacturer A,0\r\nManufacturer B,0\r\n")
        self.assertEqual(response.content, expected)

    def test_csv_export_view_class(self):
        admin = OverrideExportViewAdmin(Manufacturer, 'testproject')
        request = self.factory.post('/')
        queryset = Manufacturer.objects.all()
        response = admin.export_csv_action(request, queryset)
        expected = utf8("0,Manufacturer A\r\n0,Manufacturer B\r\n")
        self.assertEqual(response.content, expected)

    def test_csv_export_columns_overrides_views_columns(self):
        admin = ExportColumnsAndExportViewAdmin(Manufacturer, 'testproject')
        request = self.factory.post('/')
        queryset = Manufacturer.objects.all()
        response = admin.export_csv_action(request, queryset)
        expected = utf8("Manufacturer A,0\r\nManufacturer B,0\r\n")
        self.assertEqual(response.content, expected)

    def test_no_columns_view_admin_errors_meaningfully(self):
        admin = NoColumnsExportAdmin(Manufacturer, 'testproject')
        request = self.factory.post('/')
        queryset = Manufacturer.objects.all()
        with self.assertRaises(ImproperlyConfigured):
            admin.export_csv_action(request, queryset)
