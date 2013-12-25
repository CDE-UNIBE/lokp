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