.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/s-weigand/djangocms-equation/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

djangocms-equation could always use more documentation, whether as part of the
official djangocms-equation docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/s-weigand/djangocms-equation/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up ``djangocms_equation`` for local development.

1. Fork the ``djangocms_equation`` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/djangocms_equation.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv djangocms_equation
    $ cd djangocms-equation/
    $ pip install -r requirements_dev.txt
    $ pip install -e .

4. Install the ``pre-commit`` hooks, for quality assurance::

    $ pre-commit install && pre-commit install -t pre-push

5. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

6. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox and docker-compose_::

    $ docker-compose up -d
    $ tox

   Docker compose is needed for the integration tests, which use selenium_
   and the `selenium docker images`_.

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.5, 3.6 and 3.7. Check
   https://github.com/s-weigand/djangocms-equation/actions
   and make sure that the tests pass for all supported Python versions.

.. note::
  Due to racing conditions in the integration tests, which I couldn't completely eliminate,
  the CI might fail for some tests.
  In this case just write a comment, so I know to restart the test suite.

Tips
----

To run a subset of tests::

$ py.test tests.test_djangocms_equation


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bumpversion patch # possible: major / minor / patch
$ git push
$ git push --tags

Github actions will then deploy to PyPI if tests pass.

.. _docker-compose: https://docs.docker.com/compose/install/
.. _selenium: https://selenium-python.readthedocs.io/
.. _selenium docker images: https://github.com/SeleniumHQ/docker-selenium
