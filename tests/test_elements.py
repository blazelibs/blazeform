import unittest
import datetime
import warnings
from formencode.validators import Int

from pysform import Form
from pysform.element import TextElement
from pysform.util import NotGiven, NotGivenIter, literal

L = literal

class CommonTest(unittest.TestCase):

    def test_render(self):
        html = '<input class="text" id="f-username" name="username" type="text" />'
        form = Form('f')
        el = form.add_element('text', 'username', 'User Name')
        self.assertEqual(html, str(form.username.render()))
        self.assertEqual(el.label.render(), L('<label for="f-username">User Name</label>'))
        
    def test_implicit_render(self):
        html = '<input class="text" id="f-username" name="username" type="text" />'
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        self.assertEqual(html, str(form.username()))
        
    def test_attr_render(self):
        html = '<input baz="bar" class="text foo bar" id="f-username" name="username" type="text" />'
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        self.assertEqual(html, str(form.username(class_='text foo bar', baz='bar')))

    def test_text_with_default(self):
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_element('text', 'username', 'User Name', defaultval='bar')
        self.assertEqual(html, str(form.username.render()))
    
    def test_text_with_default2(self):
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        form.set_defaults({'username':'bar'})
        self.assertEqual(html, str(form.username.render()))
    
    def test_text_submit(self):
        # make sure the submit value shows up in the form
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        form.set_submitted({'username':'bar'})
        self.assertEqual(html, str(form.username.render()))
    
    def test_submit_default(self):
        # submitted should take precidence over default
        html = '<input class="text" id="f-username" name="username" type="text" value="bar" />'
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        form.set_defaults({'username':'foo'})
        form.set_submitted({'username':'bar'})
        self.assertEqual(html, str(form.username.render()))
    
    def test_default_value(self):
        # default values do not show up in .value, they only show up when
        # rendering
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        form.set_defaults({'username':'foo'})
        self.assertEqual(None, form.username.value)
    
    def test_submitted_value(self):
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        form.set_defaults({'username':'foo'})
        form.set_submitted({'username':'bar'})
        self.assertEqual('bar', form.username.value)
        
    def test_notgiven(self):
        # test that NotGiven == None and is what we get when nothing
        # submitted
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        self.assertEqual(None, form.username.value)
        
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
        assert el.value is 'foo'
        
        # doesn't affect anything if the field is submitted
        f = Form('f')
        el = f.add_text('f', 'f', if_missing='foo')
        el.submittedval = None
        assert el.value is None
    
    def test_if_empty(self):
        # if empty works like if_missing when the field isn't submitted
        f = Form('f')
        el = f.add_text('f', 'f', if_empty='foo')
        assert el.value is 'foo'
        
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
        #change it
        f = Form('f')
        el = f.add_text('f', 'f', if_empty='')
        el.submittedval = None
        assert el.value == ''        
    
    def test_strip(self):
        # strip is on by default
        el = Form('f').add_text('f', 'f')
        el.submittedval = '   '
        assert el.value == None
        
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
        assert el.is_valid() == False
        
        el = Form('f').add_text('f', 'f', required=True, if_invalid='foo')
        el.submittedval = None
        self.assertEqual(el.value, 'foo')
        
    def test_blank_submit_value(self):
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        form.set_submitted({'username':''})
        self.assertEqual(None, form.username.value)
        
        form = Form('f')
        form.add_element('text', 'username', 'User Name', if_empty='')
        form.set_submitted({'username':''})
        self.assertEqual('', form.username.value)
    
    def test_is_submitted(self):
        form = Form('f')
        form.add_element('text', 'username', 'User Name')
        form.set_defaults({'username':'foo'})
        self.assertEqual(False, form.username.is_submitted())
        
        form.set_submitted({'username':''})
        self.assertEqual(True, form.username.is_submitted())
    
    def test_required(self):
        form = Form('f')
        el = form.add_element('text', 'username', 'User Name', required=True)
        self.assertEqual(True, el.required)
        self.assertEqual(False, form.username.is_valid())
        
        # setting submitted should reset _valid to None, which causes the
        # processing to happen again
        self.assertEqual(False, form.username._valid)
        el.submittedval = ''
        self.assertEqual(None, form.username._valid)
        
        el.submittedval = 'foo'
        self.assertEqual(True, form.username.is_valid())
    
    def test_invalid_value(self):
        form = Form('f')
        el = form.add_element('text', 'username', 'User Name', required=True)
        try:
            v = el.value
            self.fail('expected exception when trying to use .value when element is invalid')
        except Exception, e:
            if str(e) != 'element value is not valid':
                raise
        
        el.submittedval = ''
        try:
            v = el.value
            self.fail('expected exception when trying to use .value when element is invalid')
        except Exception, e:
            if str(e) != 'element value is not valid':
                raise
        
        el.submittedval = None
        try:
            v = el.value
            self.fail('expected exception when trying to use .value when element is invalid')
        except Exception, e:
            if str(e) != 'element value is not valid':
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
        el = form.add_element('text', 'username', 'User Name', if_empty='bar')
        el.add_processor(v)
        self.assertEqual(True, form.username.is_valid())
        self.assertEqual(1, v.vcalled)
        self.assertEqual(True, form.username.is_valid())
        self.assertEqual(1, v.vcalled)
        self.assertEqual('bar', form.username.value)
        self.assertEqual(1, v.vcalled)
        self.assertEqual('bar', form.username.value)
        self.assertEqual(1, v.vcalled)
        
        # setting submitted should reset _valid to None, which causes the
        # processing to happen again.  Make sure we don't use an empty value
        # b/c formencode seems to cache the results and our validator's method
        # won't be called again
        el.submittedval = 'foo'
        self.assertEqual('foo', form.username.value)
        self.assertEqual(2, v.vcalled)

    def test_error_messages(self):
        form = Form('f')
        el = form.add_element('text', 'username', 'User Name', required=True)
        self.assertEqual(False, form.username.is_valid())
        self.assertEqual(len(el.errors), 1)
        self.assertEqual('"User Name" is required', el.errors[0])
        
        # formencode message
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', if_empty='test')
        el.add_processor(Int)
        self.assertEqual(False, el.is_valid())
        self.assertEqual(len(el.errors), 1)
        self.assertEqual('Please enter an integer value', el.errors[0])
        
        # custom message
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', if_empty='test')
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
        el = form.add_element('text', 'field', 'Field')
        el.add_note('test note')
        self.assertEqual(el.notes[0], 'test note')
    
    def test_handlers(self):
        form = Form('f')
        el = form.add_element('text', 'field', 'Field')
        el.add_handler('text exception', 'test error msg')
        assert el.handle_exception(Exception('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')
        
        # make sure second exception works too
        form = Form('f')
        el = form.add_element('text', 'field', 'Field')
        el.add_handler('not it', '')
        el.add_handler('text exception', 'test error msg')
        assert el.handle_exception(Exception('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')
        
        # specifying exception type
        form = Form('f')
        el = form.add_element('text', 'field', 'Field')
        el.add_handler('text exception', 'test error msg', Exception)
        assert el.handle_exception(Exception('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')
        
        # right message, wrong type
        form = Form('f')
        el = form.add_element('text', 'field', 'Field')
        el.add_handler('text exception', 'test error msg', ValueError)
        assert not el.handle_exception(Exception('text exception'))
        self.assertEqual(len(el.errors), 0)
        
        # wrong message
        form = Form('f')
        el = form.add_element('text', 'field', 'Field')
        el.add_handler('text exception', 'test error msg', Exception)
        assert not el.handle_exception(Exception('text'))
        self.assertEqual(len(el.errors), 0)
        
    def test_conversion(self):
        # without form submission, we get empty value
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', 'bool')
        self.assertEqual( el.value, None)
        
        # default values do not get processed, they are for display only
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', 'bool', '1')
        self.assertEqual( el.value, None)
        
        # submission gets converted
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', 'bool')
        el.submittedval = '1'
        self.assertEqual( el.value, True)
        
        # conversion turned off
        form = Form('f')
        el = form.add_element('text', 'field', 'Field')
        el.submittedval = '1'
        self.assertEqual( el.value, '1')
        
        # conversion with if_empty
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', 'bool', if_empty=False)
        el.submittedval = '1'
        self.assertEqual( el.value, True)
        
        # conversion with if_empty
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', 'bool', if_empty=False)
        el.submittedval = None
        self.assertEqual( el.value, False)
        
        # conversion with if_empty
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', 'bool', if_empty=True)
        el.submittedval = False
        self.assertEqual( el.value, False)
        
        # conversion with if_empty
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', 'bool', if_empty='1')
        self.assertEqual( el.value, True)
        
    def test_type_strings(self):

        form = Form('f')
        form.add_element('text', 'f1', 'Field', 'bool', if_empty='1.25')
        self.assertEqual(form.f1.value, True)
        form.add_element('text', 'f2', 'Field', 'boolean', if_empty='1.25')
        self.assertEqual(form.f2.value, True)
        form.add_element('text', 'f3', 'Field', 'int', if_empty='1')
        self.assertEqual(form.f3.value, 1)
        form.add_element('text', 'f4', 'Field', 'integer', if_empty='1')
        self.assertEqual(form.f4.value, 1)
        form.add_element('text', 'f5', 'Field', 'num', if_empty='1.25')
        self.assertEqual(form.f5.value, 1.25)
        form.add_element('text', 'f6', 'Field', 'number', if_empty='1.25')
        self.assertEqual(form.f6.value, 1.25)
        form.add_element('text', 'f7', 'Field', 'float', if_empty='1.25')
        self.assertEqual(form.f7.value, 1.25)
        form.add_element('text', 'f8', 'Field', 'str', if_empty='1.25')
        self.assertEqual(form.f8.value, '1.25')
        form.add_element('text', 'f9', 'Field', 'string', if_empty='1.25')
        self.assertEqual(form.f9.value, '1.25')
        form.add_element('text', 'f10', 'Field', 'uni', if_empty='1.25')
        self.assertEqual(form.f10.value, u'1.25')
        form.add_element('text', 'f11', 'Field', 'unicode', if_empty='1.25')
        self.assertEqual(form.f11.value, u'1.25')
        form.add_element('text', 'f12', 'Field', 'bool', if_empty='false')
        self.assertEqual(form.f12.value, False)
        
        # test invalid vtype
        form = Form('f')
        try:
            form.add_text('f1', 'Field', 'badvtype')
        except ValueError, e:
            self.assertEqual('invalid vtype "badvtype"', str(e))
            
        # test wrong type of vtype
        try:
            form.add_text('f2', 'Field', ())
        except TypeError, e:
            self.assertEqual('vtype should have been a string, got <type \'tuple\'> instead', str(e))
    #
    #def from_python_exception(self):
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
        el = form.add_element('text', 'field', 'Field')
        self.assertEqual(str(el()), html)
        
        html = '<input class="text" id="f-field" maxlength="1" name="field" type="text" />'
        form = Form('f')
        el = form.add_element('text', 'field', 'Field', maxlength=1)
        self.assertEqual(str(el()), html)
        el.submittedval = '1'
        self.assertEqual( el.value, '1')
        
        # too long
        el.submittedval = '12'
        self.assertEqual( el.is_valid(), False)
        
        # no validator
        form = Form('f')
        el = form.add_element('text', 'field', 'Field')        
        el.submittedval = '12'
        self.assertEqual( el.value, '12')
        
    def test_el_confirm(self):
        try:
            Form('f').add_confirm('f')
            self.fail('expected key error for missing "match"')
        except KeyError:
            pass
        
        html = '<input class="text" id="f-f" name="f" type="text" />'
        f = Form('f')
        pel = f.add_password('p', 'password')
        cel = f.add_confirm('f', match='p')
        self.assertEqual(str(cel()), html)
        pel.submittedval = 'foo'
        cel.submittedval = 'foo'
        assert cel.is_valid()
        pel.submittedval = 'bar'
        cel.submittedval = 'foo'
        assert not cel.is_valid()
        assert cel.errors[0] == 'does not match field "password"'

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
        el = Form('f').add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3), month_style='dd/mm/yyyy')
        self.assertEqual(str(el()), html)
        el.submittedval = '1/5/09'
        assert el.value == datetime.date(2009, 5, 1)
        el.submittedval = '2-30-04'
        assert not el.is_valid()
        
        # no-day dates
        html = '<input class="text" id="f-field" name="field" type="text" value="12/2009" />'
        el = Form('f').add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3), accept_day=False)
        self.assertEqual(str(el()), html)
        el.submittedval = '5/09'
        assert el.value == datetime.date(2009, 5, 1)
        el.submittedval = '5/1/09'
        assert not el.is_valid()

    def test_el_email(self):
        html = '<input class="text" id="f-field" name="field" type="text" />'
        el = Form('f').add_email('field', 'Field')
        self.assertEqual(str(el()), html)
        el.submittedval = 'bob@example.com'
        assert el.value == 'bob@example.com'
        el.submittedval = 'bob'
        assert not el.is_valid()
        
        try:
            el = Form('f').add_email('field', 'Field', resolve_domain=True)
            el.submittedval = 'bob@ireallyhopethisdontexistontheweb.com'
            assert not el.is_valid()
        except ImportError:
            warnings.warn('skipping test b/c pyDNS not installed')
        
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
        assert el.value == (20,30)
        
        # some validator options
        html = '<input class="text" id="f-field" name="field" type="text" value="1:00pm" />'
        el = Form('f').add_time('field', 'Field', defaultval=(13, 0), use_ampm=True, use_seconds=False)
        self.assertEqual(str(el()), html)
        el.submittedval = '8:30pm'
        assert el.value == (20,30)

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
        
        # value
        el = Form('f').add_select('f', o, if_empty=1)
        self.assertEqual(el.value, 1)
        el = Form('f').add_select('f', o, if_empty='1')
        self.assertEqual(el.value, '1')
        el = Form('f').add_select('f', o, if_empty=3)
        assert not el.is_valid()
        self.assertEqual( el.errors[0], 'the value did not come from the given options')
        
        # no auto validate
        el = Form('f').add_select('f', o, if_empty=3, auto_validate=False)
        assert el.is_valid()
        
        # conversion
        el = Form('f').add_select('f', o, vtype='int', if_empty='1')
        self.assertEqual(el.value, 1)
        
        # custom error message
        el = Form('f').add_select('f', o, if_empty=3, error_msg='test')
        assert not el.is_valid()
        self.assertEqual( el.errors[0], 'test')
        
        # choose values are invalid only if a value is required
        el = Form('f').add_select('f', o, if_empty=-2)
        assert el.is_valid()
        el = Form('f').add_select('f', o, if_empty=-2, required=True)
        assert not el.is_valid()
        
        # custom invalid values
        el = Form('f').add_select('f', o, if_empty=1, invalid=['2'])
        assert el.is_valid()
        el = Form('f').add_select('f', o, if_empty=1, invalid=['1', '2'])
        assert not el.is_valid()
        el = Form('f').add_select('f', o, if_empty=1, invalid=1)
        assert not el.is_valid()
        
        # not submitted value when not required
        el = Form('f').add_select('f', o)
        el.is_valid()
        assert el.is_valid()
        assert el.value is NotGiven
        
        # "empty" value when required, but there is an empty value in the
        # options.  It seems that required meaning 'must not be empty' should
        # take precidence.
        el = Form('f').add_select('f', o+[('', 'blank')], if_empty='', required=True)
        assert not el.is_valid()

        # make sure choose values do not get returned when required=False
        el = Form('f').add_select('f', o, if_empty=1)
        el.submittedval = -1
        self.assertEqual(el.value, 1)
        el = Form('f').add_select('f', o)
        el.submittedval = -1
        self.assertEqual(el.value, None)
        
        # make sure we do not accept multiple values if we aren't a multi
        # select
        el = Form('f').add_select('f', o, if_empty=[1,2])
        assert not el.is_valid()
        
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
        el = Form('f').add_mselect('f', o, defaultval=[1,3], choose=None)
        self.assertEqual(str(el()), html)
        
        # multiple default values
        html = \
        '<select id="f-f" multiple="multiple" name="f">\n'\
        '<option selected="selected" value="1">a</option>\n'\
        '<option selected="selected" value="2">'\
        'b</option>\n</select>'
        el = Form('f').add_mselect('f', o, defaultval=(1,2), choose=None)
        self.assertEqual(str(el()), html)
        el = Form('f').add_mselect('f', o, defaultval=[1,2], choose=None)
        self.assertEqual(str(el()), html)
    
    def test_el_select_multi1(self):
        o = [(1, 'a'), (2, 'b')]
        # value
        el = Form('f').add_mselect('f', o, if_empty=1)
        self.assertEqual(el.value, [1])
        el = Form('f').add_mselect('f', o, if_empty=1, auto_validate=False)
        self.assertEqual(el.value, [1])
        el = Form('f').add_mselect('f', o, if_empty=[1,2])
        self.assertEqual(el.value, [1,2])
        el = Form('f').add_mselect('f', o, if_empty=['1','2'])
        self.assertEqual(el.value, ['1', '2'])
        el = Form('f').add_mselect('f', o, if_empty=[1,3])
        assert not el.is_valid()
        self.assertEqual( el.errors[0], 'the value did not come from the given options')
        
        # no auto validate
        el = Form('f').add_mselect('f', o, if_empty=[1,3], auto_validate=False)
        assert el.is_valid()
        self.assertEqual(el.value, [1,3])
        
        # conversion
        el = Form('f').add_mselect('f', o, vtype='int', if_empty=['1',2])
        self.assertEqual(el.value, [1, 2])
        
        # choose values are invalid only if a value is required
        el = Form('f').add_mselect('f', o, if_empty=(-2,1))
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
        assert el.value is NotGivenIter
        for v in el.value:
            self.fail('should emulate empty')
        else:
            assert True, 'should emulate empty'
        assert el.value == []
        
        # "empty" value when required, but there is an empty value in the
        # options.  It seems that required meaning 'must not be empty' should
        # take precidence.
        el = Form('f').add_mselect('f', o+[('', 'blank')], if_empty='', required=True)
        assert not el.is_valid()
        
        # make sure choose values do not get returned when required=False
        el = Form('f').add_mselect('f', o, if_empty=1)
        el.submittedval = [-2, -1]
        self.assertEqual(el.value, 1)
        el = Form('f').add_mselect('f', o)
        el.submittedval = [-1, -2]
        self.assertEqual(el.value, [])
        el = Form('f').add_mselect('f', o)
        el.submittedval = [-1, 1]
        self.assertEqual(el.value, [1])
        
class OtherElementsTest(unittest.TestCase):
    def test_el_textarea(self):
        html = '<textarea class="foo" cols="40" id="f-f" name="f" rows="7"></textarea>'
        el = Form('f').add_textarea('f')
        self.assertEqual(str(el(class_='foo')), html)
        html = '<textarea cols="40" id="f-f" name="f" rows="7">foo</textarea>'
        el = Form('f').add_textarea('f', defaultval='foo')
        self.assertEqual(str(el()), html)
        
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
        f.set_submitted({'f':'bar', 'text':'baz', 'f-submit-flag':'submitted'})
        self.assertEqual(f.values, {'f':'foo', 'text':'baz', 'f-submit-flag':'submitted'})
        
        # need to test defaulting, passthru should also pick that up
        f = Form('f')
        f.add_text('text')
        el = f.add_passthru('f')
        f.set_defaults({'f':'foo'})
        f.set_submitted({'f':'bar', 'text':'baz', 'f-submit-flag':'submitted'})
        self.assertEqual(f.values, {'f':'foo', 'text':'baz', 'f-submit-flag':'submitted'})
    
    def test_el_fixed(self):
        f = Form('f')
        el = f.add_fixed('f', defaultval='foo', title='baz')
        self.assertEqual( el(class_='bar'), L('<div class="bar" id="f-f" title="baz">foo</div>'))
        
        # we want to be able to use a label on fixed elements
        f = Form('f')
        el = f.add_fixed('f', 'Foo', 'foo', title='baz')
        self.assertEqual( el.label(), L('<label>Foo</label>'))
        self.assertEqual( el(class_='bar'), L('<div class="bar" id="f-f" title="baz">foo</div>'))
        
        
    def test_el_static(self):
        f = Form('f')
        f.add_text('text')
        el = f.add_static('f', 'label', 'foo')
        assert el.render() == L('<div id="f-f">foo</div>')
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
        f.set_submitted({'f':'bar', 'text':'baz', 'f-submit-flag':'submitted'})
        self.assertEqual(f.values, {'text':'baz', 'f-submit-flag':'submitted'})
        
        # need to test defaulting, passthru should also pick that up
        f = Form('f')
        f.add_text('text')
        el = f.add_static('f', 'label')
        f.set_defaults({'f':'foo'})
        self.assertEqual(el(), L('<div id="f-f">foo</div>'))
    
    def test_el_header(self):
        el = Form('f').add_header('f', 'heading')
        assert el.render() == L('<h3 id="f-f">heading</h3>')
    
        # different header
        el = Form('f').add_header('f', 'heading', 'h2')
        assert el.render() == L('<h2 id="f-f">heading</h2>')
        
        # with attributes
        el = Form('f').add_header('f', 'foo', title='baz')
        self.assertEqual( el(class_='bar'), L('<h3 class="bar" id="f-f" title="baz">foo</h3>'))

class LogicalElementsTest(unittest.TestCase):
    
    def test_mcheckbox(self):
        not_checked = L('<input class="checkbox" id="f-f" name="thegroup" type="checkbox" />')
        checked = L('<input checked="checked" class="checkbox" id="f-f" name="thegroup" type="checkbox" />')

        el = Form('f').add_mcheckbox('f', 'label', group='thegroup' )
        self.assertEqual(el(), not_checked)
        el = Form('f').add_mcheckbox('f', 'label', group='thegroup', checked=True)
        self.assertEqual(el(), checked)
        el = Form('f').add_mcheckbox('f', 'label', group='thegroup')
        self.assertEqual(el(checked='checked'), checked)
        
        not_checked = L('<input class="checkbox" id="f-f" name="thegroup" type="checkbox" value="foo" />')
        checked = L('<input checked="checked" class="checkbox" id="f-f" name="thegroup" type="checkbox" value="foo" />')

        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(), not_checked)
        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup', checked=True)
        self.assertEqual(el(), checked)
        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(checked='checked'), checked)
        el = Form('f').add_mcheckbox('f', 'label', 'foo', 'thegroup')
        el.chosen = True
        self.assertEqual(el(), checked)
        
        # can't have to elements in same group with same value
        f = Form('f')
        el1 = f.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
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
        el.form.set_submitted({'f':'test'})
        
        # test the elements getting chosen by setting form defaults
        f = Form('f')
        el1 = f.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
        el2 = f.add_mcheckbox('f2', 'label', 'bar', 'thegroup')
        assert el1.chosen == el2.chosen == False
        f.set_defaults({'thegroup':'foo'})
        assert el1.chosen
        assert not el2.chosen
        f.set_defaults({'thegroup':['foo', 'bar']})
        assert el1.chosen
        assert el2.chosen
        # it was chosen, but should "undo" when set again
        f.set_defaults({'thegroup':'foo'})
        assert el1.chosen
        assert not el2.chosen
        
        # test the elements getting chosen by form submissions
        f = Form('f')
        el1 = f.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
        el2 = f.add_mcheckbox('f2', 'label', 'bar', 'thegroup')
        assert el1.chosen == el2.chosen == False
        f.set_submitted({'thegroup':'foo'})
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'thegroup':['foo', 'bar']})
        assert el1.chosen
        assert el2.chosen
        # it was chosen, but should "undo" when set again
        f.set_submitted({'thegroup':'foo'})
        assert el1.chosen
        assert not el2.chosen
    
    def test_mcheckbox2(self):
        # test integer values
        f = Form('f')
        el1 = f.add_mcheckbox('f1', 'label', 1, 'thegroup')
        el2 = f.add_mcheckbox('f2', 'label', 2, 'thegroup')
        assert el1.chosen == el2.chosen == False
        f.set_submitted({'thegroup':1})
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'thegroup':'1'})
        assert el1.chosen
        assert not el2.chosen
        f.set_submitted({'thegroup':[1, '2']})
        assert el1.chosen
        assert el2.chosen
        
    def test_radio(self):
        not_selected= L('<input class="radio" id="f-f" name="thegroup" type="radio" />')
        selected = L('<input class="radio" id="f-f" name="thegroup" selected="selected" type="radio" />')

        el = Form('f').add_radio('f', 'label', group='thegroup' )
        self.assertEqual(el(), not_selected)
        el = Form('f').add_radio('f', 'label', group='thegroup', selected=True)
        self.assertEqual(el(), selected)
        el = Form('f').add_radio('f', 'label', group='thegroup')
        self.assertEqual(el(selected='selected'), selected)
        
        not_selected= L('<input class="radio" id="f-f" name="thegroup" type="radio" value="foo" />')
        selected = L('<input class="radio" id="f-f" name="thegroup" selected="selected" type="radio" value="foo" />')

        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(), not_selected)
        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup', selected=True)
        self.assertEqual(el(), selected)
        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup')
        self.assertEqual(el(selected='selected'), selected)
        el = Form('f').add_radio('f', 'label', 'foo', 'thegroup')
        el.chosen = True
        self.assertEqual(el(), selected)

    def test_dup_values(self):
        f = Form('f')
        el = f.add_radio('radio1', 'Radio 1', group='rgroup1' )
        try:
            el = f.add_radio('radio2', 'Radio 2', group='rgroup1' )
            self.fail('should have got duplicate value assertion')
        except ValueError, e:
            self.assertEqual(str(e), 'a member of this group already exists with value "None"')
    
    def test_non_rendering(self):
        f = Form('f')
        el = f.add_radio('radio1', 'Radio 1', group='rgroup1' )
        assert el.lgroup not in f.render_els, 'logical group is trying to render'
    
class LogicalElementsTest2(unittest.TestCase):
    def setUp(self):
        self.f = f = Form('f')
        self.el1 = f.add_mcheckbox('f1', 'label', 1, 'thegroup')
        self.el2 = f.add_mcheckbox('f2', 'label', 2, 'thegroup')
        self.el3 = f.add_mcheckbox('f3', 'label', 3, 'thegroup')
        self.el3 = f.add_mcheckbox('f4', 'label', '', 'thegroup')
        self.gel = f.thegroup
        
    def test_1(self):
        self.gel.if_empty=1
        self.assertEqual(self.gel.value, [1])

    def test_2(self):
        self.gel.if_empty=[1,2]
        self.assertEqual(self.gel.value, [1,2])

    def test_3(self):
        self.gel.if_empty=['1', '2']
        self.assertEqual(self.gel.value, ['1', '2'])

    def test_4(self):
        self.gel.if_empty=[1,4]
        assert not self.gel.is_valid()
        self.assertEqual(self.gel.errors[0], 'the value did not come from the given options')

    def test_5(self):
        self.gel.if_empty=[1,4]
        self.gel.auto_validate = False
        assert self.gel.value == [1,4]

    def test_6(self):
        # custom error message
        self.gel.if_empty=[1,4]
        self.gel.error_msg = 'test'
        assert not self.gel.is_valid()
        self.assertEqual(self.gel.errors[0], 'test')

    def test_7(self):
        # conversion
        self.gel.if_empty=['1', 2]
        self.gel.vtype = 'int'
        self.assertEqual(self.gel.value, [1, 2])

    def test_8(self):
        # custom invalid values
        self.gel.if_empty=(1, 2)
        self.gel.invalid = ['3']
        assert self.gel.is_valid()

    def test_9(self):
        # custom invalid values
        self.gel.if_empty=(1, 2)
        self.gel.invalid = '3'
        assert self.gel.is_valid()
        
    def test_10(self):
        # custom invalid values
        self.gel.if_empty=(1, 2)
        self.gel.invalid = ['2']
        assert not self.gel.is_valid()

    def test_11(self):
        # custom invalid values
        self.gel.if_empty=(1, 2)
        self.gel.invalid = '2'
        assert not self.gel.is_valid()
        
    def test_12(self):
        # custom invalid values
        self.gel.if_empty=(1, 2)
        self.gel.invalid = ['2','3']
        assert not self.gel.is_valid()
        
    def test_13(self):
        # not submitted value when not required is OK.
        # Should return NotGivenIter
        self.gel.is_valid()
        assert self.gel.is_valid()
        
    def test_14(self):
        # value required
        self.gel.required=True
        assert not self.gel.is_valid()
        
    def test_15(self):
        # "empty" value when required, but there is an empty value in the
        # options.  It seems that required meaning 'must not be empty' should
        # take precidence.
        self.gel.required=True
        self.gel.if_empty=''
        assert not self.gel.is_valid()
        
    def test_16(self):
        # custom processor
        def validator(value):
            raise ValueError('test')
        self.gel.if_empty = 1
        self.gel.add_processor(validator)
        assert not self.gel.is_valid()
    

# need to test adding group first and then members
# test setting attributes for each element with a render()
# from_python_exception test needs to be created
