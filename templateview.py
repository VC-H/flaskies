#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.templateview
=====================

Test the templates used in flaskies
-----------------------------------

.. ::
  Copyright: (c) 2017 by Victor Hui.
  Licence: BSD-3-Clause (see LICENSE for more details)

* create a :py:obj:`templateview` :class:`Blueprint`

  - useful to work with :py:obj:`basics` :class:`Blueprint`

.. code-block:: python

   templateview = Blueprint('templateview',import_name=__name__)

* re-used:

  - :func:`basics.getalltemplates`
  - :func:`basics.href`

* define two :py:obj:`view_func`'s:

.. literalinclude:: ../templateview.py
   :pyobject: view

.. literalinclude:: ../templateview.py
   :pyobject: listall


show cases
----------

>>> testapp = Flask(__name__)

* raw html outputs of the templates with no context supplied:

>>> with testapp.app_context():
...     base_htm = render_template('base.htm')
...     templateview_htm = render_template('templateview.htm')
...     tableview_htm = render_template('tableview.htm')
...

>>> base_htm == '''<!DOCTYPE html>
... <html lang="en">
... <head>
...   <meta charset="utf-8">
... </head>
... <body>
... </body>
... </html>'''
True

>>> templateview_htm == '''<!DOCTYPE html>
... <html lang="en">
... <head>
...   <meta charset="utf-8">
...   <link rel="stylesheet" href="/static/css/basic.css"></link>
...   <link rel="stylesheet" href="/static/css/source.css"></link>
... </head>
... <body>
... <figure>
... <figurecaption></figurecaption>
... </figure>
... </body>
... </html>'''
True

>>> tableview_htm == '''<!DOCTYPE html>
... <html lang="en">
... <head>
...   <meta charset="utf-8">
...   <link rel="stylesheet" href="/static/css/basic.css"></link>
... </head>
... <body>
... <table>
...   <caption></caption>
... </table>
... </body>
... </html>'''
True

* ``templateview.htm`` usage: (*note*: ``{{source|safe}}``)

>>> with testapp.app_context():
...     templateview_htm_1 = render_template(
...         'templateview.htm',source='<script>alert("hi")</script>')
>>> templateview_htm_1 == '''<!DOCTYPE html>
... <html lang="en">
... <head>
...   <meta charset="utf-8">
...   <link rel="stylesheet" href="/static/css/basic.css"></link>
...   <link rel="stylesheet" href="/static/css/source.css"></link>
... </head>
... <body>
... <figure>
... <figurecaption></figurecaption>
... <script>alert("hi")</script>
... </figure>
... </body>
... </html>'''
True

* ``tableview.htm`` usage:

>>> cells = [
...     ('cell-00','cell-01','cell-02'),
...     ('cell-01','cell-11','cell-12'),
...     ('cell-02','cell-21','cell-22'),
... ]
>>> headings = ('column-0','column-1','column-2')
>>>
>>> with testapp.app_context():
...     tableview_htm_1 = render_template(
...         'tableview.htm',caption='a table',
...         tables=[dict(records=cells,headings=headings),])
...
>>> tableview_htm_1 == '''<!DOCTYPE html>
... <html lang="en">
... <head>
...   <meta charset="utf-8">
...   <link rel="stylesheet" href="/static/css/basic.css"></link>
... </head>
... <body>
... <table>
...   <caption>a table</caption>
...   <thead>
...     <tr>
...       <th>column-0</th>
...       <th>column-1</th>
...       <th>column-2</th>
...     </tr>
...   </thead>
...   <tbody>
...     <tr>
...       <td>cell-00</td>
...       <td>cell-01</td>
...       <td>cell-02</td>
...     </tr>
...     <tr>
...       <td>cell-01</td>
...       <td>cell-11</td>
...       <td>cell-12</td>
...     </tr>
...     <tr>
...       <td>cell-02</td>
...       <td>cell-21</td>
...       <td>cell-22</td>
...     </tr>
...   </tbody>
... </table>
... </body>
... </html>'''
True

"""

from __future__ import print_function, unicode_literals
import sys, os
from pygments import highlight
from pygments.lexers import HtmlLexer
from pygments.formatters import HtmlFormatter
from flask import (
    Flask, Blueprint, render_template,
    current_app, request, url_for,
    Markup)
from basics import getalltemplates, href

lexer = HtmlLexer()
formatter = HtmlFormatter(cssclass='source')
templateview = Blueprint('templateview',__name__)

@templateview.route('/templates')
def listall():
    hrefs = [
        (href(url_for('.view',template=t),t),)
        for t in getalltemplates() ]
    return render_template(
        'tableview.htm',caption='templates',
        tables=[dict(records=hrefs),])

@templateview.route('/view/<template>')
def view(template='base.htm'):
    args = request.args.to_dict()
    html = render_template(template,**args)
    # show = '<caption>{}</caption>\n'.format(template)
    show = highlight(html,lexer,formatter)
    return render_template(
        'templateview.htm',source=show.strip(),template=template)


if __name__ == '__main__':

    import sys
    import doctest

    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.register_blueprint(templateview)
    app.add_url_rule("/",endpoint='templateview.listall')

    if sys.argv[0] != "":
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(__doc__))
