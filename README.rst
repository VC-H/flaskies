flaskies
========

.. _flaskies: https://github.com/vc-h/flaskies
.. _flask: http://flask.pocoo.org/

Some `flask`_ blueprints and applications for introspections.

* `flaskies`_ has a flat file organzation structure:

  - `flaskies`_ could be placed side-by-side with other `flask`_ applications
  - `flaskies`_ is not a `python` package probably

* the modules, each implements

  - an instance of :class:`flask.Blueprint`
  - an associated `create_app_module` to return a :py:obj:`Flask` `app` for
    running the `blueprint`
  - ``__name__ == '__main__'`` executes the `app`
  - some test cases in `doctest` and documentations

Modules
-------

* :py:mod:`hello` module: ``'hello world'`` for using

  - :meth:`flask.escape`, and :meth:`flask.Markup`
  - :meth:`app.testclient`

Table of Contents
-----------------

.. toctree::
   :maxdepth: 1

   hello
