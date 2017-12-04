#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.hello
--------------

The traditional ``'hello world'`` with slightly different aims

* setting up test cases using :meth:`flask.app.testclient`;
* test out :meth:`flask.escape` and :meth:`flask.Markup`;

:Copyright: © 2017 by Victor Hui.
:Licence: BSD-3-Clause (see LICENSE for more details)

-----
"""

from __future__ import unicode_literals
from flask import Flask,Blueprint,Markup,escape

hello = Blueprint('hello',import_name=__name__)

@hello.route('/hello')
@hello.route('/hello/<friends>')
def say(friends='world'):
    "``/hello``/`<friends>` for direct pass of `friends` to ``'hello {}!'``"
    return 'hello {}!'.format(friends)

@hello.route('/Hello')
@hello.route('/Hello/<friends>')
def say_escaped(friends='World'):
    "``/Hello``/`<friends>` for escaped pass of `friends` to ``'Hello {}!'``"
    return 'Hello {}!'.format(escape(friends))


def create_app_hello():
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


    """
    app = Flask(__name__)
    app.register_blueprint(hello)
    return app


if __name__ == '__main__':

    import sys
    import doctest

    if sys.argv[0] != "":
        app = create_app_hello()
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(create_app_hello.__doc__))
