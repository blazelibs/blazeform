import unittest
from webhelpers.html.builder import literal
from pysutils import DumbObject

from pysform import Form
from pysform.element import TextElement
from pysform.util import NotGivenIter, literal

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
        self.assertEqual(self.render_html, str(form.username.render()))

    def testForm4(self):
        form = Form('login')
        el = form.add_text('username', 'User Name')
        self.assertEqual(self.render_html, str(form.username.render()))
        self.assertEqual(self.render_html, str(el.render()))
    
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
        f.set_defaults({'username':'test1', 'file':filesub})
        self.assertEqual('<input class="text" id="login-username" name="username" type="text" value="test1" />', str(f.username.render()))
        
    def test_submit(self):
        f = Form('login')
        f.add_text('username', 'User Name')
        f.set_defaults({'username':'test1'})
        post = {'login-submit-flag': 'submitted', 'username':'test2'}
        f.set_submitted(post)
        self.assertEqual('<input class="text" id="login-username" name="username" type="text" value="test2" />', str(f.username.render()))
        assert f.get_values() == {'username': 'test2', 'login-submit-flag': 'submitted'}
    
    def test_blank_checkbox(self):
        html = L('<input checked="checked" class="checkbox" id="login-disabled" name="disabled" type="checkbox" />')
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
        assert 'selected="selected"' in el1()
        assert 'selected="selected"' not in el2()
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

# run the tests if module called directly
if __name__ == "__main__":
    unittest.main()