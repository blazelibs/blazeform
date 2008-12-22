"""
Introduction
---------------

pysform is a library designed to facilitate the rendering/processing/validating
of HTML forms.

Features
---------------
- validation based on FormEncode
- attempting to have complete HTML spec coverage
- extensible rendering system() (don't have to use it)
- will work with multiple WSGI frameworks (Werkzeug currently supported)
- *extensive* unit tests
- few dependencies: FormEncode, pysutils, WebHelpers

Code Sample
--------------------

Using it might look like this::

    class MyForm(Form):
        def __init__(self):
            Form.__init__(self, 'myform')
            
            el = self.add_header('input-els', 'Optional Elements')
            el = self.add_button('button', 'Button', defaultval='PushMe')
            el = self.add_checkbox('checkbox', 'Checkbox')
            el = self.add_file('file', 'File')
            el = self.add_hidden('hidden', defaultval='my hidden val')
            el = self.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
            el = self.add_text('text', 'Text')
            el.add_note('a note')
            el.add_note('an <strong>HTML</strong> note', False)
            el = self.add_text('nolabel', defaultval='No Label')
            el.add_note('a note')
            el = self.add_password('password', 'Password')
            el = self.add_confirm('confirm', 'Confirm Password', match='password')
            el.add_note('confirm characters for password field are automatically masked')
            el = self.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
            el.add_note('note the automatic conversion from datetime object')
            emel = self.add_email('email', 'Email')
            el = self.add_confirm('confirmeml', 'Confirm Email', match=emel)
            el.add_note('note you can confirm with the name of the field or the element object')
            el.add_note('when not confirming password field, characters are not masked')
            el = self.add_time('time', 'Time')
            el = self.add_url('url', 'URL')
            options = [('1', 'one'), ('2','two')]
            el = self.add_select('select', options, 'Select')
            el = self.add_mselect('mselect', options, 'Multi Select')
            el = self.add_textarea('textarea', 'Text Area')
            el = self.add_fixed('fixed', 'Fixed', 'fixed val')
            el = self.add_fixed('fixed-no-label', defaultval = 'fixed no label')
            el = self.add_static('static', 'Static', 'static val')
            el = self.add_static('static-no-label', defaultval='static val no label')

and the view/controller code might look something like::

    class FormTest(HtmlTemplatePage):
        def prep(self):
            self.form = MyForm()
            
        def post(self):
            if self.form.is_cancel():
                self.assign('cancel', True)
            elif self.form.is_valid():
                self.assign('values', self.form.get_values())
            elif self.form.is_submitted():
                # form was submitted, but invalid
                self.form.assign_user_errors()
            self.default()
        
        def default(self):
            self.assign('form', self.form)

Example Application:
----------------------

See below in the file downloads for an example application demonstrating how
to use pysform.  There are a lot of dependencies b/c its based on
`pysapp <http://pypi.python.org/pypi/pysapp/>`_ so I suggest you use virtualenv.

Steps to get it running should be:

#. download .zip package
#. unzip
#. `cd pysform-example-0.1dev`
#. `python setup.py develop`
#. `cd myapp`
#. `pysmvt serve dev`
#. browse to http://localhost:5000/formtest

The example application is very unpolished and may contain bugs.  Its just a
very rough first draft.  The pysform code was engineered much more thoughtfully
:).

Current Status
---------------

We are in an early beta stage.  API should be relatively stable, but backwards
compatibility won't be guaranteed for a while. 

The somewhat stable `development version
<https://svn.rcslocal.com:8443/svn/pysmvt/pysform/trunk#egg=pysform-dev>`_.
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = "pysform",
    version = "0.1dev",
    description = "A library for generating and validating HTML forms",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://pypi.python.org/pypi/pysform',
    license='BSD',
    packages=['pysform'],
    install_requires = [
        "FormEncode>=1.2",
        "pysutils>=dev",
        "WebHelpers>=0.6.4"
    ],
    zip_safe=False
)