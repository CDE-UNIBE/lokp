Testing
=======

Setup
-----

Database
^^^^^^^^

Create an empty database used for testing. In the new database, create a new
extension "postgis" and create the schemas "data" and "context", both owned by
the user which owns the database.

testing.ini
^^^^^^^^^^^

Make a copy of the ``testing.ini.sample`` file, name it ``testing.ini`` and
adapt it to your needs (namely set the database connection to the one you
created above).

Install requirements
^^^^^^^^^^^^^^^^^^^^

Install the requirements needed for testing::

    (env) $ pip install - e.[testing]

You may also need the ``xvfb`` package to run tests with the virtual display::

    sudo apt-get install xvfb


ChromeDriver
^^^^^^^^^^^^

Download the `ChromeDriver`_ which matches your installed version of Chrome.

.. _ChromeDriver: https://sites.google.com/a/chromium.org/chromedriver/downloads

Specify the path to the downloaded chromedriver executable in your
``testing.ini`` file.


Run tests
---------

Run all tests::

    (env) $ pytest

Run tests with browser window popping up::

    (env) $ pytest -pop

To run only a selected test, mark the test with::

    @pytest.mark.foo
    def test_something():

... and run the test as follows::

    (env) $ pytest -m foo

