import unittest
from decimal import Decimal

from blazeform.util import (
    HtmlAttributeHolder,
    NotGiven,
    NotGivenIter,
    is_empty,
    is_iterable,
    is_notgiven,
    multi_pop,
    tolist,
)


class TestUtilFunctions(unittest.TestCase):

    def test_multi_pop(self):
        start = {'a': 1, 'b': 2, 'c': 3}
        assert {'a': 1, 'c': 3} == multi_pop(start, 'a', 'c')
        assert start == {'b': 2}

    def test_notgiven(self):
        assert not NotGiven
        assert NotGiven != False  # noqa
        assert NotGiven == ''
        assert NotGiven == u''
        assert NotGiven is NotGiven
        assert NotGiven == NotGiven
        assert str(NotGiven) == ''
        assert str(NotGiven) == u''

    def test_notgiveniter(self):
        assert not NotGivenIter
        assert NotGivenIter != False  # noqa
        assert NotGivenIter is NotGivenIter
        assert NotGivenIter == NotGivenIter
        assert NotGivenIter == NotGiven
        assert NotGiven == NotGivenIter
        assert not [] != NotGivenIter
        assert NotGivenIter == []
        assert str(NotGivenIter) == '[]'
        assert str(NotGivenIter) == u'[]'
        assert is_iterable(NotGivenIter)
        assert len(NotGivenIter) == 0

        for v in NotGivenIter:
            self.fail('should emulate empty')
        else:
            assert True, 'should emulate empty'

    def test_tolist(self):
        assert tolist([1, 2]) == [1, 2]
        assert tolist((1, 2)) == [1, 2]
        assert tolist(1) == [1]
        assert tolist(None) == []
        assert tolist(None, [1, 2]) == [1, 2]

    def test_tolist_nonmutable_default(self):
        x = tolist(None)
        assert x == []
        x.append(3)
        assert tolist(None) == []

    def test_is_iterable(self):
        assert is_iterable([])
        assert is_iterable(tuple())
        assert is_iterable({})
        assert not is_iterable('asdf')
        assert is_iterable(NotGivenIter)

    def test_is_notgiven(self):
        assert is_notgiven(NotGiven)
        assert is_notgiven(NotGivenIter)
        assert not is_notgiven(None)

    def test_is_empty(self):
        assert is_empty(NotGiven)
        assert is_notgiven(NotGivenIter)
        assert is_empty(None)
        assert is_empty('')
        assert is_empty([])
        assert is_empty({})
        assert is_empty(set())
        assert not is_empty('foo')
        assert not is_empty(False)
        assert not is_empty(0)
        assert not is_empty(0.0)
        assert not is_empty(Decimal(0))
        assert not is_empty([0])
        assert not is_empty({'foo': 'bar'})
        assert not is_empty({''})


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
        assert 'src' not in ah.attributes
        assert 'class' not in ah.attributes

    def test_add_attr(self):
        ah = HtmlAttributeHolder(src='src', class_='class')
        ah.add_attr('class_', 'class2')
        assert ah.attributes['src'] == 'src'
        assert ah.attributes['class'] == 'class class2'
