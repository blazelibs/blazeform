import unittest
from pysform.util import multi_pop, NotGiven, is_iterable, NotGivenIter, \
    is_notgiven

class CommonFormUsageTest(unittest.TestCase):

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