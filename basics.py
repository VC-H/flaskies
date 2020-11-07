#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.basics
===============

:class:`Flask` app rules table and call stack introspections
------------------------------------------------------------

.. ::
  Copyright: (c) 2017 by Victor Hui.
  Licence: BSD-3-Clause (see LICENSE for more details)

* create a :py:obj:`basics` :class:`Blueprint`

.. code-block:: python

   basics = Blueprint('basics',import_name=__name__)

* Basics of :class:`Flask` application

  - :func:`rulesmap` shows a table of rule map and
    the templates used
  - :func:`stacktables` shows a table of libraries and
    modules of the call stack
  - useful to work with :py:obj:`templateview` :class:`Blueprint`

* re-used:

  - :func:`templateview.view`
  - :func:`templateview.listall`
  - duplicated :func:`hello.href` for :func:`href`

* define two :py:obj:`view_func`'s:

.. literalinclude:: ../basics.py
   :pyobject: rulesmap

.. literalinclude:: ../basics.py
   :pyobject: stacktable

-----
"""

from __future__ import print_function, unicode_literals
import sys, os, re, traceback, inspect
from flask import (
    Flask, Blueprint, render_template, current_app, request, url_for,
    escape, Markup)
from jinja2 import meta


re_sub_rule_variable = re.compile(
    """<[^/]+>[/]*""").sub
re_findall_templates = re.compile(
    """[(\s]render_template\s*\(\s*['"](.+?)['"]""",
    flags=re.DOTALL).findall # apply to inspect.getsource(viewfunction)

def href(url,descr=None):
    """return ``Markup('<a href="{0}">{1}</a>')`` for (`url, descr`);

    >>> assert href("/") == Markup('<a href="/">/</a>')

    """
    if descr is None:
        descr = url
    return Markup('<a href="{0}">{1}</a>'.format(url,escape(descr)))

def getendtemplates():
    """return a :py:obj:`dict` of :data:`[(endpoint,templates),...]`;

    >>> testapp = Flask(__name__)
    >>> with testapp.app_context():
    ...     templatesdict = getendtemplates()
    >>> sorted(templatesdict.items()) == [
    ...     ('static',[])]
    True
    >>> testapp.register_blueprint(basics)
    >>> with testapp.app_context():
    ...     templatesdict = getendtemplates()
    >>> sorted(templatesdict.items()) == [
    ...     ('basics.rulesmap',['tableview.htm']),
    ...     ('basics.stacktable',['tableview.htm']),
    ...     ('static',[])]
    True

    """
    return dict(
        (endpoint,re_findall_templates(inspect.getsource(viewfunction)))
        for endpoint,viewfunction in current_app.view_functions.items())

def getrules():
    """return a :py:obj:`list` of :data:`(methods,rule,endpoint,template)`;

    >>> testapp = Flask(__name__)
    >>> with testapp.app_context():
    ...     table = getrules()
    ...
    >>> sorted(table.keys()) == ['headings','records']
    True
    >>> len(table.get('records'))
    1
    >>> table.get('records')[0] == (
    ...     'GET, HEAD, OPTIONS',
    ...     href('/static/','/static/<path:filename>'),
    ...     'static',
    ...     '')
    True

    """
    templatesdict = getendtemplates()
    rules = []
    for rule in current_app.url_map.iter_rules():
        methods = ", ".join(sorted(rule.methods))
        url = re_sub_rule_variable("",rule.rule)
        href_rule = href(url,descr=rule.rule)
        if 'templateview' not in current_app.blueprints:
            href_templates = Markup(', ').join(
                templatesdict[rule.endpoint])
        else:
            href_templates = Markup(', ').join(
                href(url_for('templateview.view',template=t),descr=t)
                for t in templatesdict[rule.endpoint])
        rules.append((methods,href_rule,rule.endpoint,href_templates))
    return dict(
        records = rules,
        headings = ('methods','url','endpoint','templates'),)

def tracereftemplates(jinja_env,template):
    """return a :py:obj:`list` of all references in `template` recursively;

    >>> testapp = Flask(__name__)
    >>> with testapp.app_context():
    ...     (tracereftemplates(testapp.jinja_env,'base.htm') ==
    ...      tracereftemplates(current_app.jinja_env,'base.htm') ==
    ...      [])
    ...
    True
    >>> with testapp.app_context():
    ...     (tracereftemplates(testapp.jinja_env,'tableview.htm') ==
    ...      tracereftemplates(current_app.jinja_env,'tableview.htm') ==
    ...      ['base.htm'])
    ...
    True

    """
    sourcetuple = jinja_env.loader.get_source(jinja_env,template)
    ast = jinja_env.parse(sourcetuple)
    templates = list(meta.find_referenced_templates(ast))
    for template in set(templates):
        templates.extend(tracereftemplates(jinja_env,template))
    return sorted(list(set(templates)))

def getalltemplates():
    """return a :py:obj:`list` of templates used in :data:`flask.current_app`;

    >>> testapp = Flask(__name__)
    >>> testapp.register_blueprint(basics)
    >>> with testapp.app_context():
    ...     templates = getalltemplates()
    >>> templates == [
    ...     'base.htm',
    ...     'tableview.htm',
    ... ]
    True

    """
    templatesdict = getendtemplates()
    templates = []
    list(map(templates.extend,templatesdict.values()))
    jinja_env = current_app.jinja_env
    for template in set(templates):
        templates.extend(tracereftemplates(jinja_env,template))
    return sorted(list(set(templates)))

def getstack(skip=0,ignorelibdir=False):
    """return the traceback from the caller;

    * the stack table depends on the context of caller.
    * the top stack is :func:`getstack` itself.

    >>> table = getstack()
    >>> sorted(table.keys()) == ['headings','records']
    True
    >>> len(table['records']) > 1
    True
    >>> caller = table['records'][0]
    >>> caller[-1] == Markup(
    ...     'for path,lineno,funcname,source '
    ...     'in traceback.extract_stack():')
    True
    >>> caller[:2] == ('$APP/flaskies.github/basics.py','getstack')
    True

    """
    appdir = os.path.dirname(os.getcwd())
    libdir = os.path.dirname(os.__file__)
    pkgdir = os.path.join(libdir,'site-packages')
    pyver = os.path.basename(libdir)
    vlibdir,vpkgdir = "*","*"
    if sys.base_exec_prefix != sys.exec_prefix:
        vlibdir = os.path.join(sys.exec_prefix,'lib',pyver)
        vpkgdir = os.path.join(sys.exec_prefix,'lib',pyver,'site-packages')
    stack = []
    for path,lineno,funcname,source in traceback.extract_stack():
        if path.startswith(vpkgdir):
            path = '$VSITE' + path[len(vpkgdir):]
        elif path.startswith(vlibdir):
            path = '$VLIB' + path[len(vlibdir):]
        elif path.startswith(pkgdir):
            path = '$SITE' + path[len(pkgdir):]
        elif path.startswith(appdir):
            path = '$APP' + path[len(appdir):]
        elif path.startswith(libdir):
            if ignorelibdir:
                continue
            path = '$LIB' + path[len(libdir):]
        stack.append((path,funcname,lineno,escape(source)))
    stack.reverse()
    return dict(
        records = stack[skip:],
        headings = ('file','function','lineno','source'),)


basics = Blueprint('basics',__name__)

@basics.route('/rulesmap')
def rulesmap():
    return render_template(
        'tableview.htm', caption = 'url_map',
        tables = [getrules(),])

@basics.route('/stacktable')
def stacktable():
    return render_template(
        'tableview.htm', caption = 'stack',
        tables = [getstack(skip=0),])


def create_basics_app():
    """app factory"""
    from templateview import templateview
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.register_blueprint(templateview)
    app.register_blueprint(basics)
    app.add_url_rule("/",endpoint='basics.rulesmap')
    return app


if __name__ == '__main__':

    import sys
    import doctest

    app = create_basics_app()
    if sys.argv[0] != "":
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(os.linesep.join([
            getrules.__doc__,getstack.__doc__])))
