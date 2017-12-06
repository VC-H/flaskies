#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.hello
==============

:Copyright: © 2017 by Victor Hui.
:Licence: BSD-3-Clause (see LICENSE for more details)

``'hello world'`` with :meth:`flask.escape` and :meth:`flask.Markup`
--------------------------------------------------------------------

* create a :class:`Flask.Blueprint` :py:obj:`hello`

.. code-block:: python

   hello = Blueprint('hello',import_name=__name__)

* define two :py:obj:`view_func`'s:

.. literalinclude:: ../hello.py
   :pyobject: say

.. literalinclude:: ../hello.py
   :pyobject: say_escaped

* setting up test cases using :meth:`flask.app.testclient`;

-----
"""

from __future__ import unicode_literals
import sys, re
from flask import Flask, Blueprint, Markup, escape

hello = Blueprint('hello',import_name=__name__)

@hello.route('/hello')
@hello.route('/hello/<friends>')
def say(friends='world'):
    return 'hello {}!'.format(friends)

@hello.route('/Hello')
@hello.route('/Hello/<friends>')
def say_escaped(friends='World'):
    return 'Hello {}!'.format(escape(friends))


def create_app_hello(app=None):
    """return the ``app`` registered with the ``hello blueprint``

    >>> app = create_app_hello()
    >>> testclient = app.test_client()

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

    >>> (re_findall_testcases(create_app_hello.__doc__) ==
    ... ['/hello', '/hello/there', '/hello/<friends>', '/Hello/<friends>'])
    True

    """
    if app is None:
        app = Flask(__name__)
    app.register_blueprint(hello)
    return app

re_findall_testcases = re.compile(
    """>>> got.* = testclient.get\('(.*)'\)"""
    ).findall



if __name__ == '__main__':

    import sys
    import doctest

    if sys.argv[0] != "":
        app = create_app_hello()
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(create_app_hello.__doc__))
