.. _glossary:

Glossary
========

.. glossary::
   :sorted:


   Activities
   Activity
     In the context of the LOKP, an Activity can be any action which manifests
     itself spatially and is performed by one or many :term:`Stakeholders`.

     The default :term:`Item Type` for Activities is ``a`` (see :class:`lokp.utils.validate_item_type`).


   Stakeholders
   Stakeholder
     In the context of the LOKP, a Stakeholder can be any kind of actor
     performing :term:`Activities` manifesting themselves spatially.

     The default :term:`Item Type` for Stakeholders is ``sh`` (see :class:`lokp.utils.validate_item_type`).


   Item Type
     In the LOKP, :term:`Activities` and :term:`Stakeholders` share a lot of common attributes and functions. The Item Type (``item_type``) helps to differentiate between the two.

     See :class:`lokp.utils.validate_item_type` for more information.


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

   Uids
   Uid
   UUID
     The LOKP uses Universally Unique Identifiers (UUID) to identify for example :term:`Activities` or :term:`Stakeholders`. This allows to synchronize data on these items across multiple instances of the LOKP.

     See `Universally unique identifier on Wikipedia`_ for further details.

   Customized template
     :term:`Customizations` allow to define the look of the LOKP. For the Graphical User Interface (GUI), this can be done through the templates found in the directory ``/templates/`` of the customization folder.

     See `Customization`_ for more information.

   Customization
   Customizations
     Customizations allow to define the attributes of :term:`Activities` and :term:`Stakeholders` and the look of the LOKP.

     See `Customization`_ for more information.

   Moderator
   Moderators
     Moderators within the context of the LOKP are a user group with the privileges to review (approve or reject) pending versions of :term:`Activities` or :term:`Stakeholders`.

   Administrator
   Administrators
     Administrators have the privilege to perform administrative tasks such as add or edit translations, manage users etc.

.. _Universally unique identifier on Wikipedia: http://en.wikipedia.org/wiki/Universally_unique_identifier
.. _Customization of profiles: customization.html#profiles
.. _Translation: translation.html
.. _Pyramid: http://www.pylonsproject.org/
.. _Pyramid documentation: http://pyramid.readthedocs.org/en/latest/
.. _Customization: customization.html
