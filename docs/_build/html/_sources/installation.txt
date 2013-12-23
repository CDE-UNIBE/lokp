Installation
============

This section covers the steps necessary to get the LOKP up and running.


Prerequisites
-------------

Python
^^^^^^

`Python`_ needs to be installed. LOKP is currently running under Python 2.7.x. 
You can `download Python`_ here if it is not yet installed.

.. _download Python: http://python.org/download/
.. _Python: http://python.org/

Git
^^^

The source code of LOKP is managed through `Git`_ so please make sure it is 
installed.

In case you are a developer and you'd like to contribute to the code, we 
encourage you to install and use `Git Flow`_ as well.

.. _Git: http://git-scm.com/
.. _Git Flow: https://github.com/nvie/gitflow


PostgreSQL
^^^^^^^^^^

The data entered in the LOKP is stored in a `PostgreSQL`_ database (version 9.1),
which needs to be installed along with its spatial extension `PostGIS`_.

.. _PostgreSQL: http://www.postgresql.org/
.. _PostGIS: http://postgis.net/


Installation on a UNIX system
-----------------------------

These instructions will take you through the process of installing LOKP on your 
computer, assuming that you are running a UNIX system (for example Ubuntu).

Virtual Environment
^^^^^^^^^^^^^^^^^^^

We will install LOKP in a virtual Python environment, using the `virtualenv`_ 
package.

Open a terminal and cd to the location where you want to install the project

.. rubric:: setuptools

In order to install the virtualenv package, you need to have `setuptools`_ 
installed. To see if it is installed, open a Python console in your terminal
using the following command::

    $ python

In the Python interpreter, try to import setuptools::

    >>> import setuptools

If this command results in an ``ImportError: No module named setuptools``, you 
need to install it first. Click here for instructions on how to `install 
setuptools`_.

You can quit the Python interpreter with the following command::

    >>> quit()


.. rubric:: virtualenv

If setuptools is available, you can install virtualenv with the following 
command::

    $ easy_install virtualenv

If this command fails due to permission errors, you will have to install the
virtualenv with administrative privileges::

   $ sudo easy_install virtualenv

You can then create a new virtual environment::

    $ virtualenv env
    
This will create a new folder named ``env`` which contains the virtual 
environment.

.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _install setuptools: https://pypi.python.org/pypi/setuptools


Get the code
^^^^^^^^^^^^

Use Git to get the code directly from the `LOKP Github repository`_::
    
    $ git clone https://github.com/CDE-UNIBE/lokp.git
    
This will create a folder named ``lokp`` with the code of the project.

cd into the newly created folder and nake sure that you are on the master branch
of the repository::

    $ cd lokp
    $ git checkout master

Activate the virtual environment you created earlier::

    $ source ../env/bin/activate

An activated virtual environment is indicated by adding a ``(env)`` in front of
your command line.

You can now install the dependencies of the project::

    (env) $ python setup.py develop
    
This may take a while as all of the libraries on which LOKP depends are being 
installed. If all went well, you should see a message similar to:

``Finished processing dependencies for LMKP==X.X``

.. _LOKP Github repository: https://github.com/CDE-UNIBE/lokp


Configuration
^^^^^^^^^^^^^

A lot of the LOKP can be configured in its configuration file. As this is also 
the place where you will set passwords, this file is not included in the source 
code. However, there is a sample configuration file which you can use as a 
starting point.

Copy the configuration sample file::

    $ cp development.ini.sample development.ini

You now have a configuration file called ``development.ini``, which you can open
to edit the settings as you like::

    $ vim development.ini
    
Please note that the settings for the database connection and the customization 
are explained in the next sections.


Database
^^^^^^^^

Please make sure that you have PostgreSQL and PostGIS installed. Create a new
database user and a new database, with the newly created user as owner and based
on the postgis_template. In the new database, create the schemas "data" and 
"context", both owned by the previously created user.

Adapt the database settings in the configuration file ``development.ini`` by
replacing ``username``, ``password`` and ``database``:

``sqlalchemy.url = postgresql://username:password@localhost:5432/database``

You can then use the following command to create the tables in your database
automatically::

    (env) $ populate_lmkp development.ini


Customization
^^^^^^^^^^^^^

Every instance of LOKP needs to run with a specific customization. The 
customization is indicated in the configuration file with the settings 
``lmkp.customization`` and ``lmkp.profiles_dir``.


.. rubric:: Customization

The customization files need to be situated in a directory under 
``lmkp/customization``. You can create your own customization, but it is much 
easier to start off with a preexisting customization of LOKP. 

For example, you can use the `Land Observatory`_ (LO) customization. To do this,
you need to clone the code of the LO customization (the code of which can be 
found on `Github`_) into the folder ``lmkp/customization/lo``::

    (env) $ cd lmkp/customization
    (env) $ git clone https://github.com/CDE-UNIBE/lokp_custom_lo.git lo

It does not matter if you perform these commands with an activated virtual 
environment or not.

Again, cd into the new directory and make sure that you are on the master branch
of the repository::

    (env) $ cd lo
    (env) $ git checkout master

Make sure the customization is correctly defined in the configuration file:

``lmkp.customization = lo``


.. rubric:: Profiles

Within each customization, there is the possibility to define profiles. This 
allows for example to use a different profile for the development version and
for the productive version.

The profiles directory contains the configuration of the categories, keys and
values which make up Activities and Stakeholders.

In the configuration file, you can specify which profile is to be used:

``lmkp.profiles_dir = devel``


.. rubric:: Initial data

A customization defines the attributes of an Activity and a Stakeholder and it
should also contain a script to insert these initial values into the database.

For the LO customization, there is a SQL script name which can be found at 
``lmkp/customization/lo/scripts/populate_keyvalues.sql``. Run this script as an
SQL query in your database to enter the data.


.. _Land Observatory: http://www.landobservatory.org/
.. _Github: https://github.com/CDE-UNIBE/lokp_custom_lo


JavaScript libraries
^^^^^^^^^^^^^^^^^^^^

There are some additional JavaScript libraries necessary for the LOKP to work
properly. They need to be downloaded, extracted if necessary and copied to 
``lmkp/static/lib/`` (you will have to create this folder).

For the time being, these are the following:

.. rubric:: OpenLayers

The `OpenLayers`_ library is used for the maps of the LOKP. Currently, we are
using OpenLayers 2.12, which can be downloaded `here`_.

Copy the extracted folder to: ``lmkp/static/lib/OpenLayers-2.12``.

.. _OpenLayers: http://openlayers.org/
.. _here: http://openlayers.org/download/


See it in action
^^^^^^^^^^^^^^^^

Now that everything is installed, we are ready to see it in action. 

If you are still in the customization folder, cd up to the directory where the
configuration file (``development.ini``) lies.

Let's run the application::

    (env) $ pserve development.ini

You can now open http://localhost:6543 in your browser and you should see the
LOKP in action.


Installation on a Windows system
--------------------------------

Soon to come ...


Further reading
---------------

As LOKP is built on the Pyramid framework, their `installation guide`_ may be a 
good point of reference for further information.

.. _installation guide: https://pyramid.readthedocs.org/en/latest/narr/install.html

