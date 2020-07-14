import datetime
import decimal
import unittest

from formencode.validators import Int, MaxLength
from webhelpers2.html import literal

from blazeform.form import Form
from blazeform.exceptions import ValueInvalid, ProgrammingError
from blazeform.file_upload_translators import BaseTranslator
from blazeform.util import NotGiven, NotGivenIter

L = literal


class CommonTest(unittest.TestCase):

    def test_render(self):
        html = '<input class="text" id="f-username" name="username" type="text" />'
        form = Form('f')
        el = form.add_text('username', 'User Name')
        self.assertEqual(html, str(form.elements.username.render()))
        self.assertEqual(el.label.render(), L('<label for="f-username">User Name</label>'))

    def test_implicit_render(self):
        html = '<input class="text" id="f-username" name="username" type="text" />'
        form = Form('f')
        form.add_text('username', 'User Name')
        self.assertEqual(html, str(form.elements.username()))

    def test_attr_render(self):
        html = '<input baz="bar" class="text foo bar" id="f-username" name="username" ' \
            'type="text" />'
        form = Form('f')
        form.add_text('username', 'User Name')
        self.assertEqual(html, str(form.elements.username(class_='text foo bar', baz='bar')))

    def test_text_with_default(self):
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_text('username', 'User Name', defaultval='bar')
        self.assertEqual(html, str(form.elements.username.render()))

    def test_text_with_default2(self):
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_defaults({'username': 'bar'})
        self.assertEqual(html, str(form.elements.username.render()))

    def test_text_submit(self):
        # make sure the submit value shows up in the form
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_submitted({'f-submit-flag': 'submitted', 'username': 'bar'})
        self.assertEqual(html, str(form.elements.username.render()))

    def test_text_with_zero_default(self):
        html = '<input class="text" id="f-username" name="username" type="text" value="0" />'
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_defaults({'username': 0})
        self.assertEqual(html, str(form.elements.username.render()))

    def test_submit_default(self):
        # submitted should take precidence over default
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_defaults({'username': 'foo'})
        form.set_submitted({'f-submit-flag': 'submitted', 'username': 'bar'})
        self.assertEqual(html, str(form.elements.username.render()))

    def test_default_value(self):
        # default values do not show up in .value, they only show up when
        # rendering
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_defaults({'username': 'foo'})
        assert form.elements.username.value is NotGiven

    def test_submitted_value(self):
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_defaults({'username': 'foo'})
        form.set_submitted({'f-submit-flag': 'submitted', 'username': 'bar'})
        self.assertEqual('bar', form.elements.username.value)

    def test_notgiven(self):
        # make sure the value we get really is NotGiven
        f = Form('f')
        el = f.add_text('f', 'f')
        assert el.value is NotGiven

        # default shouldn't affect this
        f = Form('f')
        el = f.add_text('f', 'f', defaultval='test')
        assert el.value is NotGiven

    def test_if_missing(self):
        f = Form('f')
        el = f.add_text('f', 'f', if_missing='foo')
        assert el.value == 'foo', el.value

        # doesn't affect anything if the field is submitted
        f = Form('f')
        el = f.add_text('f', 'f', if_missing='foo')
        el.submittedval = None
        assert el.value is None

    def test_if_empty(self):
        # if empty works like if_missing when the field isn't submitted
        f = Form('f')
        el = f.add_text('f', 'f', if_empty='foo')
        assert el.value == 'foo'

        # if_empty also covers empty submit values
        f = Form('f')
        el = f.add_text('f', 'f', if_empty='foo')
        el.submittedval = None
        assert el.value == 'foo'

        # an "empty" if_empty should not get converted to None
        f = Form('f')
        el = f.add_text('f', 'f', if_empty='')
        assert el.value == ''

        # same as previous, but making sure a submitted empty value doesn't
        # change it
        f = Form('f')
        el = f.add_text('f', 'f', if_empty='')
        el.submittedval = None
        assert el.value == ''

    def test_strip(self):
        # strip is on by default
        el = Form('f').add_text('f', 'f')
        el.submittedval = '   '
        assert el.value is None

        # turn strip off
        el = Form('f').add_text('f', 'f', strip=False)
        el.submittedval = '   '
        assert el.value == '   '

        # strip happens before if_empty
        el = Form('f').add_text('f', 'f', if_empty='test')
        el.submittedval = '   '
        assert el.value == 'test'

    def test_invalid(self):
        el = Form('f').add_text('f', 'f', required=True)
        el.submittedval = None
        assert el.is_valid() is False

        el = Form('f').add_text('f', 'f', required=True, if_invalid='foo')
        el.submittedval = None
        self.assertEqual(el.value, 'foo')

    def test_blank_submit_value(self):
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_submitted({'username': ''})
        self.assertEqual(None, form.elements.username.value)

        form = Form('f')
        form.add_text('username', 'User Name', if_empty='')
        form.set_submitted({'username': ''})
        self.assertEqual('', form.elements.username.value)

    def test_is_submitted(self):
        form = Form('f')
        form.add_text('username', 'User Name')
        form.set_defaults({'username': 'foo'})
        self.assertEqual(False, form.elements.username.is_submitted())

        form.set_submitted({'f-submit-flag': 'submitted', 'username': ''})
        self.assertEqual(True, form.elements.username.is_submitted())

    def test_required(self):
        form = Form('f')
        el = form.add_text('username', 'User Name', required=True)
        self.assertEqual(True, el.required)
        self.assertEqual(False, form.elements.username.is_valid())

        # check error message
        self.assertEqual('field is required', el.errors[0])

        # setting submitted should reset _valid to None, which causes the
        # processing to happen again
        self.assertEqual(False, form.elements.username._valid)
        el.submittedval = ''
        self.assertEqual(None, form.elements.username._valid)

        el.submittedval = 'foo'
        self.assertEqual(True, form.elements.username.is_valid())

        # error message without label sould default to element id
        form = Form('f')
        el = form.add_text('username', required=True)
        self.assertEqual(False, form.elements.username.is_valid())
        self.assertEqual('field is required', el.errors[0])

    def test_invalid_value(self):
        form = Form('f')
        el = form.add_text('username', 'User Name', required=True)
        try:
            el.value
            self.fail('expected exception when trying to use .value when element is invalid')
        except Exception as e:
            if str(e) != '"value" attribute accessed, but element "User Name" is invalid':
                raise

        el.submittedval = ''
        try:
            el.value
            self.fail('expected exception when trying to use .value when element is invalid')
        except Exception as e:
            if str(e) != '"value" attribute accessed, but element "User Name" is invalid':
                raise

        el.submittedval = None
        try:
            el.value
            self.fail('expected exception when trying to use .value when element is invalid')
        except Exception as e:
            if str(e) != '"value" attribute accessed, but element "User Name" is invalid':
                raise

        el.submittedval = '0'
        self.assertEqual('0', el.value)

        el.submittedval = 0
        self.assertEqual(0, el.value)

        el.submittedval = False
        self.assertEqual(False, el.value)

    def test_double_processing(self):
        class validator(object):
            vcalled = 0

            def __call__(self, value):
                self.vcalled += 1
                return value

        v = validator()
        form = Form('f')
        el = form.add_text('username', 'User Name', if_empty='bar')
        el.add_processor(v)
        self.assertEqual(True, form.elements.username.is_valid())
        self.assertEqual(1, v.vcalled)
        self.assertEqual(True, form.elements.username.is_valid())
        self.assertEqual(1, v.vcalled)
        self.assertEqual('bar', form.elements.username.value)
        self.assertEqual(1, v.vcalled)
        self.assertEqual('bar', form.elements.username.value)
        self.assertEqual(1, v.vcalled)

        # setting submitted should reset _valid to None, which causes the
        # processing to happen again.  Make sure we don't use an empty value
        # b/c formencode seems to cache the results and our validator's method
        # won't be called again
        el.submittedval = 'foo'
        self.assertEqual('foo', form.elements.username.value)
        self.assertEqual(2, v.vcalled)

    def test_processor_fe_class(self):
        form = Form('f')
        el = form.add_text('units', 'Units')
        el.add_processor(Int)
        assert isinstance(el.processors[0][0], Int)

    def test_processor_fe_instance(self):
        form = Form('f')
        el = form.add_text('units', 'Units')
        el.add_processor(Int())
        assert isinstance(el.processors[0][0], Int)

    def test_error_messages(self):
        form = Form('f')
        el = form.add_text('username', 'User Name', required=True)
        self.assertEqual(False, form.elements.username.is_valid())
        self.assertEqual(len(el.errors), 1)
        self.assertEqual('field is required', el.errors[0])

        # formencode message
        form = Form('f')
        el = form.add_text('field', 'Field', if_empty='test')
        el.add_processor(Int)
        self.assertEqual(False, el.is_valid())
        self.assertEqual(len(el.errors), 1)
        self.assertEqual('Please enter an integer value', el.errors[0])

        # custom message
        form = Form('f')
        el = form.add_text('field', 'Field', if_empty='test')
        el.add_processor(Int, 'int required')
        self.assertEqual(False, el.is_valid())
        self.assertEqual(len(el.errors), 1)
        self.assertEqual('int required', el.errors[0])

        # errors should be reset on submission
        el.submittedval = 'five'
        self.assertEqual(False, el.is_valid())
        self.assertEqual(len(el.errors), 1)

        el.submittedval = 5
        self.assertEqual(True, el.is_valid())
        self.assertEqual(len(el.errors), 0)

    def test_notes(self):
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_note('test note')
        self.assertEqual(el.notes[0], 'test note')

    def test_handlers(self):
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('text exception', 'test error msg')
        assert el.handle_exception(Exception('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')

        # make sure second exception works too
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('not it', '')
        el.add_handler('text exception', 'test error msg')
        assert el.handle_exception(Exception('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')

        # specifying exception type
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('text exception', 'test error msg', Exception)
        assert el.handle_exception(Exception('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')

        # specifying exception type only
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler(exc_type=TypeError)
        assert el.handle_exception(TypeError('text exception'))
        self.assertEqual(el.errors[0], 'text exception')

        # specifying exception type only
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler(exc_type=TypeError, error_msg='wrong type')
        assert el.handle_exception(TypeError('text exception'))
        self.assertEqual(el.errors[0], 'wrong type')

        # error message not specified gets exception text
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('text exception')
        assert el.handle_exception(Exception('text exception user message'))
        self.assertEqual(el.errors[0], 'text exception user message')

        # specifying exception's class string
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('text exception', 'test error msg', 'TypeError')
        assert el.handle_exception(TypeError('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')

        # right message, wrong type
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('text exception', 'test error msg', ValueError)
        assert not el.handle_exception(Exception('text exception'))
        self.assertEqual(len(el.errors), 0)

        # wrong message
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('text exception', 'test error msg', Exception)
        assert not el.handle_exception(Exception('text'))
        self.assertEqual(len(el.errors), 0)

        # callback
        def can_handle(exc):
            if 'can_handle' in str(exc):
                return True
            return False

        # callback that handles
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler(callback=can_handle, error_msg='invalid value')
        assert el.handle_exception(Exception('can_handle'))
        self.assertEqual(el.errors[0], 'invalid value')

        # callback that doesn't
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler(callback=can_handle, error_msg='invalid value')
        assert not el.handle_exception(Exception('cant_handle'))
        self.assertEqual(len(el.errors), 0)

    def test_conversion(self):
        # without form submission, we get empty value
        form = Form('f')
        el = form.add_text('field', 'Field', 'bool')
        assert el.value is NotGiven

        # default values do not get processed, they are for display only
        form = Form('f')
        el = form.add_text('field', 'Field', 'bool', '1')
        assert el.value is NotGiven

        # submission gets converted
        form = Form('f')
        el = form.add_text('field', 'Field', 'bool')
        el.submittedval = '1'
        self.assertEqual(el.value, True)

        # conversion turned off
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.submittedval = '1'
        self.assertEqual(el.value, '1')

        # conversion with if_empty
        form = Form('f')
        el = form.add_text('field', 'Field', 'bool', if_empty=False)
        el.submittedval = '1'
        self.assertEqual(el.value, True)

        # conversion with if_empty
        form = Form('f')
        el = form.add_text('field', 'Field', 'bool', if_empty=False)
        el.submittedval = None
        self.assertEqual(el.value, False)

        # conversion with if_empty
        form = Form('f')
        el = form.add_text('field', 'Field', 'bool', if_empty=True)
        el.submittedval = False
        self.assertEqual(el.value, False)

        # conversion with if_empty
        form = Form('f')
        el = form.add_text('field', 'Field', 'bool', if_empty='1')
        self.assertEqual(el.value, True)

    def test_type_strings(self):

        form = Form('f')
        form.add_text('f1', 'Field', 'bool', if_empty='1.25')
        self.assertEqual(form.elements.f1.value, True)
        form.add_text('f2', 'Field', 'boolean', if_empty='1.25')
        self.assertEqual(form.elements.f2.value, True)
        form.add_text('f3', 'Field', 'int', if_empty='1')
        self.assertEqual(form.elements.f3.value, 1)
        form.add_text('f4', 'Field', 'integer', if_empty='1')
        self.assertEqual(form.elements.f4.value, 1)
        form.add_text('f5', 'Field', 'num', if_empty='1.25')
        self.assertEqual(form.elements.f5.value, 1.25)
        form.add_text('f6', 'Field', 'number', if_empty='1.25')
        self.assertEqual(form.elements.f6.value, 1.25)
        form.add_text('f7', 'Field', 'float', if_empty='1.25')
        self.assertEqual(form.elements.f7.value, 1.25)
        form.add_text('f8', 'Field', 'str', if_empty='1.25')
        self.assertEqual(form.elements.f8.value, '1.25')
        form.add_text('f9', 'Field', 'string', if_empty='1.25')
        self.assertEqual(form.elements.f9.value, '1.25')
        form.add_text('f10', 'Field', 'uni', if_empty='1.25')
        self.assertEqual(form.elements.f10.value, u'1.25')
        form.add_text('f11', 'Field', 'unicode', if_empty='1.25')
        self.assertEqual(form.elements.f11.value, u'1.25')
        form.add_text('f12', 'Field', 'bool', if_empty='false')
        self.assertEqual(form.elements.f12.value, False)
        form.add_text('f13', 'Field', 'decimal', if_empty='1.25')
        self.assertEqual(form.elements.f13.value, decimal.Decimal('1.25'))
        form.elements.f13.submittedval = 'foo'
        assert form.elements.f13.is_valid() is False

        # test invalid vtype
        form = Form('f')
        try:
            form.add_text('f1', 'Field', 'badvtype')
        except ValueError as e:
            self.assertEqual('invalid vtype "badvtype"', str(e))

        # test wrong type of vtype
        try:
            form.add_text('f2', 'Field', ())
        except TypeError as e:
            self.assertRegexpMatches(
                str(e), r'vtype should have been a string, got <(type|class) \'tuple\'> instead'
            )
    #
    # def from_python_exception(self):
    #    # waht do we do with from_python validation problems, anything?  Right now
    #    # they just throw an exception
    #    el = Form('f').add_email('field', 'Field', defaultval='bad_email')
    #    el.render()


class InputElementsTest(unittest.TestCase):

    def test_el_button(self):
        html = '<input class="button" id="f-field" name="field" type="button" />'
        el = Form('f').add_button('field', 'Field')
        assert el() == html

    def test_el_checkbox(self):
        not_checked = '<input class="checkbox" id="f-f" name="f" type="checkbox" />'
        checked = '<input checked="checked" class="checkbox" id="f-f" name="f" type="checkbox" />'

        # no default
        f = Form('f')
        el = f.add_checkbox('f', 'f')
        self.assertEqual(str(el()), not_checked)

        # default from defaultval (True)
        el = Form('f').add_checkbox('f', 'f', defaultval=True)
        self.assertEqual(str(el()), checked)
        el = Form('f').add_checkbox('f', 'f', defaultval='checked')
        self.assertEqual(str(el()), checked)
        el = Form('f').add_checkbox('f', 'f', defaultval=1)
        self.assertEqual(str(el()), checked)

        # default from defaultval (False)
        el = Form('f').add_checkbox('f', 'f', defaultval=False)
        self.assertEqual(str(el()), not_checked)
        el = Form('f').add_checkbox('f', 'f', defaultval=None)
        self.assertEqual(str(el()), not_checked)
        el = Form('f').add_checkbox('f', 'f', defaultval=0)
        self.assertEqual(str(el()), not_checked)

        # default from checked (True)
        el = Form('f').add_checkbox('f', 'f', checked=True)
        self.assertEqual(str(el()), checked)
        el = Form('f').add_checkbox('f', 'f', checked='checked')
        self.assertEqual(str(el()), checked)
        el = Form('f').add_checkbox('f', 'f', checked=1)
        self.assertEqual(str(el()), checked)

        # default from checked (False)
        el = Form('f').add_checkbox('f', 'f', checked=False)
        self.assertEqual(str(el()), not_checked)
        el = Form('f').add_checkbox('f', 'f', checked=None)
        self.assertEqual(str(el()), not_checked)
        el = Form('f').add_checkbox('f', 'f', checked=0)
        self.assertEqual(str(el()), not_checked)

        # default takes precidence over checked
        el = Form('f').add_checkbox('f', 'f', defaultval=True, checked=False)
        self.assertEqual(str(el()), checked)
        el = Form('f').add_checkbox('f', 'f', defaultval=False, checked=True)
        self.assertEqual(str(el()), not_checked)

        # default should not affect value
        el = Form('f').add_checkbox('f', 'f', defaultval=True)
        self.assertEqual(el.value, False)

        # true submit values
        el = Form('f').add_checkbox('f', 'f')
        el.submittedval = True
        self.assertEqual(el.value, True)
        el = Form('f').add_checkbox('f', 'f')
        el.submittedval = 1
        self.assertEqual(el.value, True)
        el = Form('f').add_checkbox('f', 'f')
        el.submittedval = 'checked'
        self.assertEqual(el.value, True)
        el.submittedval = 'on'
        self.assertEqual(el.value, True)
        el.submittedval = ''
        self.assertEqual(el.value, True)

        # false submit values
        el = Form('f').add_checkbox('f', 'f')
        el.submittedval = False
        self.assertEqual(el.value, False)
        el = Form('f').add_checkbox('f', 'f')
        el.submittedval = 0
        self.assertEqual(el.value, False)
        el = Form('f').add_checkbox('f', 'f')
        self.assertEqual(el.value, False)

        # converted values int (true)
        el = Form('f').add_checkbox('f', 'f', 'int')
        el.submittedval = True
        self.assertEqual(el.value, 1)
        el = Form('f').add_checkbox('f', 'f', 'int')
        el.submittedval = 1
        self.assertEqual(el.value, 1)
        el = Form('f').add_checkbox('f', 'f', 'int')
        el.submittedval = 'checked'
        self.assertEqual(el.value, 1)

        # converted values int (false)
        el = Form('f').add_checkbox('f', 'f', 'int')
        el.submittedval = False
        self.assertEqual(el.value, 0)
        el = Form('f').add_checkbox('f', 'f', 'int')
        el.submittedval = 0
        self.assertEqual(el.value, 0)
        el = Form('f').add_checkbox('f', 'f', 'int')
        self.assertEqual(el.value, 0)

    def test_el_checkbox_req(self):
        # required value: requires special handling b/c we get
        # None for a checkbox when its missing
        el = Form('f').add_checkbox('f', 'f', 'int', required=True)
        assert not el.is_valid()

    def test_el_hidden(self):
        html = '<input class="hidden" id="f-field" name="field" type="hidden" />'
        el = Form('f').add_hidden('field', 'Field')
        self.assertEqual(str(el()), html)

    def test_el_image(self):
        html = '<input class="image" id="f-field" name="field" type="image" />'
        el = Form('f').add_image('field', 'Field')
        self.assertEqual(str(el()), html)

    def test_el_reset(self):
        html = '<input class="reset" id="f-field" name="field" type="reset" value="Reset" />'
        el = Form('f').add_reset('field', 'Field')
        self.assertEqual(str(el()), html)

        html = '<input class="reset" id="f-field" name="field" type="reset" value="r" />'
        el = Form('f').add_reset('field', 'Field', defaultval='r')
        self.assertEqual(str(el()), html)

    def test_el_submit(self):
        html = '<input class="submit" id="f-field" name="field" type="submit" value="Submit" />'
        el = Form('f').add_submit('field', 'Field')
        self.assertEqual(str(el()), html)

        html = '<input class="submit" id="f-field" name="field" type="submit" value="s" />'
        el = Form('f').add_submit('field', 'Field', defaultval='s')
        self.assertEqual(str(el()), html)

        # had a problem where we will get two class attributes
        html = '<input class="submit wymupdate" id="f-field" name="field" ' \
            'type="submit" value="Submit" />'
        el = Form('f').add_submit('field', 'Field')
        el.add_attr('class', 'wymupdate')
        self.assertEqual(str(el()), html)

        # submit button with a different name
        html = '<input class="submit" id="f-field" name="submitbtn" type="submit" value="Reset" />'
        el = Form('f').add_submit('field', 'Field', defaultval='Reset', name='submitbtn')
        self.assertEqual(str(el()), html)

        # FIXED submit button after form post
        html = '<input class="submit" id="f-field" name="submitbtn" type="submit" value="Reset" />'
        form = Form('f')
        el = form.add_submit('field', 'Field', defaultval='Reset', name='submitbtn')
        el.submittedval = '1'
        self.assertEqual(el.value, '1')
        self.assertEqual(str(el()), html)

        # submit button after form post
        html = '<input class="submit" id="f-field" name="submitbtn" type="submit" value="1" />'
        form = Form('f')
        el = form.add_submit('field', 'Field', defaultval='Reset', name='submitbtn', fixed=False)
        el.submittedval = '1'
        self.assertEqual(el.value, '1')
        self.assertEqual(str(el()), html)

    def test_el_cancel(self):
        html = '<input class="submit" id="f-field" name="field" type="submit" value="Cancel" />'
        el = Form('f').add_cancel('field', 'Field')
        self.assertEqual(str(el()), html)

        html = '<input class="submit" id="f-field" name="field" type="submit" value="c" />'
        el = Form('f').add_cancel('field', 'Field', defaultval='c')
        self.assertEqual(str(el()), html)

    def test_el_text(self):
        html = '<input class="text" id="f-field" name="field" type="text" />'
        form = Form('f')
        el = form.add_text('field', 'Field')
        self.assertEqual(str(el()), html)

        html = '<input class="text" id="f-field" maxlength="1" name="field" type="text" />'
        form = Form('f')
        el = form.add_text('field', 'Field', maxlength=1)
        self.assertEqual(str(el()), html)
        el.submittedval = '1'
        self.assertEqual(el.value, '1')

        # too long
        el.submittedval = '12'
        self.assertEqual(el.is_valid(), False)

        # no validator
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.submittedval = '12'
        self.assertEqual(el.value, '12')

    def test_el_confirm(self):
        try:
            Form('f').add_confirm('f')
            self.fail('expected key error for missing "match"')
        except ProgrammingError as e:
            if 'match argument is required' not in str(e):
                raise
        try:
            Form('f').add_confirm('f', match='notthere')
            self.fail('expected element does not exist error')
        except ProgrammingError as e:
            if 'match element "notthere" does not exist' != str(e):
                raise

        try:
            datematch = datetime.datetime.now()
            Form('f').add_confirm('f', match=datematch)
            self.fail('expected wrong type error')
        except ProgrammingError as e:
            if 'match element was not of type HasValueElement' != str(e):
                raise

        # match password
        html = '<input class="password" id="f-f" name="f" type="password" />'
        vhtml = '<input class="password" id="f-f" name="f" type="password" value="foo" />'
        f = Form('f')
        pel = f.add_password('p', 'password')
        cel = f.add_confirm('f', match='p')
        self.assertEqual(str(cel()), html)
        pel.submittedval = 'foo'
        cel.submittedval = 'foo'
        assert cel.is_valid()
        self.assertEqual(str(cel()), html)
        pel.submittedval = 'bar'
        cel.submittedval = 'foo'
        assert not cel.is_valid()
        assert cel.errors[0] == 'does not match field "password"'
        pel.default_ok = True
        self.assertEqual(str(cel()), vhtml)

        # match non-password field
        html = '<input class="text" id="f-f" name="f" type="text" />'
        vhtml = '<input class="text" id="f-f" name="f" type="text" value="foo" />'
        f = Form('f')
        pel = f.add_text('e', 'email')
        cel = f.add_confirm('f', match=pel)
        self.assertEqual(str(cel()), html)
        pel.submittedval = 'foo'
        cel.submittedval = 'foo'
        assert cel.is_valid()
        self.assertEqual(str(cel()), vhtml)
        pel.submittedval = 'bar'
        cel.submittedval = 'foo'
        assert not cel.is_valid()
        assert cel.errors[0] == 'does not match field "email"'

    def test_el_confirm_empty(self):
        # empty confirm value
        f = Form('f')
        pel = f.add_password('p', 'password')
        cel = f.add_confirm('f', match='p')
        pel.submittedval = 'bar'
        cel.submittedval = ''
        assert not cel.is_valid()
        assert cel.errors[0] == 'does not match field "password"'

    def test_el_confirm_invalid(self):
        # empty confirm value
        f = Form('f')
        pel = f.add_password('p', 'password', required=True)
        cel = f.add_confirm('f', match='p')
        pel.submittedval = ''
        cel.submittedval = ''
        assert not pel.is_valid()
        assert cel.is_valid()

    def test_el_date(self):
        html = '<input class="text" id="f-field" name="field" type="text" />'
        el = Form('f').add_date('field', 'Field')
        self.assertEqual(str(el()), html)

        # our date-time object should get converted to the appropriate format
        html = '<input class="text" id="f-field" name="field" type="text" value="12/03/2009" />'
        el = Form('f').add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3))
        self.assertEqual(str(el()), html)
        el.submittedval = '1/5/09'
        assert el.value == datetime.date(2009, 1, 5)
        el.submittedval = '2-30-04'
        assert not el.is_valid()

        # european style dates
        html = '<input class="text" id="f-field" name="field" type="text" value="03/12/2009" />'
        el = Form('f').add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3),
                                month_style='dd/mm/yyyy')
        self.assertEqual(str(el()), html)
        el.submittedval = '1/5/09'
        assert el.value == datetime.date(2009, 5, 1)
        el.submittedval = '2-30-04'
        assert not el.is_valid()

        # no-day dates
        html = '<input class="text" id="f-field" name="field" type="text" value="12/2009" />'
        el = Form('f').add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3),
                                accept_day=False)
        self.assertEqual(str(el()), html)
        el.submittedval = '5/09'
        assert el.value == datetime.date(2009, 5, 1)
        el.submittedval = '5/1/09'
        assert not el.is_valid()

        # date field not submitted
        f = Form('login')
        el = f.add_date('field', 'Field')
        post = {'login-submit-flag': 'submitted'}
        f.set_submitted(post)
        assert f.get_values() == {'field': NotGiven, 'login-submit-flag': 'submitted'}, \
            f.get_values()

    def test_el_email(self):
        html = '<input class="text" id="f-field" name="field" type="text" />'
        el = Form('f').add_email('field', 'Field')
        self.assertEqual(str(el()), html)
        el.submittedval = 'bob@example.com'
        assert el.value == 'bob@example.com'
        el.submittedval = 'bob'
        assert not el.is_valid()

        el = Form('f').add_email('field', 'Field', resolve_domain=True)
        el.submittedval = 'bob@ireallyhopethisdontexistontheweb.com'
        assert not el.is_valid()

    def test_el_password(self):
        html = '<input class="password" id="f-f" name="f" type="password" />'
        el = Form('f').add_password('f')
        self.assertEqual(str(el()), html)

        # default vals don't show up
        el = Form('f').add_password('f', defaultval='test')
        self.assertEqual(str(el()), html)

        # submitted vals don't show up
        el = Form('f').add_password('f')
        el.submittedval = 'test'
        self.assertEqual(str(el()), html)

        # default vals w/ default_ok
        html = '<input class="password" id="f-f" name="f" type="password" value="test" />'
        el = Form('f').add_password('f', defaultval='test', default_ok=True)
        self.assertEqual(str(el()), html)

        # submitted vals w/ default_ok
        el = Form('f').add_password('f', default_ok=True)
        el.submittedval = 'test'
        self.assertEqual(str(el()), html)

    def test_el_time(self):
        html = '<input class="text" id="f-f" name="f" type="text" />'
        el = Form('f').add_date('f')
        self.assertEqual(str(el()), html)

        # defaults
        html = '<input class="text" id="f-field" name="field" type="text" value="13:00:00" />'
        el = Form('f').add_time('field', 'Field', defaultval=(13, 0))
        self.assertEqual(str(el()), html)
        el.submittedval = '20:30'
        assert el.value == (20, 30)

        # some validator options
        html = '<input class="text" id="f-field" name="field" type="text" value="1:00pm" />'
        el = Form('f').add_time('field', 'Field', defaultval=(13, 0), use_ampm=True,
                                use_seconds=False)
        self.assertEqual(str(el()), html)
        el.submittedval = '8:30pm'
        assert el.value == (20, 30)

    def test_el_url(self):
        html = '<input class="text" id="f-f" name="f" type="text" />'
        el = Form('f').add_url('f')
        self.assertEqual(str(el()), html)

        html = '<input class="text" id="f-f" name="f" type="text" value="example.org" />'
        el = Form('f').add_url('f', defaultval="example.org", add_http=True)
        self.assertEqual(str(el()), html)
        el.submittedval = 'foo.com'
        self.assertEqual(el.value, 'http://foo.com')
        el.submittedval = 'foo'
        assert not el.is_valid()


class SelectTest(unittest.TestCase):
    def test_el_select(self):
        html = \
            '<select id="f-f" name="f">\n<option value="-2">Choose:'\
            '</option>\n<option value="-1">-------------------------</option>\n'\
            '<option value="1">a</option>\n<option value="2">b</option>\n</select>'
        o = [(1, 'a'), (2, 'b')]
        el = Form('f').add_select('f', o)
        self.assertEqual(str(el()), html)

        # custom choose name
        html = \
            '<select id="f-f" name="f">\n<option value="-2">test:'\
            '</option>\n<option value="-1">-------------------------</option>\n'\
            '<option value="1">a</option>\n<option value="2">b</option>\n</select>'
        el = Form('f').add_select('f', o, choose='test:')
        self.assertEqual(str(el()), html)

        # no choose
        html = \
            '<select id="f-f" name="f">\n'\
            '<option value="1">a</option>\n<option value="2">b</option>\n</select>'
        el = Form('f').add_select('f', o, choose=None)
        self.assertEqual(str(el()), html)

        # single element options
        html = '<select id="f-f" name="f">\n<option value="-2">Choose:'\
            '</option>\n<option value="-1">-------------------------</option>\n'\
            '<option value="0">0</option>\n<option value="1">1</option>\n</select>'
        el = Form('f').add_select('f', [0, 1])
        self.assertEqual(str(el()), html)

        # default values
        html = \
            '<select id="f-f" name="f">\n'\
            '<option selected="selected" value="1">a</option>\n<option value="2">'\
            'b</option>\n</select>'
        el = Form('f').add_select('f', o, defaultval=1, choose=None)
        self.assertEqual(str(el()), html)
        el = Form('f').add_select('f', o, defaultval='1', choose=None)
        self.assertEqual(str(el()), html)
        el = Form('f').add_select('f', o, defaultval=u'1', choose=None)
        self.assertEqual(str(el()), html)
        el = Form('f').add_select('f', o, defaultval=decimal.Decimal('1'), choose=None)
        self.assertEqual(str(el()), html)

        # value
        el = Form('f').add_select('f', o, if_empty=1)
        self.assertEqual(el.value, 1)
        el = Form('f').add_select('f', o, if_empty='1')
        self.assertEqual(el.value, '1')
        el = Form('f').add_select('f', o, if_empty=3)
        assert not el.is_valid()
        self.assertEqual(el.errors[0], 'the value did not come from the given options')

        # no auto validate
        el = Form('f').add_select('f', o, if_empty=3, auto_validate=False)
        assert el.is_valid()

        # conversion
        el = Form('f').add_select('f', o, vtype='int', if_empty='1')
        self.assertEqual(el.value, 1)

        # custom error message
        el = Form('f').add_select('f', o, if_empty=3, error_msg='test')
        assert not el.is_valid()
        self.assertEqual(el.errors[0], 'test')

        # choose values are invalid only if a value is required
        el = Form('f').add_select('f', o, if_empty=-2)
        assert el.is_valid()
        el = Form('f').add_select('f', o, if_empty=-2, required=True)
        assert not el.is_valid(), el.value
        assert 'the value chosen is invalid' in el.errors, el.errors
        el = Form('f').add_select('f', o, required=True)
        el.submittedval = -2
        assert not el.is_valid()
        assert 'the value chosen is invalid' in el.errors, el.errors

        # correct required error message
        el = Form('f').add_select('f', o, required=True)
        el.submittedval = ''
        assert not el.is_valid()
        assert 'field is required' in el.errors, el.errors

        # custom invalid values
        el = Form('f').add_select('f', o, if_empty=1, invalid=['2'])
        assert el.is_valid()
        el = Form('f').add_select('f', o, if_empty=1, invalid=['1', '2'])
        assert not el.is_valid()
        el = Form('f').add_select('f', o, if_empty=1, invalid=1)
        assert not el.is_valid()

        # "empty" value when required, but there is an empty value in the
        # options.  It seems that required meaning 'must not be empty' should
        # take precidence.
        el = Form('f').add_select('f', o + [('', 'blank')], if_empty='', required=True)
        assert not el.is_valid()

        # make sure choose values do not get returned when required=False
        el = Form('f').add_select('f', o, if_empty=1)
        el.submittedval = -1
        self.assertEqual(el.value, 1)
        el = Form('f').add_select('f', o)
        el.submittedval = -1
        self.assertEqual(el.value, None)

        # if vtype = bool, then we need to make sure a "choose" option doesn't
        # get returned as True
        el = Form('f').add_select('f', o, vtype='bool')
        el.submittedval = -1
        self.assertEqual(el.value, None)
        # but we should be able to specify if we always want a boolean value
        el = Form('f').add_select('f', o, if_empty=1, vtype='bool')
        el.submittedval = -1
        self.assertEqual(el.value, True)

        # make sure we do not accept multiple values if we aren't a multi
        # select
        el = Form('f').add_select('f', o, if_empty=[1, 2])
        assert not el.is_valid()

        # check the processor to be sure both tuples and strings are
        # allowed as options
        el_options = [(-2, 'Choose:'), (-1, '-----------'), ('first', 'First Option'),
                      'Second Option']

        el = Form('f').add_select('f', el_options)
        el.submittedval = 'first'
        assert el.is_valid()
        el.submittedval = 'Second Option'
        assert el.is_valid()

    def test_el_select_not_submitted(self):
        o = [(1, 'a'), (2, 'b')]
        # not submitted value when not required
        el = Form('f').add_select('f', o)
        el.is_valid()
        assert el.is_valid()
        assert el.value is NotGiven

    def test_el_select_strip(self):
        # make sure values get stripped
        el_options = [(-2, 'Choose:'), (-1, '-----------'), ('first', 'First Option'),
                      'Second Option']
        el = Form('f').add_select('f', el_options)
        el.submittedval = 'first '
        assert el.is_valid()
        el.submittedval = 'Second Option '
        assert el.is_valid()

    def test_el_select_strip_multi(self):
        el_options = [(-2, 'Choose:'), (-1, '-----------'), ('first', 'First Option'),
                      'Second Option']
        el = Form('f').add_mselect('f', el_options)
        el.submittedval = ['first ', 'Second Option ']
        assert el.is_valid()

    def test_el_select_multi(self):
        html = \
            '<select id="f-f" multiple="multiple" name="f">\n'\
            '<option value="-2">Choose:'\
            '</option>\n<option value="-1">-------------------------</option>\n'\
            '<option value="1">a</option>\n<option value="2">b</option>\n</select>'
        o = [(1, 'a'), (2, 'b')]
        el = Form('f').add_select('f', o, multiple=True)
        self.assertEqual(str(el()), html)
        el = Form('f').add_select('f', o, multiple=1)
        self.assertEqual(str(el()), html)
        el = Form('f').add_select('f', o, multiple='multiple')
        self.assertEqual(str(el()), html)
        el = Form('f').add_select('f', o, multiple=False)
        assert 'multiple' not in str(el())

        # single default values
        html = \
            '<select id="f-f" multiple="multiple" name="f">\n'\
            '<option selected="selected" value="1">a</option>\n<option value="2">'\
            'b</option>\n</select>'
        el = Form('f').add_mselect('f', o, defaultval=1, choose=None)
        self.assertEqual(str(el()), html)
        el = Form('f').add_mselect('f', o, defaultval=[1, 3], choose=None)
        self.assertEqual(str(el()), html)

        # multiple default values
        html = \
            '<select id="f-f" multiple="multiple" name="f">\n'\
            '<option selected="selected" value="1">a</option>\n'\
            '<option selected="selected" value="2">'\
            'b</option>\n</select>'
        el = Form('f').add_mselect('f', o, defaultval=(1, 2), choose=None)
        self.assertEqual(str(el()), html)
        el = Form('f').add_mselect('f', o, defaultval=[1, 2], choose=None)
        self.assertEqual(str(el()), html)

    def test_el_select_multi1(self):
        o = [(1, 'a'), (2, 'b')]
        # value
        el = Form('f').add_mselect('f', o, if_empty=1)
        self.assertEqual(el.value, [1])
        el = Form('f').add_mselect('f', o, if_empty=1, auto_validate=False)
        self.assertEqual(el.value, [1])
        el = Form('f').add_mselect('f', o, if_empty=[1, 2])
        self.assertEqual(el.value, [1, 2])
        el = Form('f').add_mselect('f', o, if_empty=['1', '2'])
        self.assertEqual(el.value, ['1', '2'])
        el = Form('f').add_mselect('f', o)
        el.submittedval = ['1', '2']
        self.assertEqual(el.value, ['1', '2'])
        el = Form('f').add_mselect('f', o, if_empty=[1, 3])
        assert not el.is_valid()
        self.assertEqual(el.errors[0], 'the value did not come from the given options')

        # no auto validate
        el = Form('f').add_mselect('f', o, if_empty=[1, 3], auto_validate=False)
        assert el.is_valid()
        self.assertEqual(el.value, [1, 3])

        # conversion
        el = Form('f').add_mselect('f', o, vtype='int', if_empty=['1', 2])
        self.assertEqual(el.value, [1, 2])

        # choose values are invalid only if a value is required
        el = Form('f').add_mselect('f', o, if_empty=(-2, 1))
        assert el.is_valid()
        el = Form('f').add_mselect('f', o, if_empty=(-2, 1), required=True)
        assert not el.is_valid()

        # custom invalid values
        el = Form('f').add_mselect('f', o, if_empty=(-1, 1), invalid=['2'])
        assert el.is_valid()
        el = Form('f').add_mselect('f', o, if_empty=(-1, 1), invalid=['1', '2'])
        assert not el.is_valid()
        el = Form('f').add_mselect('f', o, if_empty=(-1, 1), invalid=1)
        assert not el.is_valid()

    def test_el_select_multi2(self):
        o = [(1, 'a'), (2, 'b')]
        # not submitted value when not required is OK.
        # Should return NotGivenIter
        el = Form('f').add_mselect('f', o)
        assert el.is_valid()
        assert el.value is NotGivenIter, el.value
        for v in el.value:
            self.fail('should emulate empty')
        else:
            assert True, 'should emulate empty'
        assert el.value == []

        # "empty" value when required, but there is an empty value in the
        # options.  It seems that required meaning 'must not be empty' should
        # take precidence.
        el = Form('f').add_mselect('f', o + [('', 'blank')], if_empty='', required=True)
        assert not el.is_valid()

        # make sure choose values do not get returned when required=False
        el = Form('f').add_mselect('f', o, if_empty=1)
        el.submittedval = [-2, -1]
        self.assertEqual(el.value, [1])
        el = Form('f').add_mselect('f', o)
        el.submittedval = [-1, -2]
        self.assertEqual(el.value, [])
        el = Form('f').add_mselect('f', o)
        el.submittedval = [-1, 1]
        self.assertEqual(el.value, [1])
        el = Form('f').add_mselect('f', o)
        el.submittedval = [-2]
        self.assertEqual(el.value, [])
        el.submittedval = -2
        self.assertEqual(el.value, [])
        el.submittedval = [u'-2']
        self.assertEqual(el.value, [])
        el.submittedval = ['-2']
        self.assertEqual(el.value, [])

        # choose values should not get stripped out when choose=False
        o = [(1, 'a'), (-2, 'b')]
        el = Form('f').add_mselect('f', o, choose=False)
        el.submittedval = [-2]
        self.assertEqual(el.value, [-2])

    def test_el_select_name_attr(self):
        o = [(1, 'a'), (2, 'b')]
        html = \
            '<select id="f-f" name="myselect">\n'\
            '<option selected="selected" value="1">a</option>\n<option value="2">'\
            'b</option>\n</select>'
        el = Form('f').add_select('f', o, defaultval=1, choose=None, name="myselect")
        self.assertEqual(str(el()), html)


class OtherElementsTest(unittest.TestCase):
    def test_el_textarea(self):
        html = '<textarea class="foo" cols="40" id="f-f" name="f" rows="7"></textarea>'
        el = Form('f').add_textarea('f')
        self.assertEqual(str(el(class_='foo')), html)
        html = '<textarea cols="40" id="f-f" name="f" rows="7">foo</textarea>'
        el = Form('f').add_textarea('f', defaultval='foo')
        self.assertEqual(str(el()), html)
        html = '<textarea class="foo" cols="40" id="f-f" maxlength="500" name="f" rows="7">' \
            '</textarea>'
        el = Form('f').add_textarea('f', maxlength=500)
        self.assertEqual(str(el(class_='foo')), html)
        self.assertEqual(el.get_attr('maxlength'), 500)
        self.assertEqual(len(el.processors), 1)
        assert type(el.processors[0][0]) == MaxLength

    def test_el_passthru(self):
        f = Form('f')
        f.add_text('text')
        el = f.add_passthru('f', 'foo')
        assert el.value == 'foo'
        try:
            el.render()
            self.fail('passthru should not render')
        except AttributeError:
            pass
        try:
            el.submittedval = 'foo'
            self.fail('passthru should not be submittable')
        except NotImplementedError:
            pass
        # a submitted value should not affect the returned value
        f.set_submitted({'f': 'bar', 'text': 'baz', 'f-submit-flag': 'submitted'})
        self.assertEqual(f.values, {'f': 'foo', 'text': 'baz', 'f-submit-flag': 'submitted'})

        # need to test defaulting, passthru should also pick that up
        f = Form('f')
        f.add_text('text')
        el = f.add_passthru('f')
        f.set_defaults({'f': 'foo'})
        f.set_submitted({'f': 'bar', 'text': 'baz', 'f-submit-flag': 'submitted'})
        self.assertEqual(f.values, {'f': 'foo', 'text': 'baz', 'f-submit-flag': 'submitted'})

    def test_el_fixed(self):
        f = Form('f')
        el = f.add_fixed('f', defaultval='foo', title='baz')
        self.assertEqual(el(class_='bar'), L('<div class="bar" id="f-f" title="baz">foo</div>'))

        # we want to be able to use a label on fixed elements
        f = Form('f')
        el = f.add_fixed('f', 'Foo', 'foo', title='baz')
        self.assertEqual(el.label(), L('<label>Foo</label>'))
        self.assertEqual(el(class_='bar'), L('<div class="bar" id="f-f" title="baz">foo</div>'))

    def test_el_static(self):
        f = Form('f')
        f.add_text('text')
        el = f.add_static('f', 'label', 'foo')
        assert el.render() == L('<span id="f-f">foo</span>')
        try:
            assert el.value == 'foo'
            self.fail('static should not have a value')
        except NotImplementedError:
            pass

        try:
            el.submittedval = 'foo'
            self.fail('static should not be submittable')
        except NotImplementedError:
            pass

        # the value should not show up in return values or be submittable
        f.set_submitted({'f': 'bar', 'text': 'baz', 'f-submit-flag': 'submitted'})
        self.assertEqual(f.values, {'text': 'baz', 'f-submit-flag': 'submitted'})

        # need to test defaulting, passthru should also pick that up
        f = Form('f')
        f.add_text('text')
        el = f.add_static('f', 'label')
        f.set_defaults({'f': 'foo'})
        self.assertEqual(el(), L('<span id="f-f">foo</span>'))

    def test_el_header(self):
        el = Form('f').add_header('f', 'heading')
        assert el.render() == L('<h3 id="f-f">heading</h3>')

        # different header
        el = Form('f').add_header('f', 'heading', 'h2')
        assert el.render() == L('<h2 id="f-f">heading</h2>')

        # with attributes
        el = Form('f').add_header('f', 'foo', title='baz')
        self.assertEqual(el(class_='bar'), L('<h3 class="bar" id="f-f" title="baz">foo</h3>'))

        # empty header
        el = Form('f').add_header('f')
        self.assertEqual(el.render(), L('<h3 id="f-f"></h3>'))


class LogicalElementsTest(unittest.TestCase):

    def test_mcheckbox(self):
        not_checked = L('<input class="checkbox" id="f-f" name="thegroup" type="checkbox" />')
        checked = L('<input checked="checked" class="checkbox" id="f-f" name="thegroup" '
                    'type="checkbox" />')

        el = Form('f').add_mcheckbox('f', 'label', group='thegroup')
        self.assertEqual(el(), not_checked)
        el = Form('f').add_mcheckbox('f', 'label', group='thegroup', checked=True)
        self.assertEqual(el(), checked)
        el = Form('f').add_mcheckbox('f', 'label', group='thegroup')
        self.assertEqual(el(checked='checked'), checked)

        not_checked = L('<input class="checkbox" id="f-f" name="thegroup" type="checkbox" '
                        'value="foo" />')
        checked = L('<input checked="checked" class="checkbox" id="f-f" name="thegroup" '
                    'type="checkbox" value="foo" />')

        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(), not_checked)
        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup', checked=True)
        self.assertEqual(el(), checked)
        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(checked='checked'), checked)
        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup')
        el.chosen = True
        self.assertEqual(el(), checked)

        # can't have two elements in same group with same value
        f = Form('f')
        f.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
        try:
            f.add_mcheckbox('f2', 'label', 'foo', 'thegroup')
        except ValueError:
            pass

        # elements should not take submit values
        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup')
        try:
            el.submittedval = False
            self.fail('should not accept submittedval')
        except NotImplementedError:
            pass
        el.form.set_submitted({'f': 'test'})

        # cannot set required on an mcheckbox
        try:
            el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup', required=True)
        except ProgrammingError as pe:
            assert pe.args[0] == 'Required is not allowed on this element. ' \
                'Set it for the logical group.'

    def test_mcheckbox2(self):
        # test the elements getting chosen by setting form defaults
        f = Form('f')
        el1 = f.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
        el2 = f.add_mcheckbox('f2', 'label', 'bar', 'thegroup')
        assert el1.chosen is el2.chosen is False

        f.set_defaults({'thegroup': 'foo'})

        assert el1.chosen
        assert not el2.chosen
        f.set_defaults({'thegroup': ['foo', 'bar']})
        assert el1.chosen
        assert el2.chosen
        # it was chosen, but should "undo" when set again
        f.set_defaults({'thegroup': 'foo'})
        assert el1.chosen
        assert not el2.chosen

    def test_mcheckbox3(self):
        # test the elements getting chosen by form submissions
        f = Form('f')
        el1 = f.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
        el2 = f.add_mcheckbox('f2', 'label', 'bar', 'thegroup')
        assert el1.chosen is el2.chosen is False
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': 'foo'})
        assert f.elements.thegroup.value == ['foo'], f.elements.thegroup.value
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': ['foo', 'bar']})
        assert f.elements.thegroup.value == ['foo', 'bar']
        assert el1.chosen
        assert el2.chosen
        # it was chosen, but should "undo" when set again
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': 'foo'})
        assert el1.chosen
        assert not el2.chosen
        # both should unset
        f.set_submitted({'f-submit-flag': 'submitted'})
        assert not el1.chosen
        assert not el2.chosen

    def test_mcheckbox4(self):
        # test integer values
        f = Form('f')
        el1 = f.add_mcheckbox('f1', 'label', 1, 'thegroup')
        el2 = f.add_mcheckbox('f2', 'label', 2, 'thegroup')
        assert el1.chosen is el2.chosen is False
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': 1})
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': '1'})
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': [1, '2']})
        assert el1.chosen
        assert el2.chosen

    def test_radio(self):
        not_selected = L('<input class="radio" id="f-f" name="thegroup" type="radio" />')
        selected = L('<input checked="checked" class="radio" id="f-f" name="thegroup" '
                     'type="radio" />')

        el = Form('f').add_radio('f', 'label', group='thegroup')
        self.assertEqual(el(), not_selected)
        el = Form('f').add_radio('f', 'label', group='thegroup', selected=True)
        self.assertEqual(el(), selected)
        el = Form('f').add_radio('f', 'label', group='thegroup')
        self.assertEqual(el(checked='checked'), selected)

        not_selected = L('<input class="radio" id="f-f" name="thegroup" type="radio" '
                         'value="foo" />')
        selected = L('<input checked="checked" class="radio" id="f-f" name="thegroup" '
                     'type="radio" value="foo" />')

        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(), not_selected)
        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup', selected=True)
        self.assertEqual(el(), selected)
        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(checked='checked'), selected)
        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup')
        el.chosen = True
        self.assertEqual(el(), selected)

        # cannot set required on an mradio
        try:
            el = Form('f').add_radio('f', 'label', 'foo', 'thegroup', required=True)
        except ProgrammingError as pe:
            assert pe.args[0] == 'Required is not allowed on this element. ' \
                'Set it for the logical group.'

    def test_radio2(self):
        # test the elements getting chosen by setting form defaults
        f = Form('f')
        el1 = f.add_radio('f1', 'label', 'foo', 'thegroup')
        el2 = f.add_radio('f2', 'label', 'bar', 'thegroup')
        assert el1.chosen is el2.chosen is False
        f.set_defaults({'thegroup': 'foo'})
        assert el1.chosen
        assert not el2.chosen
        f.set_defaults({'thegroup': ['foo', 'bar']})
        assert el1.chosen
        assert el2.chosen
        # it was chosen, but should "undo" when set again
        f.set_defaults({'thegroup': 'foo'})
        assert el1.chosen
        assert not el2.chosen

    def test_radio3(self):
        # test the elements getting chosen by form submissions
        f = Form('f')
        el1 = f.add_radio('f1', 'label', 'foo', 'thegroup')
        el2 = f.add_radio('f2', 'label', 'bar', 'thegroup')
        assert el1.chosen is el2.chosen is False
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': 'foo'})
        assert f.elements.thegroup.value == 'foo'
        assert el1.chosen
        assert not el2.chosen
        # a radio shouldn't accept multiple values, the children will not
        # be affected
        f.set_submitted({'thegroup': ['foo', 'bar']})
        assert el1.chosen
        assert not el2.chosen
        assert not f.elements.thegroup.is_valid()
        assert f.elements.thegroup.errors[0] == 'this field does not accept more than one value'
        # it was chosen, but should "undo" when set again
        f.set_submitted({'thegroup': 'bar'})
        assert not el1.chosen
        assert el2.chosen
        # both should unset
        f.set_submitted({'f-submit-flag': 'submitted'})
        assert not el1.chosen
        assert not el2.chosen

    def test_mradio4(self):
        # test integer values
        f = Form('f')
        el1 = f.add_radio('f1', 'label', 1, 'thegroup')
        el2 = f.add_radio('f2', 'label', 2, 'thegroup')
        assert el1.chosen is el2.chosen is False
        f.set_submitted({'f-submit-flag': 'submitted', 'thegroup': 1})
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'thegroup': '1'})
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'thegroup': '2'})
        assert not el1.chosen
        assert el2.chosen

    def test_dup_values(self):
        f = Form('f')
        f.add_radio('radio1', 'Radio 1', group='rgroup1')
        try:
            f.add_radio('radio2', 'Radio 2', group='rgroup1')
            self.fail('should have got duplicate value assertion')
        except ValueError as e:
            self.assertEqual(str(e), 'a member of this group already exists with value ""')

    def test_non_rendering(self):
        f = Form('f')
        el = f.add_radio('radio1', 'Radio 1', group='rgroup1')
        assert el.lgroup not in f.renderable_els, 'logical group is trying to render'


class LogicalElementsTest2(unittest.TestCase):
    def setUp(self):
        self.f = f = Form('f')
        self.el1 = f.add_mcheckbox('f1', 'label', 1, 'thegroup')
        self.el2 = f.add_mcheckbox('f2', 'label', 2, 'thegroup')
        self.el3 = f.add_mcheckbox('f3', 'label', 3, 'thegroup')
        self.el3 = f.add_mcheckbox('f4', 'label', '', 'thegroup')
        self.gel = f.elements.thegroup

    def test_1(self):
        self.gel.if_empty = 1
        self.assertEqual(self.gel.value, [1])

    def test_2(self):
        self.gel.if_empty = [1, 2]
        self.assertEqual(self.gel.value, [1, 2])

    def test_3(self):
        self.gel.if_empty = ['1', '2']
        self.assertEqual(self.gel.value, ['1', '2'])

    def test_4(self):
        self.gel.if_empty = [1, 4]
        assert not self.gel.is_valid()
        self.assertEqual(self.gel.errors[0], 'the value did not come from the given options')

    def test_5(self):
        self.gel.if_empty = [1, 4]
        self.gel.auto_validate = False
        assert self.gel.value == [1, 4]

    def test_6(self):
        # custom error message
        self.gel.if_empty = [1, 4]
        self.gel.error_msg = 'test'
        assert not self.gel.is_valid()
        self.assertEqual(self.gel.errors[0], 'test')

    def test_7(self):
        # conversion
        self.gel.if_empty = ['1', 2]
        self.gel.vtype = 'int'
        self.assertEqual(self.gel.value, [1, 2])

    def test_8(self):
        # custom invalid values
        self.gel.if_empty = (1, 2)
        self.gel.invalid = ['3']
        assert self.gel.is_valid()

    def test_9(self):
        # custom invalid values
        self.gel.if_empty = (1, 2)
        self.gel.invalid = '3'
        assert self.gel.is_valid()

    def test_10(self):
        # custom invalid values
        self.gel.if_empty = (1, 2)
        self.gel.invalid = ['2']
        assert not self.gel.is_valid()

    def test_11(self):
        # custom invalid values
        self.gel.if_empty = (1, 2)
        self.gel.invalid = '2'
        assert not self.gel.is_valid()

    def test_12(self):
        # custom invalid values
        self.gel.if_empty = (1, 2)
        self.gel.invalid = ['2', '3']
        assert not self.gel.is_valid()

    def test_13(self):
        # not submitted value when not required is OK.
        # Should return NotGivenIter
        self.gel.is_valid()
        assert self.gel.is_valid()

    def test_14(self):
        # value required
        self.gel.required = True
        assert not self.gel.is_valid()

    def test_15(self):
        # "empty" value when required, but there is an empty value in the
        # options.  It seems that required meaning 'must not be empty' should
        # take precidence.
        self.gel.required = True
        self.gel.if_empty = ''
        assert not self.gel.is_valid()

    def test_16(self):
        # custom processor
        def validator(value):
            raise ValueInvalid('test')
        self.gel.if_empty = 1
        self.gel.add_processor(validator)
        assert not self.gel.is_valid()


class FileUploadsTest(unittest.TestCase):

    blank = BaseTranslator(None, 'application/octet-stream', 0)
    # technically, we shouldn't get a size with an emptystring name, but just
    # in case
    noname = BaseTranslator('', 'text/plain', 10)
    text = BaseTranslator('text.txt', 'text/plain', 10)
    noext = BaseTranslator('nofileext', 'text/plain', 10)
    noct = BaseTranslator('text.txt', '', 10)

    def test_html(self):
        html = L('<input class="file" id="f-f" name="f" type="file" />')
        el = Form('f').add_file('f')
        self.assertEqual(el(), html)

    def test_defaults(self):
        el = Form('f').add_file('f')
        self.assertEqual(el.defaultval, NotGiven)
        self.assertEqual(el.displayval, NotGiven)
        # setting to not given is ok
        el.defaultval = NotGiven
        # setting to anything else is a problem
        try:
            el.defaultval = 'foo'
            self.fail('file element should not support default values')
        except NotImplementedError as e:
            self.assertEqual(str(e), 'FileElement doesn\'t support default values')

    def test_submitted(self):
        el = Form('f').add_file('f')
        el.submittedval = self.text
        assert el.is_valid()
        self.assertEqual(el.value.file_name, self.text.file_name)
        self.assertEqual(el.value.content_type, self.text.content_type)
        self.assertEqual(el.value.content_length, self.text.content_length)

    def test_no_file_submit(self):
        el = Form('f').add_file('f')
        assert el.is_valid()
        assert el.value is NotGiven

        el = Form('f').add_file('f', required=True)
        assert not el.is_valid()

    def test_maxsize(self):
        tosub = self.text
        el = Form('f').add_file('f')
        el.maxsize(5)
        el.submittedval = tosub
        assert not el.is_valid(), 'max size validation should have failed'
        assert el.errors[0] == 'file too big (10), max size 5'

        el = Form('f').add_file('f')
        el.maxsize(15)
        el.submittedval = tosub
        assert el.is_valid(), 'max size validation should have been ok'

        # zero length max size validation
        # this is probably going to be confusing since the content length is usually not given
        # for files by a browser, but lets test anyway
        tosub = BaseTranslator('text.txt', 'text/plain', 0)
        el = Form('f').add_file('f')
        el.maxsize(5)
        el.submittedval = tosub
        assert not el.is_valid(), 'max size validation should have failed'
        assert el.errors[0] == 'maximum size requirement exists, but submitted file ' \
            'had no content length'

        # none should be the same as zero
        tosub = BaseTranslator('text.txt', 'text/plain', None)
        el = Form('f').add_file('f')
        el.maxsize(5)
        el.submittedval = tosub
        assert not el.is_valid(), 'max size validation should have failed'
        assert el.errors[0] == 'maximum size requirement exists, but submitted file ' \
            'had no content length'

        # no submission should pass since maxsize should only run if a file is uploaded
        el = Form('f').add_file('f')
        el.maxsize(5)
        el.submittedval = self.blank
        assert el.is_valid(), el.errors

    def test_allowexts(self):
        tosub = self.text
        el = Form('f').add_file('f')
        el.allow_extension('txt')
        el.submittedval = tosub
        assert el.is_valid()

        el = Form('f').add_file('f')
        el.allow_extension('.txt')
        el.submittedval = tosub
        assert el.is_valid()

        el = Form('f').add_file('f')
        el.allow_extension('pdf', 'doc')
        el.submittedval = tosub
        assert not el.is_valid()
        self.assertEqual(el.errors[0], 'extension ".txt" not allowed')

        tosub = self.noext
        el = Form('f').add_file('f')
        el.allow_extension('txt')
        el.submittedval = tosub
        assert not el.is_valid()
        assert 'submitted file had no extension' in el.errors[0]

        # no submission should work
        el = Form('f').add_file('f')
        el.allow_extension('txt')
        el.submittedval = self.blank
        assert el.is_valid(), el.errors

    def test_denyexts(self):
        tosub = self.text
        el = Form('f').add_file('f')
        el.deny_extension('txt')
        el.submittedval = tosub
        assert not el.is_valid()

        el = Form('f').add_file('f')
        el.deny_extension('.txt', '.pdf')
        el.submittedval = tosub
        assert not el.is_valid()
        assert el.errors[0] == 'extension ".txt" not permitted', el.errors

        el = Form('f').add_file('f')
        el.deny_extension('pdf', 'doc')
        el.submittedval = tosub
        assert el.is_valid()

        el = Form('f').add_file('f')
        el.deny_extension('txt')
        el.submittedval = self.noext
        assert not el.is_valid()
        assert 'submitted file had no extension' in el.errors[0]

        # no submission should work
        el = Form('f').add_file('f')
        el.deny_extension('txt')
        el.submittedval = self.blank
        assert el.is_valid()

    def test_allowtypes(self):
        tosub = self.text
        el = Form('f').add_file('f')
        el.allow_type('text/plain')
        el.submittedval = tosub
        assert el.is_valid()

        el = Form('f').add_file('f')
        el.allow_type('text/css', 'text/javascript')
        el.submittedval = tosub
        assert not el.is_valid()
        self.assertEqual(el.errors[0], 'content type "text/plain" not allowed')

        el = Form('f').add_file('f')
        el.allow_type('text/css', 'text/javascript')
        el.submittedval = self.noct
        assert not el.is_valid()
        assert 'submitted file had no content-type' in el.errors[0], el.errors

        # no submission should work
        el = Form('f').add_file('f')
        el.allow_type('text/css', 'text/javascript')
        el.submittedval = self.blank
        assert el.is_valid()

    def test_denytypes(self):
        tosub = self.text
        el = Form('f').add_file('f')
        el.deny_type('text/plain')
        el.submittedval = tosub
        assert not el.is_valid()
        self.assertEqual(el.errors[0], 'content type "text/plain" not permitted')

        el = Form('f').add_file('f')
        el.deny_type('text/css', 'text/javascript')
        el.submittedval = tosub
        assert el.is_valid()

        el = Form('f').add_file('f')
        el.deny_type('text/css', 'text/javascript')
        el.submittedval = self.noct
        assert not el.is_valid()
        assert 'submitted file had no content-type' in el.errors[0]

        # no submission should work
        el = Form('f').add_file('f')
        el.deny_type('text/css', 'text/javascript')
        el.submittedval = self.blank
        assert el.is_valid()

    def test_required(self):
        # None value for file name is valid as long as field isn't required
        el = Form('f').add_file('f')
        el.submittedval = self.blank
        assert el.is_valid()

        # ditto for empty string name
        el = Form('f').add_file('f')
        el.submittedval = self.noname
        assert el.is_valid()

        # making required should result in error
        el = Form('f').add_file('f', required=True)
        el.submittedval = self.noname
        assert not el.is_valid()
        assert el.errors[0] == 'field is required'

        # ditto for empty string name
        el = Form('f').add_file('f', required=True)
        el.submittedval = self.noname
        assert not el.is_valid()
        assert el.errors[0] == 'field is required'


# need to test adding group first and then members
# test setting attributes for each element with a render()
# from_python_exception test needs to be created
