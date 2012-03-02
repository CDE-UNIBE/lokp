import os
from setuptools import find_packages
from setuptools import setup

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
    'WebTest',
    'Babel',
    'lingua'
    ]

setup(name='LMKP',
      version='0.0',
      description='LMKP',
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
      message_extractors={'.': [
      ('**.py', 'lingua_python', None),
      ('**.pt', 'lingua_xml', None),
      ]},
      entry_points="""\
      [paste.app_factory]
      main = lmkp:main
      [console_scripts]
      populate_LMKP = lmkp.scripts.populate:main
      """,
      )
