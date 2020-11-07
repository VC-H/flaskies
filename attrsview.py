#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.attrsview
==================

Viewing the `attribute-value` pairs of a python object
------------------------------------------------------

.. ::
  Copyright: (c) 2017 by Victor Hui.
  Licence: BSD-3-Clause (see LICENSE for more details)

* create a :py:obj:`attrsview` :class:`Blueprint`

.. code-block:: python

   attrsview = Blueprint('attrsview',import_name=__name__)

* general functionalities:

  - provide viewing the `attribute-value` pairs in
    a table for a specific python object;
  - capable of viewing the next level of `attribute-value`
    pairs for some attributes;
  - capable of viewing context variable in
    the jinja template environment;

* specically, :py:obj:`attrsview` sets up two views:

.. code-block:: python

   attrsview_routes('current_app',current_app)
   attrsview.add_app_template_global(pancontext)

* re-used:

  - :func:`basics.href`

* definition of the generic view dispatch and routing for any object

.. literalinclude:: ../attrsview.py
   :pyobject: viewattrs

.. literalinclude:: ../attrsview.py
   :pyobject: attrsview_routes

* re-use :py:obj:`viewattrs` as :py:obj:`jinja2.contextfunction` to
  :py:obj:`panout` `context` in the jinja environment

.. literalinclude:: ../attrsview.py
   :pyobject: pancontext

.. literalinclude:: ../attrsview.py
   :pyobject: viewcontext


Some test cases
---------------

>>> testapp = Flask(__name__)
>>> testapp.register_blueprint(attrsview)
>>> testclient = testapp.test_client()

* test response to the request of ``/viewattrs/current_app/blueprints/``

>>> got = testclient.get('/viewattrs/current_app/blueprints/')
>>> blueprints_html = got.get_data(as_text=True)
>>> all(map(blueprints_html.__contains__,[
...     '<caption>current_app/blueprints/</caption>',
...     '<td><a href="attrsview/">attrsview</a></td>',
...     '<td>{}</td>'.format(escape(attrsview.__class__)),
... ]))
True

* test response to the request of ``/viewattrs/context/``
* check the list of context variables
* check :py:obj:`pancontext` is in the list

>>> got = testclient.get('/viewattrs/context/')
>>> context_html = got.get_data(as_text=True)
>>> re.findall('<td>(.*)</td>',context_html)[::2] == [
...     '<a href="config/">config</a>', 'cycler', 'dict',
...     '<a href="g/">g</a>', 'get_flashed_messages',
...     'joiner', 'lipsum', 'namespace', 'pancontext',
...     'range', '<a href="request/">request</a>',
...     '<a href="session/">session</a>',
...     'url_for'
... ]
True

-----
"""

from __future__ import print_function, unicode_literals
from six import string_types
import sys, os, re
from flask import (
    Flask, Blueprint, render_template, current_app,
    render_template_string, escape, Markup)
from jinja2 import contextfunction
from basics import href

Primitives = (string_types,type,bool,int,float,complex)

def panrepr(key,obj):
    """return (:py:obj:`href` (`key`) - :py:obj:`str` (`obj`)) \
    if `obj` is not :py:obj:`Primitives` nor :py:obj:`callable`;

    >>> isinstance(escape("x"),string_types)
    True
    >>> panrepr("","x") == panrepr("",escape("x")) == ("",escape("x"))
    True
    >>> panrepr("",0) == ("",escape(0))
    True
    >>> panrepr("",True) == ("",escape(True))
    True
    >>> panrepr("",(None,)) == (href("/",""),escape(tuple))
    True
    >>> panrepr("",[]) == (href("/",""),escape(list))
    True
    >>> panrepr("",{}) == (href("/",""),escape(dict))
    True
    >>> panrepr("",panrepr) == ("",escape(panrepr))
    True

    """
    key = str(key)
    url = key + "/"
    if isinstance(obj,Primitives) or obj is None:
        return key,escape(obj)
    if isinstance(obj,(tuple,list,dict)):
        return href(url,key),escape(obj.__class__)
    if callable(obj):
        return key,escape(obj)
    if hasattr(obj,'__dict__'):
        return href(url,key),escape(obj.__class__)
    return key,escape(obj)

def panout(obj):
    """return a list of (`attribute,value`)'s of an `obj`; \
    handling (`attribute,value`)'s using :func:`panrepr`;

    >>> panout.__dict__
    {}
    >>> list(panout(panout))
    []
    >>> len(list(panout(Primitives))) == len(Primitives)
    True
    >>> (list(panout(Primitives))[0] ==
    ...     (href("0/","0"),escape(Primitives[0].__class__)) ==
    ...     (href("0/","0"),escape(tuple)))
    True
    >>> list(panout(Primitives[0]))[0] == ("0",escape(string_types[0]))
    True

    """
    if isinstance(obj,dict) or (hasattr(obj,'keys') and hasattr(obj,'get')):
        return (panrepr(key,obj.get(key)) for key in sorted(obj.keys()))
    if isinstance(obj,(tuple,list)):
        return (panrepr(enum,item) for enum,item in enumerate(obj))
    if hasattr(obj,'__dict__'):
        return panout(obj.__dict__)
    return panout(obj.__class__)

def getenditem(obj=None,keypath=""):
    """return the item on the end of `keypath` of `obj`;

    >>> getenditem() == None
    True
    >>> getenditem(attrsview) == attrsview
    True
    >>> getenditem(attrsview,'name/') == 'attrsview'
    True
    >>> getenditem(attrsview,'name/format/') == attrsview.name.format
    True

    """
    if keypath == "":
        return obj
    for key in keypath.split("/")[:-1]:
        if isinstance(obj,dict):
            if key == 'None' and None in obj:
                key = None
            obj = obj[key]
        elif isinstance(obj,(tuple,list)):
            obj = obj[int(key)]
        else:
            obj = getattr(obj,key)
    return obj

def viewattrs(name,obj):
    def dispatch(keypath=""):
        enditem = getenditem(obj,keypath)
        attrs = panout(enditem)
        table = dict(records=attrs,headings=('attribute','value'))
        keypath = name + "/" + keypath
        return render_template(
            'tableview.htm',tables=[table,],caption=keypath)
    return dispatch

def attrsview_routes(name,obj):
    rule = '/viewattrs/' + name + "/"
    route = dict(endpoint=name,view_func=viewattrs(name,obj))
    attrsview.add_url_rule(rule+'<path:keypath>',**route)
    attrsview.add_url_rule(rule,**route)

@contextfunction
def pancontext(context,keypath=""):
    obj = dict(context.items())
    view_func = viewattrs('context',obj)
    return view_func(keypath)

attrsview = Blueprint('attrsview',__name__)
attrsview_routes('current_app',current_app)
attrsview.add_app_template_global(pancontext)

@attrsview.route('/viewattrs/context/')
@attrsview.route('/viewattrs/context/<path:keypath>')
def viewcontext(keypath=""):
    context = 'pancontext(keypath="{}")|safe'.format(keypath)
    return render_template_string('{{ ' + context + '}}')


def create_attrsview_app():
    """app factory"""
    from basics import basics
    from templateview import templateview
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    attrsview_routes('Primitives',Primitives)
    app.register_blueprint(attrsview)
    app.register_blueprint(templateview)
    app.register_blueprint(basics)
    app.add_url_rule("/",endpoint='basics.rulesmap')
    return app


if __name__ == '__main__':

    import sys
    import doctest

    app = create_attrsview_app()
    if sys.argv[0] != "":
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(__doc__))
