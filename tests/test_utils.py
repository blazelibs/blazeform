import unittest
from pysform.util import multi_pop, NotGiven, is_iterable, NotGivenIter, \
    is_notgiven, HtmlAttributeHolder

class TestUtilFunctions(unittest.TestCase):

    def test_multi_pop(self):
        start = {'a':1, 'b':2, 'c':3}
        assert {'a':1, 'c':3} == multi_pop(start, 'a', 'c')
        assert start == {'b':2}
        
    def test_notgiven(self):
        assert not None
        assert not NotGiven
        assert NotGiven != False
        assert None != False
        assert NotGiven is NotGiven
        assert NotGiven == NotGiven
        assert None is not NotGiven
        assert None == NotGiven
        assert not None != NotGiven
        assert NotGiven == None
        assert str(NotGiven) == 'None'
        assert unicode(NotGiven) == u'None'
    
    def test_notgiveniter(self):
        assert not NotGivenIter
        assert NotGivenIter != False
        assert NotGivenIter is NotGivenIter
        assert NotGivenIter == NotGivenIter
        assert NotGivenIter == NotGiven
        assert NotGiven == NotGivenIter
        assert not [] != NotGivenIter
        assert NotGivenIter == []
        assert str(NotGivenIter) == '[]'
        assert unicode(NotGivenIter) == u'[]'
        assert is_iterable(NotGivenIter)
        assert len(NotGivenIter) == 0

        for v in NotGivenIter:
            self.fail('should emulate empty')
        else:
            assert True, 'should emulate empty'
        
    def test_is_iterable(self):
        assert is_iterable([])
        assert is_iterable(tuple())
        assert is_iterable({})
        assert not is_iterable('asdf')
        
    def test_is_notgiven(self):
        assert is_notgiven(NotGiven)
        assert is_notgiven(NotGivenIter)
        assert not is_notgiven(None)

class TestHtmlAttributeHolder(unittest.TestCase):
    def test_init(self):
        ah = HtmlAttributeHolder(src='src', class_='class')
        assert ah.attributes['src'] == 'src'
        assert ah.attributes['class'] == 'class'

    def test_set_attrs(self):
        ah = HtmlAttributeHolder()
        ah.set_attrs(src='src', class_='class')
        assert ah.attributes['src'] == 'src'
        assert ah.attributes['class'] == 'class'

    def test_set_attr(self):
        ah = HtmlAttributeHolder()
        ah.set_attr('src', 'src')
        ah.set_attr('class_', 'class')
        assert ah.attributes['src'] == 'src'
        assert ah.attributes['class'] == 'class'
        
        ah.set_attr('class_', 'class2')
        assert ah.attributes['class'] == 'class2'
    
    def test_get_attr(self):
        ah = HtmlAttributeHolder(src='src', class_='class')
        assert ah.get_attr('src') == 'src'
        assert ah.get_attr('class') == 'class'
        assert ah.get_attr('class_') == 'class'
        
    def test_del_attr(self):
        ah = HtmlAttributeHolder(src='src', class_='class')
        ah.del_attr('src')
        ah.del_attr('class')
        assert not ah.attributes.has_key('src')
        assert not ah.attributes.has_key('class')
    
    def test_add_attr(self):
        ah = HtmlAttributeHolder(src='src', class_='class')
        ah.add_attr('class_', 'class2')
        assert ah.attributes['src'] == 'src'
        assert ah.attributes['class'] == 'class class2'

    
