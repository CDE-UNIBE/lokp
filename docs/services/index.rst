Introduction
============

The data for the LOKP can be accessed and queried through REST services. This
also permits external applications to communicate with the LOKP data, as it can
be seen for example in the QGIS plugin.


.. _services-output-formats:

Output Formats
--------------

There are different output formats available which have to be provided when
requesting a service.

.. rubric:: Available output services

* ``JSON``: A JSON representation
* ``HTML``: The HTML representation of an Activity or a Stakeholder. This
returns a rendered template which is basically the grid or the detail view.


.. rubric:: Available services

* `Read One`_: Read an Activity or a Stakeholder based on its UUID.
* `Read Many`_: Read multiple Activities or Stakeholders.


.. _Read One: readone.html
.. _Read Many: readmany.html
