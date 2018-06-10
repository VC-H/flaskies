#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

flaskies.cookiesman: Cookies Manager
====================================

* A :class:`Blueprint` to manage cookies using ``wtforms``.

.. code-block:: python

   cookiesman = Blueprint('cookiesman',import_name=__name__)

* :py:obj:`cookiesman` has one view only

.. literalinclude:: ../cookiesman.py
   :pyobject: viewcookies

* :class:`CookiesManForm` creates the form for :py:obj:`viewcookies`.
  The form is built dynamically from the cookies of the current sesssion.

.. code-block:: python

   class CookiesManForm(FlaskForm):

.. literalinclude:: ../cookiesman.py
   :pyobject: CookiesManForm.dynbuild

* where :class:`CookieForm` builds input entries for the modification and
  removal of current cookie, and :class:`NewCookieForm` builds an input
  form for the setting of a new cookie. The boolean entry :py:obj:`http`
  sets cookies ``HttpOnly``.  :class:`CookiesManForm` is a nested form
  composed of :class:`CookieForm` and :class:`NewCookieForm`.

.. literalinclude:: ../cookiesman.py
   :pyobject: CookieForm

.. literalinclude:: ../cookiesman.py
   :pyobject: NewCookieForm


Tests
-----

* setting up the tests with CSRF

>>> from flask_wtf.csrf import generate_csrf
>>> testapp = Flask(__name__)
>>> testapp.testing = testapp.config['TESTING'] = True
>>> testapp.secret_key = testapp.config['SECRET_KEY'] = 'secret'
>>> csrf = CSRFProtect(testapp)
>>> testapp.register_blueprint(cookiesman)

* create a client

>>> client = testapp.test_client()
>>> client.cookie_jar
<_TestCookieJar[]>

* verify setting a session cookie on first request

>>> client.get('/cookiesview')
<Response streamed [200 OK]>
>>> cookies = list(client.cookie_jar)
>>> assert len(cookies) == 1
>>> sessioncookie = cookies[0]
>>> assert sessioncookie.name == 'session'
>>> assert sessioncookie.value != ""
>>> assert sessioncookie.domain == 'localhost.local'
>>> assert sessioncookie.path == '/'

* verify persistence of the session cookie on the client;

>>> with testapp.app_context():
...     # inside a request context
...     client.get('/cookiesview')
...     list(client.cookie_jar) == cookies
<Response streamed [200 OK]>
True

* verify another client has a different session cookie

>>> with testapp.test_client() as client2:
...     client2.get('/cookiesview')
...     cookies2 = list(client2.cookie_jar)
...     assert len(cookies2) == 1
...     assert cookies2[0].name == 'session'
...     assert cookies2[0].value != sessioncookie.value
<Response streamed [200 OK]>

* define an emulation of :meth:`CookiesManForm.dynbuild` for the tests

>>> def dynbuild(cookies):
...     # require request context
...     data = dict(csrf_token=generate_csrf())
...     for cookie in cookies:
...         key = md5(cookie.name).hexdigest()
...         data[key + '-name'] = cookie.name
...         data[key + '-value'] = cookie.value
...         data[key + '-http'] = 'HttpOnly' in cookie._rest
...     return data

* add a cookie

>>> with testapp.app_context():
...     client.get('/cookiesview')
...     data = dynbuild(client.cookie_jar)
...     data.update({'new-name':"a",'new-value':"b",'new-http':None})
...     client.post('/cookiesview',data=data,follow_redirects=True)
<Response streamed [200 OK]>
<Response streamed [200 OK]>

>>> cookies = list(client.cookie_jar)
>>> len(cookies)
2
>>> str(cookies[1]) == str(sessioncookie)
True
>>> assert cookies[0].name == "a"
>>> assert cookies[0].value == "b"
>>> 'HttpOnly' in cookies[0]._rest
False

* modifiy the value of cookie "a"

>>> with testapp.app_context():
...     client.get('/cookiesview')
...     data = dynbuild(client.cookie_jar)
...     key = md5("a").hexdigest()
...     data[key + '-value'] = "b+"
...     data[key + '-http'] = True
...     client.post('/cookiesview',data=data,follow_redirects=True)
<Response streamed [200 OK]>
<Response streamed [200 OK]>

>>> cookies = list(client.cookie_jar)
>>> len(cookies)
2
>>> str(cookies[1]) == str(sessioncookie)
True
>>> assert cookies[0].name == "a"
>>> assert cookies[0].value == "b+"
>>> 'HttpOnly' in cookies[0]._rest
True

* remove a cookie

>>> with testapp.app_context():
...     client.get('/cookiesview')
...     data = dynbuild(client.cookie_jar)
...     key = md5("a").hexdigest()
...     data[key + '-value'] = ""
...     client.post('/cookiesview',data=data,follow_redirects=True)
<Response streamed [200 OK]>
<Response streamed [200 OK]>

>>> cookies = list(client.cookie_jar)
>>> len(cookies)
1
>>> str(cookies[0]) == str(sessioncookie)
True

"""


import sys
from flask import (
    Flask, Blueprint, request, make_response, render_template,
    url_for, redirect )
from wtforms import StringField, BooleanField, FormField, Form
from flask_wtf import FlaskForm, CSRFProtect
from jinja2 import Template
from hashlib import md5


class CookieForm(Form):
    value = StringField('value')
    http = BooleanField('http')

class NewCookieForm(CookieForm):
    name = StringField('name',default="")

class CookiesManForm(FlaskForm):

    @staticmethod
    def dynbuild(request):
        class DynCookiesManForm(CookiesManForm):
            new = FormField(NewCookieForm)
        for name,value in request.cookies.items():
            key = md5(name).hexdigest()
            default = dict(value=value,http=False)
            formfield = FormField(CookieForm,label=name,default=default)
            setattr(DynCookiesManForm,key,formfield)
        return DynCookiesManForm(request.form)

    def set_newcookie(self,response):
        newcookie = self.data.get('new')
        name = newcookie.get('name',"")
        if name != "" and not name.isspace():
            value = newcookie.get('value',"")
            if value != "" and not value.isspace():
                http = newcookie.get('http')
                response.set_cookie(name,value,httponly=http)

    def update_cookies(self,request,response):
        for name,value in request.cookies.items():
            key = md5(name).hexdigest()
            formfield = self.data.get(key)
            formvalue = formfield.get('value',"")
            if formvalue == "" or formvalue.isspace():
                response.set_cookie(name,"",expires=0)  # remove
                continue
            formhttp = formfield.get('http')
            response.set_cookie(name,formvalue,httponly=formhttp)

    def set_cookies(self,request,response):
        self.update_cookies(request,response)
        self.set_newcookie(response)


cookiesman = Blueprint('cookiesman',import_name=__name__)

@cookiesman.route('/cookiesview',methods=['GET','POST'])
def viewcookies():
    # print('')
    # print('request.cookies:',request.cookies)
    cookiesform = CookiesManForm.dynbuild(request)
    # print('cookiesman.data:',cookiesform.data)
    if request.method == 'POST' and cookiesform.validate():
        # print('post:cookiesman.data:',cookiesform.data)
        response = make_response(redirect(url_for('cookiesman.viewcookies')))
        cookiesform.set_cookies(request,response)
        return response
    return render_template('cookiesview.htm',form=cookiesform)


def create_cookiesman_app(csrfprotect=True,secret='hello!'):
    """app factory"""
    from basics import basics
    from attrsview import attrsview
    from templateview import templateview
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.secret_key = app.config['SECRET_KEY'] = secret
    app.csrf = CSRFProtect(app)
    app.register_blueprint(cookiesman)
    app.register_blueprint(attrsview)
    app.register_blueprint(templateview)
    app.register_blueprint(basics)
    app.add_url_rule("/",endpoint='basics.rulesmap')
    return app


if __name__ == '__main__':

    import sys
    import doctest

    app = create_cookiesman_app()
    if sys.argv[0] != "":
        app.run(debug=True,use_reloader=True)
    else:
        print(doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
        exec(doctest.script_from_examples(__doc__))
