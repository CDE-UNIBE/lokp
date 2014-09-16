.. _glossary:

Glossary
========

.. glossary::
   :sorted:


   Activities
   Activity
     In the context of the LOKP, an Activity can be any action which manifests
     itself spatially and is performed by one or many :term:`Stakeholders`.

     The default :term:`Item Type` for Activities is ``a`` (see :class:`lmkp.utils.validate_item_type`).


   Stakeholders
   Stakeholder
     In the context of the LOKP, a Stakeholder can be any kind of actor
     performing :term:`Activities` manifesting themselves spatially.

     The default :term:`Item Type` for Stakeholders is ``sh`` (see :class:`lmkp.utils.validate_item_type`).


   Item Type
     In the LOKP, :term:`Activities` and :term:`Stakeholders` share a lot of common attributes and functions. The Item Type (``item_type``) helps to differentiate between the two.

     See :class:`lmkp.utils.validate_item_type` for more information.


   Items
   Item
     The term `Items` is used to label both :term:`Activities` and :term:`Stakeholders`.


   Status
     Each version of an :term:`Item` has a status which is based on the review process and determines the visibility of the version. The following statuses exist: ``pending``, ``active``, ``inactive``, ``deleted``, ``rejected`` and ``edited``.


   Profile
     Profiles are used to allow a specific configuration based on spatial or thematic criteria.

     See `Customization of profiles`_ for more information.


   Locale
     Locales are used to translate both the interface and the database attributes of the LOKP.

     See `Translation`_ for more information.


   Pyramid
     The LOKP is based on the `Pyramid`_ web framework, which is part of the Pylons framework. Please refer to the `Pyramid documentation`_ for further details.


.. _Customization of profiles: customization.html#profiles
.. _Translation: translation.html
.. _Pyramid: http://www.pylonsproject.org/
.. _Pyramid documentation: http://pyramid.readthedocs.org/en/latest/
