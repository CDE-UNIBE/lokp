.. _read-many:

Read Many
=========

Read many Activities or Stakeholders.

There are 2 :ref:`read-many-variants` of this service and a number of
:ref:`read-many-parameters` can be applied.

.. _read-many-variants:

Variants
--------

* :ref:`read-many-with-pending`
* :ref:`read-many-public`


.. _read-many-with-pending:

Read Many (with pending)
^^^^^^^^^^^^^^^^^^^^^^^^

Return many Activities or Stakeholders. For each item, only one version is
visible, always the latest visible version to the current user.  This means that
logged in users can see their own pending versions and moderators of the current
profile can see pending versions as well.

By default, the items are ordered with the item having the most recent change
being on top.

.. rubric:: URL

::

    /activities/json?[PARAMETERS]
    /stakeholders/json?[PARAMETERS]

* ``PARAMETERS``: Optional parameters, see :ref:`read-many-parameters` for more
  details.

.. rubric:: Examples

* `/activities/json?limit=10 <http://www.landobservatory.org/activities/json?limit=10>`_
* `/stakeholders/json?limit=10 <http://www.landobservatory.org/activities/json?limit=10>`_



.. _read-many-public:

Read Many (public)
^^^^^^^^^^^^^^^^^^

Return many Activities or Stakeholders. For each item, only one version is
visible, always the latest visible version to the public. This means no pending
versions are returned, even if the user is logged in.

By default, the items are ordered with the item having the most recent change
being on top.

.. rubric:: URL

::

    /activities/public/json?[PARAMETERS]
    /stakeholders/public/json?[PARAMETERS]

* ``PARAMETERS``: Optional parameters, see :ref:`read-many-parameters` for more
  details.

.. rubric:: Examples

* `/activities/public/json <http://www.landobservatory.org/activities/public/json?limit=10>`_
* `/stakeholders/public/json <http://www.landobservatory.org/stakeholders/public/json?limit=10>`_





.. _read-many-parameters:

Parameters
----------

There are a number of query parameters which can also be combined. Please note
that not all of the parameters can be set for all variants of the Read Many
service.


Filters: Activities
^^^^^^^^^^^^^^^^^^^

``a__[A_Key]__[op]`` (*string*): Filter Activities or Stakeholders (through
involvements) based on Activity attributes.

* ``[A_Key]``: A valid Activity key. Translations are not valid, always use the
  original name.
* ``[op]``: A filter operator. Possible filter operators are listed in the
  tables below.

  =======  ====  ===========================
  =======  ====  ===========================
  ``eq``   ==    is equal to
  ``ne``   !=    is not equal to
  ``lt``   <     is less than
  ``lte``  <=    is less than or equal to
  ``gt``   >     is greater than
  ``gte``  >=    is greater than or equal to
  =======  ====  ===========================

  Possible filter operators for **number** values

  =========  ====  =============================================
  =========  ====  =============================================
  ``like``   ~     matches regular expression (case sensitive)
  ``ilike``  ~*    matches regular expression (case insensitive)
  =========  ====  =============================================

  Possible filter operators for **text** values

.. rubric:: Examples

* `/activities/json?a__Intended%20area%20(ha)__eq=25000 <http://www.landobservatory.org/activities/json?a__Intended%20area%20(ha)__eq=25000&limit=10>`_
* `/activities/json?a__Intention%20of%20Investment__like=Industry <http://www.landobservatory.org/activities/json?a__Intention%20of%20Investment__like=Industry&limit=10>`_
* `/stakeholders/json?a__Intended%20area%20(ha)__gte=1000000 <http://www.landobservatory.org/stakeholders/json?a__Intended%20area%20(ha)__gte=1000000&limit=10>`_


Filters: Stakeholders
^^^^^^^^^^^^^^^^^^^^^

``sh__[SH_Key]__[op]`` (*string*): Filter Activities (through involvements) or
Stakeholders based on Stakeholder attributes.

* ``[SH_Key]``: A valid Stakeholder key. Translations are not valid, always use
  the original name.
* ``[op]``: A filter operator. Possible filter operators are listed in the
  tables below.

  =======  ====  ===========================
  =======  ====  ===========================
  ``eq``   ==    is equal to
  ``ne``   !=    is not equal to
  ``lt``   <     is less than
  ``lte``  <=    is less than or equal to
  ``gt``   >     is greater than
  ``gte``  >=    is greater than or equal to
  =======  ====  ===========================

  Possible filter operators for **number** values

  =========  ====  =============================================
  =========  ====  =============================================
  ``like``   ~     matches regular expression (case sensitive)
  ``ilike``  ~*    matches regular expression (case insensitive)
  =========  ====  =============================================

  Possible filter operators for **text** values

.. rubric:: Examples

* `/activities/json?sh__Country%20of%20origin__like=Switzerland <http://www.landobservatory.org/activities/json?sh__Country%20of%20origin__like=Switzerland&limit=10>`_
* `/stakeholders/json?sh__Name__ilike=company <http://www.landobservatory.org/stakeholders/json?sh__Name__ilike=company&limit=10>`_
* `/stakeholders/json?sh__Economic%20Sector__nlike=Financial%20sector <http://www.landobservatory.org/stakeholders/json?sh__Economic%20Sector__nlike=Financial%20sector&limit=10>`_


Filters: Logical operator
^^^^^^^^^^^^^^^^^^^^^^^^^

``logical_op`` (*string*): The logical operator when querying Activities or
Stakeholders with multiple filters.

* ``and`` (*default*): All filter criteria must apply
* ``or``: At least one of the filter criteria must apply

.. rubric:: Examples

* `/activities/json?sh__Name__like=Venture&sh__Country%20of%20origin__like=India&logical_op=and <http://www.landobservatory.org/activities/json?sh__Name__like=Venture&sh__Country%20of%20origin__like=India&logical_op=and&limit=10>`_
* `/stakeholders/json?sh__Name__like=Venture&sh__Country%20of%20origin__like=India&logical_op=or <http://www.landobservatory.org/stakeholders/json?sh__Name__like=Venture&sh__Country%20of%20origin__like=India&logical_op=or&limit=10>`_


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

* `/activities/json?involvements=full <http://www.landobservatory.org/activities/json?involvements=full&limit=10>`_
* `/stakeholders/json?involvements=short <http://www.landobservatory.org/stakeholders/json?involvements=short&limit=10>`_
* `/activities/json?involvements=none <http://www.landobservatory.org/activities/json?involvements=none&limit=10>`_


Status
^^^^^^

``status`` (*string*): Show only versions of Activities or Stakeholders with a
certain status.

.. note::

   Not every status can be filtered. Primarily of interest is the filter
   ``status=pending``.

.. rubric:: Examples

* `/activities/json?status=pending <http://www.landobservatory.org/activities/json?status=pending&limit=10>`_
* `/stakeholders/json?status=pending <http://www.landobservatory.org/stakeholders/json?status=pending&limit=10>`_


Offset and Limit
^^^^^^^^^^^^^^^^

``offset`` (*integer*): The numbers of entries to leave out before showing the
  first.

``limit`` (*integer*): The numbers of items to show at a time.

.. rubric:: Examples

* `/activities/json?offset=0&limit=10 <http://www.landobservatory.org/activities/json?offset=0&limit=10>`_


Ordering
^^^^^^^^

``order_by`` (*string*): The attribute to order the results by. Needs to be a
  key of the corresponding Item (Activity Key for /activities, Stakeholder Key
  for /stakeholders).

``dir`` (*string*): The direction of the ordering.

  Possible values are:

  * ``asc`` (*default*): Ascending order (from small to big).
  * ``desc``: Descending order.

.. rubric:: Examples

* `/activities/json?order_by=Intended%20area%20(ha) <http://www.landobservatory.org/activities/json?order_by=Intended%20area%20(ha)&limit=10>`_
* `/stakeholders/json?order_by=Name&dir=DESC <http://www.landobservatory.org/stakeholders/json?order_by=Name&dir=DESC&limit=10>`_


Bounding Box and Spatial Reference System
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   This parameter is only valid for Activities.

``bbox`` (*string*): A bounding box to apply a geographic filter to the
  Activities.
``epsg`` (*string*): The code of a spatial reference system for the bounding box
  parameter. Best practice: use ``epsg=900913``.

* ``[bbox]``: A bounding box.
* ``profile``: Use the bounding box of the currently selected profile.

.. rubric:: Examples

* `/activities/json?bbox=11495976.178433%2C1114146.12413%2C11567062.614729%2C1241490.213235 <http://www.landobservatory.org/activities/json?bbox=11495976.178433%2C1114146.12413%2C11567062.614729%2C1241490.213235&limit=10>`_
* `/activities/json?bbox=profile <http://www.landobservatory.org/activities/json?bbox=profile&limit=10>`_

