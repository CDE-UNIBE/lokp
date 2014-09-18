Customization
=============

The customization is an important aspect of any instance of LOKP and it serves
mainly two purposes:

1. It defines the attributes which make up the Activities and Stakeholders.
   Without these definitions, the LOKP does not work properly.
2. It provides the Graphical User Interface (GUI), along with its translation.


Currently, the following customizations are known:

* `LO`_: The customization used for the `Land Observatory`_.
* `SPM`_: The customization used for the `Stakeholder Platform Madagascar`_.

.. _LO: https://github.com/CDE-UNIBE/lokp_custom_lo
.. _Land Observatory: http://www.landobservatory.org
.. _SPM: https://github.com/CDE-UNIBE/lokp_custom_spm
.. _Stakeholder Platform Madagascar: http://spm.esapp.info

Each customization needs to have a predefined structure and should contain at
least the following directories:

* ``/profiles/`` The profiles folder contains the configuration files for the
  attributes of Activities and Stakeholders, as well as some configuration of
  the application itself.
* ``/scripts/`` The scripts folder contains mainly SQL scripts which can be used
  populate a new database with the attributes used in the configuration. It also
  contains scripts to perform hotfixes on the database.

* ``/templates/`` The templates folder contains the templates needed for the
  Graphical User Interface of the customization. Here, the HTML representation
  of the tool is defined.
* ``/static/`` The static folder contains static assets of the GUI, such as CSS
  or JavaScript files, documents or images.
* ``/locale/`` The locale folder contains the translation files for the GUI.


Profiles
--------

The profiles can be used to configure the attributes of Activities and
Stakeholders.

The configuration of the attributes takes place in a `YAML`_ file. Please note
that **the keys, values and catetories have to be in the database first** before
you can use their IDs to configure the Activities and Stakeholders.

.. _YAML: http://en.wikipedia.org/wiki/YAML


YAML Structure
^^^^^^^^^^^^^^

The basic structure of the configuration YAMLs (``new_activity.yml`` and
``new_stakeholder.yml``) is as follows:

.. code-block:: yaml

    fields:
      # Category: The ID of the category.
      1:
        # (optional) Provide an order number to fix the sequence of the
        # categories.
        order: 1
        # Subcategory: The ID of another category (as a subcategory or thematic
        # group). The Category and the Subcategory can have the same ID (eg. if
        # no Subcategory is defined).
        11:
          # (optional) Provide an order number to fix the sequence of the
          # subcategories.
          order: 1
          # (optional) Indicate if the name of this Subcategory should appear in
          # the details page of an Activity or a Stakeholder.
          # Default is false.
          showindetails: true
          # (optional) The map settings if this thematic group contains a map.
          # Currently, only one map per configuration is valid.
          map:
            # The name of the map. Must be unique within the configuration.
            name: "mapname"
            # The mode of the map. Possible values are "multipoints" or
            # "singlepoint".
            mode: "singlepoint"
          # (optional) The involvement settings if this thematic group contains
          # an involvement.
          involvement:
            # The name of the involvement. Must be unique within the
            # configuration.
            name: "involvementname"
            # Possible Stakeholder_Role(s) of this involvement as array.
            # Corresponds to the IDs of the roles in the database. Each role can
            # only appear once within the configuration. For Stakeholders (in-
            # volvements can only be added from Activity side), the involvement
            # must always be repeatable and all roles can be added to the same
            # involvement.
            roles: [1,2]
            # (optional) The involvement can be entered multiple times.
            repeat: true
          # Taggroup: Taggroups are numbered continuously (1 to n).
          1:
            # (optional) Provide an order number to fix the sequence of the
            # taggroups.
            order: 1
            # (optional) This taggroup can be entered multiple times.
            repeat: true
            # (optional) This taggroup can contain a polygon geometry.
            geometry: true
            # Key: The ID of a key.
            3:
              # (optional) This key is the maintag. Each taggroup needs to have
              # exactly one maintag. A key defined as maintag needs to be unique
              # throughout the configuration.
              maintag: true
              # (optional) A validator for this key. Important: This will
              # overwrite the default validator for this key set in the
              # database! So far, only numeric ranges can be specified.
              # Example 1: Value between 0 and 10: [0,10].
              # Example 2: Minimal value of 100: [100].
              validator: [0,10]
              # (optional) This key is to be part of a short representation in
              # the involvement overview. Only a few keys should be used for
              # this overview (Example: Name and Country for Stakeholders).
              # The keys appear in the order of the integer specified here. The
              # first one is used to search when adding new involvements.
              involvementoverview: 1
              # (optional) This key is to be used as a column of the grid. The
              # columns are in the order of the integer specified here.
              gridcolumn: 1
              # (optional) This key is used for map symbolization. The one with
              # the lowest integer is used as default map symbolization.
              mapsymbol: 1
              # (optional) Mandatory fields need to be filled out for the form
              # to be submitted. Use with caution for forms with multiple cate-
              # gories because the user cannot jump to the next page without
              # filling out something.
              mandatory: true
              # (optional) Desired fields are highlighted in the form but the
              # form can be submitted if these fields are left empty.
              desired: true
              # (optional) A filter can be set on this key.
              filterable: true
              # (optional) This key is used as the default search option for
              # either Activities or Stakeholders (used for example in the
              # grid view).
              default_search: true
            # Key: The ID of a key. If no additional parameter is set for this
            key, use 'null' as a value.
            25: null


.. rubric:: Categories

Categories are used to structure the attributes (group them thematically). There
are two levels of categories:

* Category: The main category. For example in the form of the `Land
  Observatory`_, this corresponds to the green buttons on the right of the form.
* Subcategory or Thematic Group: The second level of categories. For example in
  the `Land Observatory`_, this corresponds to the orange headers in the form.

Both types of categories are defined only as IDs in the configuration YAML. The
lookup table (``data.categories``) is the same for both and they can be both
translated there.

New categories are to be entered in English.

.. _Land Observatory: http://www.landobservatory.org


.. rubric:: Keys

The IDs of the keys defined in the configuration YAML correspond to the ones in
the database (table ``data.a_keys`` or ``data.sh_keys``). Furthermore, this
table serves to define:

* type: the type of the values belonging to this key. This defines which kind of
  input field is shown in the form. Valid are:

  * Dropdown: There need to be some values (see below) for this key
  * Checkbox: There need to be some values (see below) for this key
  * InputToken: There need to be some values (see below) for this key
  * Number: Float
  * Integer
  * IntegerDropdown: A dropdown of numbers based on the validator range
  * String: One line of text
  * Text: A larger text (textarea)
  * Date: A date
  * Files

* helptext: shown in the form next to the input field, for example 'ha' or
  'years').
* validator: a default validator for this key (or its values to be precise). It
  can be overwritten in the YAML configuration. See the examples in the basic
  structure of the YAML configuration above to see how to define the validator.

Keys can be translated in the same database table.


.. rubric:: Keys

The IDs of the values defined in the configuration YAML correspond to the ones
in the database (table ``data.a_values`` or ``data.sh_values``). Furthermore,
this table serves to define:

* fk_key: the key this value belongs to.
* order: optionally provide an ordering of the values of the same keys. If left
  empty, the values are ordered alphabetically.

Values can be translated in the same database table.


Local Profile
^^^^^^^^^^^^^

There is the possibility to create local profiles which extend the global
profile, allowing thus to provide additional attributes for each local profile.

The configuration of local profiles takes place in separate configuration YAMLs
and follows the basic structure of the global configuration YAML. Indicating the
ID of the category, subcategory and taggroups allows to place a local key
exactly where it should be. New categories, subcategories and taggroups can be
created (note that they also need to be in the database first!), in which case a
maintag must also be specified correctly. It is possible to overwrite an
existing validator in a local profile.

.. note::
  So far, it is only possible to add new keys. For the time being, no keys can
  be removed (or hidden) in a local profile.

Example of the configuration of a local new_activity.yml for the Laos profile:

.. code-block:: yaml

    fields:
      # [C] 2: General Information
      2:
        # [C-THG] 12: Land Area
        42:
          # [TG]
          1:
            # [K] 52: Lao specific key 1
            52:
              maintag: true
              validator: [10, 20]


Graphical User Interface
------------------------

The GUI is created with `Mako`_ templates. If you want to create your own
customization, use a preexisting customization (see list above) as a starting
point as the templates should be named exactly the same.

.. _Mako: http://www.makotemplates.org/
