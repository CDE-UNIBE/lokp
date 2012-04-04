import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'papyrus',
    'Mako>=0.6',
    'WebTest',
    'cryptacular',
    'Babel',
    'lingua',
    'psycopg2',
    'pyyaml',
    'chameleon>=2.8',
    'lxml==2.3',
    'pykml'
    ]

setup(name='LandMatrixKnowledgePlatform',
      version='0.1',
      description='The Land Matrix Knowledge Platform',
      long_description=README + '\n\n' +  CHANGES,
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
      message_extractors={'.': [
      ('**.py', 'lingua_python', None),
      ('**.pt', 'lingua_xml', None),
      ('**.mak', 'mako', None),
      ]},
      entry_points="""\
      [paste.app_factory]
      main = lmkp:main
      [console_scripts]
      populate_LMKP = lmkp.scripts.populate:main
      """,
      )