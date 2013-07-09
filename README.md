Land Observatory Knowledge Platform
===========

Getting Started
---------------

Switch to the Python virtual environment

    source path/to/venv/bin/activate
    
Move to the directory containg this file

    cd <directory containing this file>

Setup the project and install dependencies in the virtual environment

    (venv)user@computer:~/this/directory$ python setup.py develop
    
Copy configuration sample file and setup custom paths and database connection

    cp development.ini.sample development.ini
    vim development.ini

Populate the database

    (venv)user@computer:~/this/directory$ populate_LMKP development.ini

or

    (venv)user@computer:~/this/directory$ populate_lmkp development.ini

Start the server

    (venv)user@computer:~/this/directory$ pserve development.ini
    
Point your browser to [http://localhost:6543/](http://localhost:6543/)

Don't forget to include some profiles and enter some keys and values (for
example by using the SQL script in /scripts).
