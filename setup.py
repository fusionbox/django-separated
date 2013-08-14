import os
import sys

from setuptools import setup

version = __import__('separated').get_version()

install_requires = ['Django>=1.3']
tests_require = []

if sys.version_info[0] < 3:
    install_requires.append('unicodecsv')


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(name='django-separated',
      version=version,
      author="Fusionbox, Inc.",
      author_email="programmers@fusionbox.com",
      url="https://github.com/fusionbox/django-separated",
      keywords="django csv class-based views",
      description="Class-based view and mixins for handling CSV with Django.",
      long_description=read_file('README.rst'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet :: WWW/HTTP',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
      ],
      install_requires=install_requires,
      tests_require=tests_require,
      packages=[
          'separated',
      ],

      test_suite='testproject.runtests',
)
