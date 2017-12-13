#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.queriesdemo
====================

Demo ``request.args`` handlings in :mod:`jinja2` templates
----------------------------------------------------------

.. ::
  Copyright: (c) 2017 by Victor Hui.
  Licence: BSD-3-Clause (see LICENSE for more details)

* new tests

  - ``GET`` method of :meth:`flask.request` for queries
  - ``request.args`` in :mod:`jinja2` templates
  - :meth:`flask.render_template_string`

* re-used

  - :meth:`hello.href`
  - :meth:`hello.re_findall_testcases`

* create a :py:obj:`queriesdemo` :class:`Blueprint`

.. code-block:: python

   queriesdemo = Blueprint('queriesdemo',import_name=__name__)

* define four :py:obj:`view_func`'s:

.. literalinclude:: ../queriesdemo.py
   :pyobject: getx

.. literalinclude:: ../queriesdemo.py
   :pyobject: getx_safe

.. literalinclude:: ../queriesdemo.py
   :pyobject: getargs

.. literalinclude:: ../queriesdemo.py
   :pyobject: viewtestcases

-----
"""

from __future__ import print_function, unicode_literals
import sys, re
from flask import (
    Flask, Blueprint, render_template, url_for,
    render_template_string, escape, Markup)
from hello import re_findall_testcases, href

queriesdemo = Blueprint('queriesdemo',__name__)

@queriesdemo.route('/getx')
def getx():
    return render_template_string('{{request.args.get("x")}}')

@queriesdemo.route('/getx_safe')
def getx_safe(): # it is actually unsafe!
    return render_template_string('{{request.args.get("x")|safe}}')

@queriesdemo.route('/getargs')
def getargs():
    return render_template_string('{{request.args}}')

def gettestcases():
    """return a table of testcases used in the doctest;

    >>> from werkzeug import ImmutableMultiDict
    >>> testapp = Flask(__name__)
    >>> testapp.register_blueprint(queriesdemo)
    >>> testclient = testapp.test_client()

    >>> with testapp.test_request_context():
    ...     testcases, unsafecases = gettestcases()
    >>> testcases == [
    ...     '/getx',         '/getx_safe',
    ...     '/getx?x=1',     '/getx_safe?x=1',
    ...     '/getx?x=x',     '/getx_safe?x=x',
    ...     '/getx?y=0',     '/getx_safe?y=0',
    ...     '/getx?x=y&y=x', '/getx_safe?x=y&y=x',
    ...     '/getargs',
    ...     '/getargs?x=1',
    ...     '/getargs?x=1&y=0'
    ... ]
    True

    * no query

    >>> got = testclient.get('/getx')
    >>> got_safe = testclient.get('/getx_safe')
    >>> (got.get_data(as_text=True) ==
    ...  got_safe.get_data(as_text=True) ==
    ... "None")
    True

    * appropriate queries

    >>> got = testclient.get('/getx?x=1')
    >>> got_safe = testclient.get('/getx_safe?x=1')
    >>> (got.get_data(as_text=True) ==
    ...  got_safe.get_data(as_text=True) ==
    ... "1")
    True

    >>> got = testclient.get('/getx?x=x')
    >>> got_safe = testclient.get('/getx_safe?x=x')
    >>> (got.get_data(as_text=True) ==
    ...  got_safe.get_data(as_text=True) ==
    ...  "x")
    True

    * inappropriate queries

    >>> got = testclient.get('/getx?y=0')
    >>> got_safe = testclient.get('/getx_safe?y=0')
    >>> (got.get_data(as_text=True) ==
    ...  got_safe.get_data(as_text=True) ==
    ...  'None')
    True

    >>> got = testclient.get('/getx?x=y&y=x')
    >>> got_safe = testclient.get('/getx_safe?x=y&y=x')
    >>> (got.get_data(as_text=True) ==
    ...  got_safe.get_data(as_text=True) ==
    ...  "y")
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

    * potential ``xxs`` attacks if queries were presumed `safe`

    >>> img = '''<img src='/static/'>'''
    >>> got_safe = testclient.get('/getx_safe?x='+img)
    >>> got_safe.get_data(as_text=True) == img
    True
    >>> got = testclient.get('/getx?x='+img)
    >>> (got.get_data(as_text=True) == escape(img) ==
    ... '&lt;img src=&#39;/static/&#39;&gt;')
    True

    >>> a = '''<a href='/'>/</a>'''
    >>> got_safe = testclient.get('/getx_safe?x='+a)
    >>> got_safe.get_data(as_text=True) == a
    True
    >>> got = testclient.get('/getx?x='+a)
    >>> (got.get_data(as_text=True) == escape(a) ==
    ... '&lt;a href=&#39;/&#39;&gt;/&lt;/a&gt;')
    True

    >>> alert = '''<script>alert('hi!')</script>'''
    >>> got_safe = testclient.get('/getx_safe?x='+alert)
    >>> got_safe.get_data(as_text=True) == alert
    True
    >>> got = testclient.get('/getx?x='+alert)
    >>> (got.get_data(as_text=True) == escape(alert) ==
    ... '&lt;script&gt;alert(&#39;hi!&#39;)&lt;/script&gt;')
    True

    """
    url_prefix = url_for('queriesdemo.viewtestcases')[:-len('/testcases')]
    testcases = re_findall_testcases(gettestcases.__doc__)
    testcases = [ url_prefix + testcase for testcase in testcases ]
    unsafecases = []
    for html in [
            """<img src='/static/'>""",
            """<a href='/'>/</a>""",
            """<script>alert('hi')</script>""", ]:
        unsafecases.append(url_prefix + '/getx?x=' + html)
        unsafecases.append(url_prefix + '/getx_safe?x=' + html)
    return testcases,unsafecases


@queriesdemo.route('/testcases')
def viewtestcases():
    testcases, unsafecases = gettestcases()
    table = dict(
        records = [ (href(url),) for url in testcases ],
        headings = ('testcases',))
    table_unsafecases = dict(
        records = [ (href(url),) for url in unsafecases ],
        headings=('unsafe testcases',))
    return render_template(
        'tableview.htm',caption='queriesdemo',
        tables=[table,table_unsafecases])


if __name__ == '__main__':

    import sys
    import doctest

    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.register_blueprint(queriesdemo)
    app.add_url_rule("/",endpoint='queriesdemo.viewtestcases')

    if sys.argv[0] != "":
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(gettestcases.__doc__))
