Evaluation
==========

.. important::
    Please note that this service is currently rather experimental.

The evaluation JSON service can be accessed by sending a POST request to
``/evaluation``.


JSON Format
-----------

The JSON paylot sent via ``POST`` request must have the following
format::

  {
    "attributes": {
      "KEY/ITEM": "FUNCTION"
    },
    "group_by": [
      "KEY"
    ],
    "item": "ITEM",
    "translate": {
      "keys": [
        [
          "KEY"
        ]
      ]
    },
    "locale": "LOCALE",
    "profile": "PROFILE",
    "filter": "FILTER"
  }

See below for explanations.


``attributes``
~~~~~~~~~~~~~~

Determine which keys of the item are being looked at and the function
to apply to these keys. Entries should have the following form::

  "KEY/ITEM": "FUNCTION"

Where ``"KEY/ITEM"`` is either a valid key of the item or the item
itself (eg. ``"Activity"``).

``"FUNCTION"`` has to be one of the predefined functions which currently
are:

  * ``"sum"``: Perform a sum on the given key. This function is only
    valid if the key contains number values.

  * ``"count"``: Perform a count on the objects.

  * ``"count distinct"``: Perform a count on the objects but omit
    duplicates.


``group_by``
~~~~~~~~~~~~

A list of keys to group the results by.


``item``
~~~~~~~~

(Optional). Define which item is being looked at. Default value (if
omitted) is "Activity". Valid are "Activity" and "Stakeholder".


``translate``
~~~~~~~~~~~~~

(Optional). Optional list of keys and/or values which will be returned
translated.


``locale``
~~~~~~~~~~

(Optional). Optional list of locales used for translation.


``profile``
~~~~~~~~~~~

(Optional). Optional profile to limit the results.


``filter``
~~~~~~~~~~

(Optional). Optional filter parameter to apply to the results. This is
the filter query string as in the URL when applying a filter in the list
or on the map.


``a_ids``
~~~~~~~~~

(Optional). Optional array of Activity identifiers to filter the results
by.


``sh_ids``
~~~~~~~~~~

(Optional). Optional array of Stakeholder identifiers to filter the
results by.


Examples
--------

Example 1 (used by http://www.landobservatory.org/charts/bars/a)::

  {
    "item": "Activity",
    "attributes": {
      "Activity": "count",
      "Intended area (ha)": "sum"
    },
    "translate": {
      "keys": [
        [
          "Intention of Investment"
        ],
        [
          "Negotiation Status"
        ],
        [
          "Implementation status"
        ]
      ]
    },
    "group_by": [
      "Intention of Investment"
    ]
  }


Example 2 (used by http://www.landobservatory.org/charts/stackedbars/)::

  {
    "item": "Activity",
    "attributes": {
      "Activity": "count"
    },
    "profile": "global",
    "translate": {
      "keys": [
        [
          "Country",
          "Implementation status"
        ],
        [
          "Country",
          "Negotiation Status"
        ]
      ]
    },
    "group_by": [
      "Country",
      "Implementation status"
    ]
  }


Example 3 (used by http://www.landobservatory.org/charts/map/)::

  {
    "item": "Stakeholder",
    "attributes": {
      "Stakeholder": "count"
    },
    "group_by": [
      "Country of origin"
    ],
    "locales": [
      "code"
    ],
    "translate": {
      "keys": [
        [
          "Country of origin"
        ]
      ]
    },
    "profile": "laos"
  }


Example with filter::

  {
    "item": "Stakeholder",
    "attributes": {
      "Stakeholder": "count"
    },
    "translate": {
      "keys": [
        [
          "Country of origin"
        ]
      ]
    },
    "group_by": [
      "Country of origin"
    ],
    "filter": "a__Intended area (ha)__gt=300000&a__Intention of Investment__like=Agriculture"
  }


Example with filter by Activity ID::

  {
    "item": "Stakeholder",
    "attributes": {
      "Stakeholder": "count"
    },
    "translate": {
      "keys": [
        [
          "Country of origin"
        ]
      ]
    },
    "group_by": [
      "Country of origin"
    ],
    "a_ids": ["28363cf0-f150-4da9-a0fb-da4ea0a2de52"]
  }
