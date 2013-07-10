import os
from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid==1.3',
    'pyramid_handlers==0.5',
    'pyramid_mailer==0.10',
    'SQLAlchemy==0.7.6',
    'GeoAlchemy==0.7.1',
    'transaction==1.2.0',
    'pyramid_tm==0.4',
    'pyramid_debugtoolbar==1.0.2',
    'zope.sqlalchemy==0.7',
    'waitress==0.8.1',
    'papyrus==0.8.1',
    'Mako==0.6',
    'WebTest==1.3.4',
    'cryptacular',
    'Babel==0.9.6',
    'lingua==1.3',
    'PasteScript==1.7.5',
    'psycopg2==2.4.5',
    'PyYAML==3.10',
    'Chameleon==2.8.5',
    'recaptcha-client==1.0.6',
    'requests==1.1.0',
    'deform==0.9.7',
    'pyramid_beaker==0.7'
    ]

setup(name='LMKP',
      version='0.51',
      description='The Land Matrix Knowledge Platform',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
      "Programming Language :: Python",
      "Framework :: Pylons",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Centre for Development and Environment, University of Bern',
      author_email='',
      url='http://www.cde.unibe.ch',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='lmkp',
      install_requires=requires,
      message_extractors={'lmkp': [
      ('**.py', 'lingua_python', None),
      ('**.pt', 'lingua_xml', None),
      ('**.mak', 'mako', None),
      ('lmkp/static/**', 'ignore', None)
      ]},
      entry_points="""\
      [paste.app_factory]
      main = lmkp:main
      [console_scripts]
      populate_lmkp = lmkp.scripts.populate:main
      """
      )