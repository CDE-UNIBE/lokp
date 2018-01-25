.. note::
    This section is not up to date anymore after release 1.0.

Translation
===========

The LOKP is completely translateable. However, it is important to note that 
there are different ways to translate the various strings of the LOKP.

The strings which appear in the graphical user interface are translated using 
the gettext system based on portable object (.po) files. See `Wikipedia`_ for
further details. Both the strings of the content-agnostic core platform and 
those of the customization are translated this way.

The values in the database, eg. the attributes of an Activity and a Stakeholder
can also be translated. Their translations are stored in the database, which can
be done automatically in the administration panel.

.. _Wikipedia: http://en.wikipedia.org/wiki/Gettext


For Translators
---------------

This section is for translators, who were contacted directly by one of the 
developers.


Graphical User Interface
^^^^^^^^^^^^^^^^^^^^^^^^

The translation of the Graphical User Interface is done using ``.po`` files,
there is one for the core platform and one for the customization. Usually, both
of these files were sent to you by a developer.

There are free tools available, which you can use to translate the strings in
these files. We suggest you use `Poedit`_ for the task. Download, install and
start the program, then open one of the files.

Select each entry and use the field at the bottom left for the translation (see
also this `screenshot`_). Once you are done, you can save the file and send it 
back to the developer.

.. topic:: Placeholders

    Some strings to translate may contain special characters such as ``{0}``, 
    ``{1}`` and so on, or ``%s``. 

    =========================  =========================
    Original                   Translation
    =========================  =========================
    Hello, my name is %s!      Bonjour, je m'appelle %s!
    We have {0} weather today  Tenemos {0} tiempo hoy
    =========================  =========================

    These are placeholders and should be added unchanged to the translation.

.. _Poedit: http://www.poedit.net/
.. _screenshot: _static/images/poedit.png


Attributes
^^^^^^^^^^

The translation of attributes and categories is done in spreadsheets. There are
3 different spreadsheets, for Activities, Stakeholders and Categories. You
should receive them from a developer.

You can do the translation directly in the spreadsheets and send them back to 
the developer.

A few things to consider when translating in the spreadsheets:

* Please use the columns "Name (translation)" and "Helptext (translation)" for 
  translation.
* It may be helpful for the translation to open the form in English to see the 
  context of the attributes. If you do not know where to find the form, please
  ask the developer.
* The translations should be as short as possible.
* Please write only in the orange fields.
* Use the "Additional comments" column if you have remarks or questions. Please 
  do not write questions in the translation field.
  

For Developers
--------------

This section is for developers of the LOKP and has the aim to describe the steps
necessary to extract strings for translation, prepare the files for the
translators and afterwards insert the translations.


During development
^^^^^^^^^^^^^^^^^^

.. rubric:: Python

Translation in Python views is done through a ``TranslationStringFactory``, 
which is added as a subscriber to every new request as it is described `here`_. 
For this reason, there is no need to create a new ``TranslationStringFactory`` 
every time, instead the function attached to the request can be used::

    _ = request.translate
    print _('String to translate')

.. rubric:: Templates

In the templates, the translate function of the request is usually available
directly, which makes it easy to translate strings in the templates::

    ${_('String to translate')}

For further information, please refer to the section on `Internationalization 
and Localization`_ in the Pyramid manual.

.. _here: http://blog.abourget.net/2011/1/13/pyramid-and-mako:-how-to-do-i18n-the-pylons-way/
.. _Internationalization and Localization: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html


Translate the Core Platform
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. rubric:: Before translation

Use the following command to extract all the strings marked for translation::

    (env) $ python setup.py extract_messages

This will create or update the ``lokp/locale/lokp.pot`` file which serves as a
template for all the ``.po`` files in the various languages.

To update all language files (the ``.po`` files), run::

    (env) $ python setup.py update_catalog

After that, the ``lokp.po`` files for all languages are updated. You can now
send these files to the respective translators for translation.


.. rubric:: After translation

Once the ``lokp.po`` files are translated, you need to compile them for the
translation to become active. You achieve this by running::

    (env) $ python setup.py compile_catalog


Translate the Customization
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The translation of the strings contained in the customization of the LOKP is a
bit more complicated because it should exclude the strings already translated in
the core platform. For this reason, a special ``setup_custom.py`` is used which
needs to be adapted to match the customization to translate.

This section describes the steps necessary to translate a customization 
``[CUSTOM]`` into a specific language ``[LOCALE]``. For the customization, these
steps need to be repeated for every single language.

The accompanying examples illustrate the translation of the ``lo`` customization
into Spanish (``es``).

.. rubric:: Before translation

.. warning::
   Using the unchanged ``setup_custom.py`` will extract the messages of **all
   customization folders** situated in ``lokp/customization/``. If you have
   other customized folders there, adapt your ``setup_custom.py`` to include 
   only the folder you want to translate.

Extract all the strings marked for translation of the customization and create
the template ``.pot`` file::

    (env) $ python setup_custom.py extract_messages -o lokp/customization/[CUSTOM]/locale/[CUSTOM].pot

.. pull-quote::

   Example: Extract all strings of the LO customization::
   
       (env) $ python setup_custom.py extract_messages -o lokp/customization/lo/locale/lo.pot

Update the language file for a language based on the translation template file::

    (env) $ python setup_custom.py update_catalog -l [LOCALE] --domain [CUSTOM] -i lokp/customization/[CUSTOM]/locale/[CUSTOM].pot -d lokp/customization/[CUSTOM]/locale

.. pull-quote::

   Example: Update the language file of the LO customization for Spanish::
   
       (env) $ python setup_custom.py update_catalog -l es --domain lo -i lokp/customization/lo/locale/lo.pot -d lokp/customization/lo/locale


.. rubric:: After translation

Compile the translated language files::

    (env) $ python setup_custom.py compile_catalog -l [LOCALE] --domain [CUSTOM] -d lokp/customization/[CUSTOM]/locale

.. pull-quote::

   Example: Compile the language catalog of the LO customization for Spanish::
   
       (env) $ python setup_custom.py compile_catalog -l es --domain lo -d lokp/customization/lo/locale


Translate the Attributes
^^^^^^^^^^^^^^^^^^^^^^^^

The attributes are translated directly in the database. There is a script to
insert multiple (all) translations at once, but it is crucial that they are in
the correct form to do so. Translators can use a spreadsheet for translations
which can be converted into a CSV file and handed over to the script in the
administration panel.

.. rubric:: Before translation

You will need to repeat the following steps 3 times, for Activities, 
Stakeholders and Categories (containing the categories of both Activities and 
Stakeholders)

You can get a list of all Categories, Activities and Stakeholders through the
service at ``/translation/extract/[TYPE]?lang=[LOCALE]`` where 

* ``[TYPE]`` is one of
    * ``activities``
    * ``stakeholders``
    * ``categories``
* ``[LOCALE]`` is the locale of the language you'd like to translate to. This is
  important as the service will also output already translated strings.

Example: `/translation/extract/activities?lang=es`_.

.. note:: Please note that you need translation permissions to access this 
  service.

Open one of the templates (either `template_keyvalues.xls`_ for Activities or 
Stakeholders, or `template_categories.xls`_ for Categories) and delete all 
existing content. Select the first row and paste the copied values from the 
clipboard. With the first column still selected, use "Data" > "Text to Columns" 
with Semicolon as separator to spread the data over all columns. Format the 
sheet if needed. In the original format, the translators should only write in 
the cells with an orange background color. You can protect the sheet using 
"Review" > "Protect Sheet", which automatically prevents writing to any 
non-orange cell.

Save the sheets and send them to the translators.

.. _/translation/extract/activities?lang=es: http://www.landobservatory.org/translation/extract/activities?lang=es
.. _template_keyvalues.xls: _static/files/template_keyvalues.xls
.. _template_categories.xls: _static/files/template_categories.xls


.. rubric:: After translation

To insert the translations done in a spreadsheet, you need to first open the 
file and copy the following columns to a new document:

* For Keys (do not copy Values!):
    * Name (original)
    * Name (translation)
    * Helptext (original)
    * Helptext (translation)
* For Values (do not copy Keys!):
    * Name (original)
    * Name (translation)
* For Categories:
    * Name (original)
    * Name (translation)

Save the new document as ``.csv`` and convert it to UTF-8 (eg. in Notepad++).
Also, add a header in the following form:

``Description;";";Db_Item;lang``

where Db_Item is one of ``A_Key``, ``A_Value``, ``SH_Key``, ``SH_Value``, 
``Category``.

Copy the file to ``lokp/documents/translation`` and open the administration
interface to insert the batch translation.


Add a new language
^^^^^^^^^^^^^^^^^^

If you'd like to add a new language for translation, you need to create a first
language file based on the template file. To do so, you can follow these steps.
Please make sure there is an initial template file (``.pot``) available first,
see above for how to do that.

.. note:: For new languages to appear in the GUI, you need to add them to the
  database first!

.. rubric:: Core platform

Create the initial catalog for a language::

    (env) $ python setup.py init_catalog -l [LOCALE]

.. rubric:: Customization

Create the initial catalog for a language::

    (env) $ python setup_custom.py init_catalog -l [LOCALE] --domain [CUSTOM] -i lokp/customization/[CUSTOM]/locale/[CUSTOM].pot -d lokp/customization/[CUSTOM]/locale

.. pull-quote::

   Example: Create the initial catalog of the LO customization for Spanish::
   
       (env) $ python setup_custom.py init_catalog -l es --domain lo -i lokp/customization/lo/locale/lo.pot -d lokp/customization/lo/locale


