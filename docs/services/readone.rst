Read One
========

Read an Activity or a Stakeholder based on its unique identifier (UUID). 

There are 3 :ref:`read-one-variants` of this service and some 
:ref:`read-one-parameters` can be applied.


.. _read-one-variants:

Variants
--------

* :ref:`read-one-with-pending`
* :ref:`read-one-public`
* :ref:`read-one-active`



.. _read-one-with-pending:

Read One (with pending)
^^^^^^^^^^^^^^^^^^^^^^^

Returns all versions of an Activity or a Stakeholder, including pending versions
by the currently logged in user or all pending versions if logged in as a
moderator of the current profile.

Multiple versions are returned if they exist, ordered by version number with the
newest on top.

.. rubric:: URL

::

    /activities/json/[UUID]?[PARAMETERS]
    /stakeholders/json/[UUID]?[PARAMETERS]

* ``UUID``: The unique identifier (UUID) of the Activity or the Stakeholder.
* ``PARAMETERS``: Optional parameters, see :ref:`read-one-parameters` for more 
  details.

.. rubric:: Examples

* `/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3 <http://www.landobservatory.org/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3>`_
* `/stakeholders/json/7bc522fc-45f7-448c-ab5c-84a60e864671 <http://www.landobservatory.org/stakeholders/json/7bc522fc-45f7-448c-ab5c-84a60e864671>`_



.. _read-one-public:

Read One (public)
^^^^^^^^^^^^^^^^^

Returns only the versions of an Activity or a Stakeholder which are visible to
the public, meaning no pending versions are returned even if the user is logged
in.

Multiple versions are returned if they exist, ordered by version number with the
newest on top.

.. rubric:: URL

::

    /activities/public/json/[UUID]?[PARAMETERS]
    /stakeholders/public/json/[UUID]?[PARAMETERS]

* ``UUID``: The unique identifier (UUID) of the Activity or the Stakeholder.
* ``PARAMETERS``: Optional parameters, see :ref:`read-one-parameters` for more 
  details.

.. rubric:: Examples

* `/activities/public/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3 <http://www.landobservatory.org/activities/public/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3>`_
* `/stakeholders/public/json/7bc522fc-45f7-448c-ab5c-84a60e864671 <http://www.landobservatory.org/stakeholders/public/json/7bc522fc-45f7-448c-ab5c-84a60e864671>`_



.. _read-one-active:

Read One (active)
^^^^^^^^^^^^^^^^^

Returns only the active version of the Activity or a Stakeholder if there is one
available. This service therefore never returns more than 1 version.

.. rubric:: URL

::

    /activities/active/json/[UUID]?[PARAMETERS]
    /stakeholders/active/json/[UUID]?[PARAMETERS]

* ``UUID``: The unique identifier (UUID) of the Activity or the Stakeholder.
* ``PARAMETERS``: Optional parameters, see :ref:`read-one-parameters` for more 
  details.

.. rubric:: Examples

* `/activities/active/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3 <http://www.landobservatory.org/activities/active/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3>`_
* `/stakeholders/active/json/7bc522fc-45f7-448c-ab5c-84a60e864671 <http://www.landobservatory.org/stakeholders/active/json/7bc522fc-45f7-448c-ab5c-84a60e864671>`_



.. _read-one-parameters:

Parameters
----------

There are some query parameters which can also be combined. Please note that not
all of the parameters can be set for all variants of the Read One service.


Involvements
^^^^^^^^^^^^

``involvements`` (*string*): Specify the level of details for the involvements.

Possible values are:
  
* ``full`` (*default*): Full details with all the taggroups of the involvement.
* ``short``: A short representation of the involvement, not showing any 
  taggroups but only some attributes of the involvement itself (id, role, 
  status, ...)
* ``none``: No involvements are shown.

.. rubric:: Examples

* `/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?involvements=full <http://www.landobservatory.org/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?involvements=full>`_
* `/stakeholders/json/7bc522fc-45f7-448c-ab5c-84a60e864671?involvements=short <http://www.landobservatory.org/stakeholders/json/7bc522fc-45f7-448c-ab5c-84a60e864671?involvements=short>`_
* `/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?involvements=none <http://www.landobservatory.org/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?involvements=none>`_


Versions
^^^^^^^^

.. note::

   This parameter is not valid for the variant :ref:`read-one-active`.

``versions`` (*comma-separated list of integers*): Query specific versions. If 
none of the versions are not found, no results are returned.

.. rubric:: Examples

* `/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?versions=1,2 <http://www.landobservatory.org/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?versions=1,2>`_
* `/stakeholders/json/7bc522fc-45f7-448c-ab5c-84a60e864671?versions=2 <http://www.landobservatory.org/stakeholders/json/7bc522fc-45f7-448c-ab5c-84a60e864671?versions=2>`_


Geometry
^^^^^^^^

.. note::

   This parameter is only valid for Activities.

``geometry`` (*string*): Specify the level of details for the geometries of an 
Activity.

Possible values are:

* ``-`` (*default*): Only the representative (point) geometry of the Activity is
  returned.
* ``full``: All geometries are returned, meaning that also geometries of the 
  taggroups of the Activity are returned where available.

.. rubric:: Examples

* `/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?geometry=full <http://www.landobservatory.org/activities/json/888238c0-9a55-42f8-bf19-0b8b0cdbb6b3?geometry=full>`_
