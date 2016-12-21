import os
from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid_mako',
    'pyramid_chameleon',
    'pyramid==1.7',
    'pyramid_handlers==0.5',
    'pyramid_mailer==0.10',
    'SQLAlchemy==0.7.6',
    'GeoAlchemy==0.7.1',
    'transaction==1.2.0',
    'pyramid_tm==0.4',
    'pyramid_debugtoolbar==3.0.4',
    'zope.sqlalchemy==0.7',
    'waitress==0.8.1',
    'papyrus==0.8.1',
    'Mako==0.8',
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
    'simplejson',
    'pyramid_beaker==0.7',
    'sphinx==1.2',
    'pytest==2.5.2',
    'selenium==2.42.1',
    'mock==1.0.1',
]

setup(name='LMKP',
      version='0.9.8b',
      description='The Myanmar land reporting',
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
          ('customization/**', 'ignore', None),
          ('static/**', 'ignore', None),
          ('scripts/**', 'ignore', None),
          ('**.py', 'lingua_python', None),
          ('**.pt', 'lingua_xml', None),
          ('**.mak', 'mako', None),
      ]},
      entry_points="""\
      [paste.app_factory]
      main = lmkp:main
      [console_scripts]
      populate_lmkp = lmkp.scripts.populate:main
      """
      )
