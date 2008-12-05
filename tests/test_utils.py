import unittest
from pysform.util import multi_pop, NotGiven

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