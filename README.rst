flaskies
========

.. _flaskies: https://github.com/vc-h/flaskies
.. _flask: http://flask.pocoo.org/

Some flask <http://flask.pocoo.org>
blueprints and applications for introspections.

* `flaskies`_ has a flat file organzation structure:

  - `flaskies`_ could be placed side-by-side with other `flask`_ applications
  - `flaskies`_ is not a `python` package probably

* `flaskies`_ modules_, each implements:

  - an instance of :class:`flask.Blueprint`
  - the associated :samp:`create_app_{module}` to return
    a :py:obj:`Flask` `app` for running the `blueprint`
  - the :samp:`{module}` is executable to run the experimental server
  - test cases via :py:mod:`doctest` and documentations


Modules
-------

* :py:mod:`hello` module: ``'hello world'`` for using

  - :meth:`flask.escape`, and :meth:`flask.Markup`
  - :meth:`flask.Flask.testclient`
