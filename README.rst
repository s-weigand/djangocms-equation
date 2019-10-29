==================
djangocms-equation
==================


.. .. image:: https://img.shields.io/pypi/v/djangocms-equation.svg
           :target: https://pypi.python.org/pypi/djangocms-equation
           :alt: Latest PyPi Release

.. image:: https://api.travis-ci.org/s-weigand/djangocms-equation.svg?branch=master
        :target: https://travis-ci.org/s-weigand/djangocms-equation
        :alt: Test Status

.. image:: https://readthedocs.org/projects/djangocms-equation/badge/?version=latest
        :target: https://djangocms-equation.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/s-weigand/djangocms-equation/shield.svg
        :target: https://pyup.io/repos/github/s-weigand/djangocms-equation/
        :alt: Python Updates

.. image:: https://badges.greenkeeper.io/s-weigand/djangocms-equation.svg
        :target: https://greenkeeper.io/
        :alt: Typescript/Javascript Updates

.. image:: https://coveralls.io/repos/github/s-weigand/djangocms-equation/badge.svg?branch=master
        :target: https://coveralls.io/github/s-weigand/djangocms-equation?branch=master
        :alt: Code Coverage

.. image:: https://percy.io/static/images/percy-badge.svg
        :target: https://percy.io/s-weigand/djangocms-equation
        :alt: This project is using Percy.io for visual regression testing.

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/psf/black
        :alt: Code style Python: black

.. image:: https://img.shields.io/badge/code_style-prettier-ff69b4.svg
        :target: https://prettier.io/
        :alt: Code style TypeScript: prettier


DjangoCMS plugin to write equations, utilizing KaTeX


* Free software: Apache Software License 2.0
* Documentation: https://djangocms-equation.readthedocs.io.


Features
--------

* Enables the use of LaTeX for equations with django-cms
* Live editing of LaTeX Code, via KaTeX

Installation
------------
Install the plugin from PyPi

.. code-block:: bash

    $ pip install djangocms_equation

Add it to the installed apps in the ``settings.py`` of your django-cms project.

.. code-block:: python

    "INSTALLED_APPS": [..., "djangocms_equation"]

For the Equations to be properly displayed in ``djangocms-text-ckeditor``,
while edit it, you need to add the css file to the allowed of ckeditor.
To do this simply add the following lines to the `settings.py`
of your django-cms project.

.. code-block:: python

    CKEDITOR_SETTINGS = {
        "contentsCss": ["/static/djangocms_equation/css/change_form_template.css"]
    }


.. note::
    The equations might be rendered properly in ckeditor-windows,when they are added the first
    time. This can be fixed by saving the text plugin or having another equation on the page.

Credits
-------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
