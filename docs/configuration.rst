Configuration
=============

This section aims to give an overview of all the configuration options which can
be made in the main configuration file (``development.ini`` or 
``production.ini``) of the application.


.. _configuration-customization:

.. rubric:: Customization

``lokp.customization``

The name of the customization directory. This directory needs to be located in 
``lokp/customization``


.. _configuration-profiles:

.. rubric:: Profiles

``lokp.profiles_dir``

The subdirectory within the customization directory (see 
(ref:`configuration-customization`) which contains the profile configurations.

There can be multiple profiles in the profiles directory. This allows to have
more than one instances of your customization running with the same code base
but with slightly different attributes. For example, you could use a different
profile for the development version and for the productive version.


.. _configuration-wms:

.. rubric:: WMS

``lokp.base_wms``

The base URL of the WMS to be used for the context layers.


.. _configuration-admin-password:

.. rubric:: Administration Password

``lokp.admin_password``

The password of the administration account (username: ``admin``).


.. _configuration-admin-email:

.. rubric:: Administration Email

``lokp.admin_email``

The E-Mail address of the administrator. Some of the notifications or error 
messages will be sent to this address so make sure it is valid and checked 
regularly.


.. _configuration-comments-url:

.. rubric:: Comments

``lokp.comments_url``

The URL of the commenting system to be used.


.. _configuration-files:

.. rubric:: Files

``lokp.file_upload_dir``

``lokp.file_upload_max_size``

``lokp.file_mime_extensions``

The settings for the file upload functionality.


.. _configuration-use-js-builds:

.. rubric:: Use JS Builds

``lokp.use_js_builds``

*deprecated*: This parameter is or will become deprecated as ExtJS is not used
anymore.
