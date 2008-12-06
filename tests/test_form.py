import unittest
from webhelpers.html.builder import literal

from pysform import Form
from pysform.element import TextElement

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
        form.add_element('text', 'username', 'User Name')
        self.assertEqual(self.render_html, str(form.username.render()))

    def testForm4(self):
        form = Form('login')
        el = form.add_text('username', 'User Name')
        self.assertEqual(self.render_html, str(form.username.render()))
        self.assertEqual(self.render_html, str(el.render()))
    
    def testForm5(self):
        """ensure form has correct encoding for file uploads"""
        
        f1 = Form('login')
        f1.add_text('username', 'User Name')
        assert "multipart/form-data" not in f1.render()
        
        f2 = Form('pictures')
        f2.add_file('picture', 'Picture')
        assert "multipart/form-data" in f2.render()
        
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
        f.add_element('text', 'username', 'User Name')
        f.set_defaults({'username':'test1'})
        #post = {'login-submit-flag': 'submitted'}
        #f.set_submitted(post)
        self.assertEqual('<input class="text" id="login-username" name="username" type="text" value="test1" />', str(f.username.render()))
        
    def test_submit(self):
        f = Form('login')
        f.add_element('text', 'username', 'User Name')
        f.set_defaults({'username':'test1'})
        post = {'login-submit-flag': 'submitted', 'username':'test2'}
        f.set_submitted(post)
        self.assertEqual('<input class="text" id="login-username" name="username" type="text" value="test2" />', str(f.username.render()))
    
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