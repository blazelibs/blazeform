from formencode.validators import Int
import unittest

from webhelpers2.html.builder import literal

from blazeform.form import Form
from blazeform.element import TextElement
from blazeform.exceptions import ValueInvalid, ElementInvalid, ProgrammingError
from blazeform.util import NotGiven
from blazeutils import DumbObject

L = literal


class TypeRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.f = Form('login')

    def tearDown(self):
        self.f = None

    def testRegisterElementType1(self):
        self.f.register_element_type('testtype', TextElement)
        self.assertEqual(TextElement, self.f._registered_types['testtype'])

    def testRegisterDuplicateElementType(self):
        self.f.register_element_type('testtype', TextElement)

        try:
            self.f.register_element_type('testtype', TextElement)
        except ValueError:
            pass
        else:
            self.fail("expected a ValueError")


class CommonFormUsageTest(unittest.TestCase):

    def setUp(self):
        self.render_html = '<input class="text" id="login-username" name="username" type="text" />'

    def testForm1(self):
        """
        most basic usage of a form
        """
        form = Form('login')
        form.add_text('username', 'User Name')
        self.assertEqual(self.render_html, str(form.elements.username.render()))

    def testForm4(self):
        form = Form('login')
        el = form.add_text('username', 'User Name')
        self.assertEqual(self.render_html, str(form.elements.username.render()))
        self.assertEqual(self.render_html, str(el.render()))

    def test_first_class_elements(self):
        """
        first element in form and under header should have a 'first' class
        """
        form_first_html = '<div id="user-username-row" class="text row odd first">'
        header_first_html = '<div id="user-groupname-row" class="text row even first">'
        form = Form('user')
        form.add_text('username', 'User Name')
        form.add_header('group_membership_header', 'Group Membership')
        form.add_text('groupname', 'Group')
        form_html = form.render()
        assert form_html.find(form_first_html) > -1
        assert form_html.find(header_first_html) > -1

    def test_formencoding(self):
        """ensure form has correct encoding for file uploads"""

        f1 = Form('login')
        f1.add_text('username', 'User Name')
        assert "multipart/form-data" not in f1.render()

        f2 = Form('pictures')
        f2.add_file('picture', 'Picture')
        assert "multipart/form-data" in f2.render()

        # make sure this works with grouped elements
        f = Form('f')
        fg = f.add_elgroup('file-group')
        fg.add_file('picture', 'Picture')
        assert "multipart/form-data" in f.render()

    def test_submit_validation(self):
        f1 = Form('login')
        assert "login-submit-flag" in f1.render()

    def test_is_submit(self):
        f1 = Form('login')
        assert not f1.is_submitted()

        post = {'login-submit-flag': 'submitted'}
        f1.set_submitted(post)
        assert f1.is_submitted()

    def test_is_cancel(self):
        f1 = Form('login')
        f1.add_cancel('cancel', 'Cancel')
        assert not f1.is_cancel()

        # cancel button, but form is not submitted
        post = {'cancel': 'submitted'}
        f1.set_submitted(post)
        assert not f1.is_cancel()

        # now submit form
        post['login-submit-flag'] = 'submitted'
        f1.set_submitted(post)
        assert f1.is_cancel()

    def test_default(self):
        f = Form('login')
        f.add_text('username', 'User Name')
        f.add_file('file')
        filesub = DumbObject(filename='text.txt', content_type='text/plain', content_length=10)
        f.set_defaults({'username': 'test1', 'file': filesub})
        self.assertEqual(
            '<input class="text" id="login-username" name="username" type="text" value="test1" />',
            str(f.elements.username.render())
        )

    def test_submit(self):
        f = Form('login')
        f.add_text('username', 'User Name')
        f.set_defaults({'username': 'test1'})
        post = {'login-submit-flag': 'submitted', 'username': 'test2'}
        f.set_submitted(post)
        self.assertEqual(
            '<input class="text" id="login-username" name="username" type="text" value="test2" />',
            str(f.elements.username.render())
        )
        assert f.get_values() == {'username': 'test2', 'login-submit-flag': 'submitted'}

    def test_submit_by_name(self):
        f = Form('login')
        f.add_text('username', 'User Name')
        f.add_submit('submit')
        post = {'login-submit-flag': 'submitted', 'username': 'test2', 'submit': 'Submit'}
        f.set_submitted(post)
        assert f.get_values() == {'username': 'test2', 'login-submit-flag': 'submitted',
                                  'submit': 'Submit'}

        f = Form('login')
        f.add_text('username', 'User Name', name="unfield")
        f.add_submit('submit', name="submitbtn")
        post = {'login-submit-flag': 'submitted', 'unfield': 'test2', 'submitbtn': 'Submit'}
        f.set_submitted(post)
        self.assertEqual(f.get_values(), {'unfield': 'test2', 'login-submit-flag': 'submitted',
                                          'submitbtn': 'Submit'})

    def test_blank_checkbox(self):
        html = L('<input checked="checked" class="checkbox" id="login-disabled" name="disabled" '
                 'type="checkbox" />')
        f = Form('login')
        el = f.add_checkbox('disabled', 'Disabled', defaultval=True)
        self.assertEqual(el(), html)
        post = {'login-submit-flag': 'submitted'}
        f.set_submitted(post)
        dvalue = f.get_values()['disabled']
        assert dvalue is False

        # should unset on re-post after a blank submit
        html = L('<input class="checkbox" id="login-disabled" name="disabled" type="checkbox" />')
        self.assertEqual(el(), html)

    def test_blank_checkbox_nameattr(self):
        html = L('<input checked="checked" class="checkbox" id="login-disabled" name="mycb" '
                 'type="checkbox" />')
        f = Form('login')
        el = f.add_checkbox('disabled', 'Disabled', defaultval=True, name="mycb")
        self.assertEqual(el(), html)
        post = {'login-submit-flag': 'submitted'}
        f.set_submitted(post)
        dvalue = f.get_values()['mycb']
        assert dvalue is False

        # should unset on re-post after a blank submit
        html = L('<input class="checkbox" id="login-disabled" name="mycb" type="checkbox" />')
        self.assertEqual(el(), html)

    def test_blank_multiselect(self):
        f = Form('login')
        options = [(1, 'one'), (2, 'two')]
        el = f.add_mselect('numlist', options, 'Disabled', defaultval=2)
        assert 'selected="selected"' in el()
        post = {'login-submit-flag': 'submitted'}
        f.set_submitted(post)
        assert not f.get_values()['numlist']

        # should unset on re-post after a blank submit
        assert 'selected="selected"' not in el()

    def test_blank_multicheckbox(self):
        f = Form('login')
        el1 = f.add_mcheckbox('mcheck1', 'Check 1', 1, 'cgroup1', checked=True)
        el2 = f.add_mcheckbox('mcheck2', 'Check 2', 2, 'cgroup1')
        assert 'checked="checked"' in el1()
        assert 'checked="checked"' not in el2()
        post = {'login-submit-flag': 'submitted'}
        f.set_submitted(post)
        assert not f.get_values()['cgroup1']

        # should unset on re-post after a blank submit
        assert 'checked="checked"' not in el1()
        assert 'checked="checked"' not in el2()

    def test_blank_radio(self):
        f = Form('login')
        el1 = f.add_radio('radio1', 'Radio 1', 1, 'rgroup1', selected=True)
        el2 = f.add_radio('radio2', 'Radio 2', 2, 'rgroup1')
        assert 'checked="checked"' in el1()
        assert 'checked="checked"' not in el2()
        post = {'login-submit-flag': 'submitted'}
        f.set_submitted(post)
        assert not f.get_values()['rgroup1']

        # should unset on re-post after a blank submit
        assert 'selected="selected"' not in el1()
        assert 'selected="selected"' not in el2()

    def test_dup_fields(self):
        f = Form('f')
        f.add_text('f')
        try:
            f.add_text('f')
            self.fail('should not be able to add elements with the same id')
        except ValueError:
            pass

    def test_is_valid(self):
        f = Form('f')
        f.add_text('f')
        # wasn't submitted, so not valid
        assert not f.is_valid()
        f.set_submitted({'f-submit-flag': 'submitted'})
        assert f.is_valid()

        f = Form('f')
        f.add_text('f', required=True)
        # wasn't submitted, so not valid
        assert not f.is_valid()
        f.set_submitted({'f-submit-flag': 'submitted'})
        assert not f.is_valid()
        f.set_submitted({'f-submit-flag': 'submitted', 'f': 'foo'})
        assert f.is_valid()

    def test_form_validators(self):
        def validator(form):
            if form.elements.myfield.is_valid():
                if form.elements.myfield.value != 'foo':
                    raise ValueInvalid('My Field: must be "foo", not "%s"' %
                                       form.elements.myfield.value)
        f = Form('f')
        f.add_text('myfield', 'My Field')
        f.add_validator(validator)
        f.set_submitted({'f-submit-flag': 'submitted', 'myfield': 'bar'})
        assert not f.is_valid()
        self.assertEqual(f._errors[0], 'My Field: must be "foo", not "bar"')
        f.set_submitted({'f-submit-flag': 'submitted', 'myfield': 'foo'})
        assert f.is_valid()
        assert len(f._errors) == 0

        # custom message
        f = Form('f')
        f.add_text('myfield', 'My Field')
        f.add_validator(validator, 'value incorrect')
        f.set_submitted({'f-submit-flag': 'submitted', 'myfield': 'bar'})
        assert not f.is_valid()
        self.assertEqual(f._errors[0], 'value incorrect')

    def test_validator_fe_class(self):
        form = Form('f')
        form.add_text('units', 'Units')
        form.add_validator(Int)
        assert isinstance(form._validators[0][0], Int)

    def test_validator_fe_instance(self):
        form = Form('f')
        form.add_text('units', 'Units')
        form.add_validator(Int())
        assert isinstance(form._validators[0][0], Int)

    def test_validator_recursion(self):
        """
            referencing .value from that field's validator causes a recursion
        """
        f = Form('f')

        def validator(form):
            try:
                f.elements.myfield.value
            except ElementInvalid as e:
                raise ValueInvalid(e)
        el = f.add_text('myfield', 'My Field', maxlength=1)
        el.add_processor(validator)
        f.set_submitted({'f-submit-flag': 'submitted', 'myfield': '12'})
        try:
            assert not f.is_valid()
        except RuntimeError as e:
            assert 'maximum recursion depth exceeded' in str(e), str(e)

    def test_validator_element_invalid(self):
        """
            If a validator references an invalid element, then we don't let
            that exception propogate
        """
        f = Form('f')

        def validator(form):
            f.elements.f1.value
        f.add_text('f1', 'f1', maxlength=1)
        f.add_text('f2', 'f2')
        f.add_validator(validator)
        f.set_submitted({'f-submit-flag': 'submitted', 'f1': '12'})
        assert not f.is_valid()

    def test_add_field_errors_string(self):
        form = Form('f')
        form.add_text('text1', 'Value')
        form.add_text('text2', 'Value')

        result = form.add_field_errors({
            'text1': 'Generic Error',
            'text2': 'Error'
        })
        assert result
        self.assertEqual(form.elements.text1.errors, ['Generic Error'])
        self.assertEqual(form.elements.text2.errors, ['Error'])

    def test_add_field_errors_list(self):
        form = Form('f')
        form.add_text('text1', 'Value')
        form.add_text('text2', 'Value')

        result = form.add_field_errors({
            'text1': ['Generic Error 1', 'Generic Error 2'],
            'text2': ['Error 1', 'Error 2']
        })
        assert result
        assert len(form.elements.text1.errors) == 2
        self.assertEqual(form.elements.text1.errors, ['Generic Error 1', 'Generic Error 2'])
        self.assertEqual(form.elements.text2.errors, ['Error 1', 'Error 2'])

    def test_add_field_errors_extras(self):
        # the result of calling add_field_errors() when all errors are not
        # processed should be False
        form = Form('f')
        form.add_text('text1', 'Value')
        form.add_text('text2', 'Value')

        result = form.add_field_errors({
            'text1': 'Generic Error',
            'text2': 'Error',
            'not there': 'Error'
        })
        assert result is False

    def test_exception_handling(self):
        # works with an element handler
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('text exception', 'test error msg')
        assert form.handle_exception(Exception('text exception'))
        self.assertEqual(el.errors[0], 'test error msg')

        # make sure exception on second field works
        form = Form('f')
        el = form.add_text('field', 'Field')
        el.add_handler('not it', '')
        el2 = form.add_text('field2', 'Field')
        el2.add_handler('text exception', 'test error msg')
        assert form.handle_exception(Exception('text exception'))
        self.assertEqual(el2.errors[0], 'test error msg')

        # form exceptions
        f = Form('f')
        f.add_handler('text exception', 'test error msg')
        assert f.handle_exception(Exception('text exception'))
        self.assertEqual(f._errors[0], 'test error msg')

        # make sure second exception works too
        f = Form('f')
        f.add_handler('not it', '')
        f.add_handler('text exception', 'test error msg')
        assert f.handle_exception(Exception('text exception'))
        self.assertEqual(f._errors[0], 'test error msg')

        # specifying exception type
        f = Form('f')
        f.add_handler('text exception', 'test error msg', Exception)
        assert f.handle_exception(Exception('text exception'))
        self.assertEqual(f._errors[0], 'test error msg')

        # right message, wrong type
        f = Form('f')
        f.add_handler('text exception', 'test error msg', ValueError)
        assert not f.handle_exception(Exception('text exception'))
        self.assertEqual(len(f._errors), 0)

        # wrong message
        f = Form('f')
        f.add_handler('text exception', 'test error msg', Exception)
        assert not f.handle_exception(Exception('text'))
        self.assertEqual(len(f._errors), 0)

    def test_submitted_only_when_appropriate(self):
        f1 = Form('login1')
        f1.add_text('field')
        f2 = Form('login2')
        f2.add_text('field')

        post = {
            'login1-submit-flag': 'submitted',
            'field': 'foo'
        }
        f1.set_submitted(post)
        assert f1.is_submitted()
        assert f1.elements.field.value == 'foo'

        f2.set_submitted(post)
        assert not f2.is_submitted()
        assert f2.elements.field.value is NotGiven

    def test_exception_on_static_submit(self):
        f1 = Form('login1', static=True)
        f1.add_text('field')
        post = {
            'login1-submit-flag': 'submitted',
            'field': 'foo'
        }
        try:
            f1.set_submitted(post)
            assert False, 'expected exception for submitting to static form'
        except ProgrammingError:
            pass

    def test_all_errors(self):
        def validator(form):
            if form.elements.myfield.is_valid():
                if form.elements.myfield.value != 'foo':
                    raise ValueInvalid('My Field: must be "foo", not "%s"' %
                                       form.elements.myfield.value)

        f1 = Form('login1')
        f1.add_text('field', 'Field', required=True)
        f1.add_text('myfield', 'My Field', required=True)
        f1.add_validator(validator)

        post = {
            'login1-submit-flag': 'submitted',
            'myfield': 'bar'
        }
        f1.set_submitted(post)
        assert not f1.is_valid()

        form_errors, field_errors = f1.all_errors()
        self.assertEqual(field_errors, {'Field': ['field is required']})
        self.assertEqual(form_errors, ['My Field: must be "foo", not "bar"'])

        # now make sure we can set the id as the field errors dict key if needed
        form_errors, field_errors = f1.all_errors(id_as_key=True)
        self.assertEqual(field_errors, {'field': ['field is required']})


# run the tests if module called directly
if __name__ == "__main__":
    unittest.main()
