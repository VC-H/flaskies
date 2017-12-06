#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.queriesdemo
====================

:Copyright: © 2017 by Victor Hui.
:Licence: BSD-3-Clause (see LICENSE for more details)

Test :class:`flask.Flask` ``get`` query handling in :mod:`jinja2` templates
---------------------------------------------------------------------------

* create a :class:`Flask.Blueprint` :py:obj:`queriesdemo`

.. code-block:: python

   queriesdemo = Blueprint('queriesdemo',import_name=__name__)

* define three :py:obj:`view_func`'s:

  - test :meth:`flask.render_template_string`
  - test ``request.args`` in :mod:`jinja2` templates

.. literalinclude:: ../queriesdemo.py
   :pyobject: getx

.. literalinclude:: ../queriesdemo.py
   :pyobject: getx_unsafe

.. literalinclude:: ../queriesdemo.py
   :pyobject: getargs

-----
"""

from __future__ import print_function, unicode_literals
import sys, re
from flask import Flask, Blueprint, render_template_string, escape, Markup

queriesdemo = Blueprint('queriesdemo',__name__)

@queriesdemo.route('/getx')
def getx():
    return render_template_string('{{request.args.get("x")}}')

@queriesdemo.route('/getx_unsafe')
def getx_unsafe():
    return render_template_string('{{request.args.get("x")|safe}}')

@queriesdemo.route('/getargs')
def getargs():
    return render_template_string('{{request.args}}')

def create_app_queriesdemo(app=None):
    """return the ``app`` registered with ``queriesdemo`` ``blueprint``

    >>> from werkzeug import ImmutableMultiDict
    >>> from flask import request
    >>> app = create_app_queriesdemo()
    >>> testclient = app.test_client()

    * no query

    >>> got = testclient.get('/getx')
    >>> got_unsafe = testclient.get('/getx_unsafe')
    >>> (got.get_data(as_text=True) ==
    ...  got_unsafe.get_data(as_text=True) ==
    ... "None")
    True

    * appropriate queries

    >>> got = testclient.get('/getx?x=1')
    >>> got_unsafe = testclient.get('/getx_unsafe?x=1')
    >>> (got.get_data(as_text=True) ==
    ...  got_unsafe.get_data(as_text=True) ==
    ... "1")
    True

    >>> got = testclient.get('/getx?x=x')
    >>> got_unsafe = testclient.get('/getx_unsafe?x=x')
    >>> (got.get_data(as_text=True) ==
    ...  got_unsafe.get_data(as_text=True) ==
    ...  "x")
    True

    * inappropriate queries

    >>> got = testclient.get('/getx?y=0')
    >>> got_unsafe = testclient.get('/getx_unsafe?y=0')
    >>> (got.get_data(as_text=True) ==
    ...  got_unsafe.get_data(as_text=True) ==
    ...  'None')
    True

    >>> got = testclient.get('/getx?x=y&y=x')
    >>> got_unsafe = testclient.get('/getx_unsafe?x=y&y=x')
    >>> (got.get_data(as_text=True) ==
    ...  got_unsafe.get_data(as_text=True) ==
    ...  "y")
    True

    * potential ``xxs`` attacks if queries were presumed `safe`

    >>> img = '<img src=/static/>'
    >>> got_unsafe = testclient.get('/getx_unsafe?x='+img)
    >>> got_unsafe.get_data(as_text=True) == img
    True
    >>> got = testclient.get('/getx?x='+img)
    >>> (got.get_data(as_text=True) == escape(img) ==
    ... '&lt;img src=/static/&gt;')
    True

    >>> href = '<a href=/>/</a>'
    >>> got_unsafe = testclient.get('/getx_unsafe?x='+href)
    >>> got_unsafe.get_data(as_text=True) == href
    True
    >>> got = testclient.get('/getx?x='+href)
    >>> (got.get_data(as_text=True) == escape(href) ==
    ... '&lt;a href=/&gt;/&lt;/a&gt;')
    True

    >>> alert = '<script>alert("hi!")</script>'
    >>> got_unsafe = testclient.get('/getx_unsafe?x='+alert)
    >>> got_unsafe.get_data(as_text=True) == alert
    True
    >>> got = testclient.get('/getx?x='+alert)
    >>> (got.get_data(as_text=True) == escape(alert) ==
    ... '&lt;script&gt;alert(&#34;hi!&#34;)&lt;/script&gt;')
    True

    * multiple queries

    >>> got = testclient.get('/getargs')
    >>> got.get_data(as_text=True) == repr(ImmutableMultiDict([]))
    True

    >>> got = testclient.get('/getargs?x=1')
    >>> (eval(Markup(got.get_data(as_text=True)).unescape()) ==
    ...  ImmutableMultiDict({'x':'1'}))
    True

    >>> got = testclient.get('/getargs?x=1&y=0')
    >>> (eval(Markup(got.get_data(as_text=True)).unescape()) ==
    ...  ImmutableMultiDict({'x':'1','y':'0'}))
    True

    """

    if app is None:
        app = Flask(__name__)
    app.register_blueprint(queriesdemo)
    return app


if __name__ == '__main__':

    import sys
    import doctest

    if sys.argv[0] != "":
        app = create_app_queriesdemo()
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(create_app_queriesdemo.__doc__))
