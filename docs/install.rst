Install
=======

This section covers the steps necessary to get the LOKP up and running.

Getting Started
---------------

Activate the Python virtual environment::

    source path/to/virtualenv/bin/activate

Move to the directory of the LOKP project::

    cd <project directory>

Setup the project and install dependencies in the virtual environment::

    (env)user@computer:~/path/to/project$ python setup.py develop
    
Copy configuration sample file and set custom paths and database connection::

    cp development.ini.sample development.ini
    vim development.ini

Populate the database::

    (env)user@computer:~/path/to/project$ populate_LMKP development.ini
    
or::

    (env)user@computer:~/path/to/project$ populate_lmkp development.ini

Start the server::

    (env)user@computer:~/path/to/project$ pserve development.ini

Point your browser to http://localhost:6543/ and you should see the LOKP 
running.

Don't forget to include some profiles and enter some keys and values (for 
example by using the SQL script in /scripts).
