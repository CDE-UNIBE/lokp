import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'babel==2.5.3',
    'cryptacular==1.4.1',
    'deform==2.0.4',
    'geoalchemy2==0.4.2',
    'geojson==2.3.0',
    'lingua==4.13',
    'plaster_pastedeploy==0.4.2',
    'psycopg2==2.7.3.2',
    'pyramid==1.9.1',
    'pyramid_beaker==0.8',
    'pyramid_debugtoolbar==4.3',
    'pyramid_mailer==0.15.1',
    'pyramid_mako==1.0.2',
    'pyramid_tm==2.2',
    'PyShp==1.2.12',
    'pyyaml==3.12',
    'shapely==1.6.3',
    'sqlalchemy==1.2.1',
    'transaction==2.1.2',
    'waitress==1.1.0',
    'zope.sqlalchemy==0.7.7',
    'fabric3==1.14.post1',
]

tests_require = [
    'pytest==3.3.2',
    'pytest-cov==2.5.1',
    'PyVirtualDisplay==0.2.1',
    'requests==2.18.4',
    'selenium==3.8.1',
    'WebTest==2.0.29',
]

deploy_require = [
    'pyramid_crow==0.4.2',
]

setup(
    name='lokp',
    version='1.0',
    description='The Land Observatory',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Centre for Development and Environment, University of Bern',
    author_email='',
    url='https://github.com/CDE-UNIBE/lokp',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
        'deploy': deploy_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = lokp:main',
        ],
        'console_scripts': [
            'initialize_lokp_db = lokp.scripts.initialize_db:main'
        ]
    },
)
