import os

from setuptools import setup


install_requires = ['Django>=1.3', 'unicodecsv']
tests_require = []


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(name='django-separated',
      version='1.0.2',
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
