flaskies
========

.. _flaskies: https://github.com/vc-h/flaskies
.. _flask: http://flask.pocoo.org/

Some flask <http://flask.pocoo.org>
blueprints and applications for introspections.

* `flaskies`_ has a flat file organzation structure:

  - `flaskies`_ could be placed side-by-side with other `flask`_ applications
  - most probably, `flaskies`_ is not intended to be a `python` package

* `flaskies`_ :samp:`{modules}`, each implements:

  - an instance of :class:`flask.Blueprint`, e.g.

    .. code-block:: python

       module = Blueprint('module',__name__)

  - the :samp:`{module}` is executable

  - the ``'__main__'`` block runs a test server
    registered with the `blueprint`, e.g.

    .. code-block:: python

       if __name__ == '__main__':
           app = Flask(__nam__)
           app.register_blueprint(module)
           app.run(debug=True,use_reloader=True)

  - :py:mod:`doctest` to perform tests
  - :py:mod:`sphinx` :py:mod:`autodoc` to compile the documentation
