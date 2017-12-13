#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.hello
==============

``'hello world'`` examples
--------------------------

.. ::
  Copyright: (c) 2017 by Victor Hui.
  Licence: BSD-3-Clause (see LICENSE for more details)

* test running:

  - ``GET`` method of :meth:`flask.request`
  - :meth:`flask.escape`
  - :meth:`flask.Markup`
  - :meth:`Flask.testclient`
  - :meth:`flask.render_template`

* create a :py:obj:`hello` :class:`Blueprint`

.. code-block:: python

   hello = Blueprint('hello',import_name=__name__)

* define three :py:obj:`view_func`'s:

.. literalinclude:: ../hello.py
   :pyobject: say

.. literalinclude:: ../hello.py
   :pyobject: say_escaped

.. literalinclude:: ../hello.py
   :pyobject: viewtestcases


-----
"""

from __future__ import unicode_literals
import sys, re
from flask import (
    Flask, Blueprint, render_template, url_for,
    escape, Markup)

hello = Blueprint('hello',import_name=__name__)

@hello.route('/hello')
@hello.route('/hello/<friends>')
def say(friends='world'):
    return 'hello {}!'.format(friends)

@hello.route('/Hello')
@hello.route('/Hello/<friends>')
def say_escaped(friends='World'):
    return 'Hello {}!'.format(escape(friends))

re_findall_testcases = re.compile(
    """>>> got.* = testclient.get\('(.*)'\)"""
    ).findall

def href(url,descr=None):
    """return ``Markup('<a href="{0}">{1}</a>')`` for (`url, descr`);

    >>> assert href("/") == Markup('<a href="/">/</a>')

    """
    if descr is None:
        descr = url
    return Markup('<a href="{0}">{1}</a>'.format(url,escape(descr)))

def gettestcases():
    """return testcases used here in the doctest;

    >>> testapp = Flask(__name__)
    >>> testapp.register_blueprint(hello)
    >>> testclient = testapp.test_client()

    >>> with testapp.test_request_context():
    ...     testcases = gettestcases()
    >>> testcases == [
    ...     '/hello',
    ...     '/hello/there',
    ...     '/hello/<friends>',
    ...     '/Hello/<friends>'
    ... ]
    True

    * basic tests:

    >>> got = testclient.get('/hello')
    >>> assert got.status == '200 OK'
    >>> assert got.get_data(as_text=True) == 'hello world!'

    >>> got = testclient.get('/hello/there')
    >>> assert got.status == '200 OK'
    >>> assert got.get_data(as_text=True) == 'hello there!'

    * ``/hello``/`<friends>` does not take trailing slash,

    >>> testclient.get('/hello/')
    <Response streamed [404 NOT FOUND]>

    * :meth:`escape` and not, rules are *case sensitive*!

    >>> got = testclient.get('/hello/<friends>')
    >>> assert got.status == '200 OK'
    >>> assert got.get_data(as_text=True) == 'hello <friends>!'

    >>> got = testclient.get('/Hello/<friends>')
    >>> assert got.status == '200 OK'
    >>> assert got.get_data(as_text=True) == 'Hello &lt;friends&gt;!'

    * :meth:`escape` and :meth:`Markup`:

    >>> (escape('<em>escaped</em>') ==
    ...  Markup(u'&lt;em&gt;escaped&lt;/em&gt;') ==
    ...  escape(Markup(u'&lt;em&gt;escaped&lt;/em&gt;')))
    True

    >>> (escape(Markup('<em>escaped</em>')) ==
    ...  Markup(Markup('<em>escaped</em>')) ==
    ...  Markup('<em>escaped</em>'))
    True

    """
    url_prefix = url_for('hello.viewtestcases')[:-len('/testcases')]
    testcases= re_findall_testcases(gettestcases.__doc__)
    return [ url_prefix + testcase for testcase in testcases ]


@hello.route('/testcases')
def viewtestcases():
    hrefs = [ (href(url),) for url in gettestcases() ]
    return render_template(
        'tableview.htm',caption='hello',
        tables=[dict(records=hrefs,headings=('testcases',)),])


if __name__ == '__main__':

    import sys
    import doctest

    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.register_blueprint(hello)
    app.add_url_rule("/",endpoint='hello.viewtestcases')

    if sys.argv[0] != "":
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(gettestcases.__doc__))
