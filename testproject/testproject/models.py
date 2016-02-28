from django.db import models


try:
    from django.utils.encoding import python_2_unicode_compatible
except ImportError:  # Django < 1.5
    python_2_unicode_compatible = None


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

if python_2_unicode_compatible:
    Manufacturer = python_2_unicode_compatible(Manufacturer)
else:
    Manufacturer.__unicode__ = Manufacturer.__str__
    del Manufacturer.__str__


class Car(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    name = models.CharField(max_length=255)

    def get_display_name(self):
        return self.name.upper()
