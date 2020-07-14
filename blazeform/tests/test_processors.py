from blazeutils.testing import raises
from decimal import Decimal
from formencode import Invalid
from formencode.validators import MaxLength

from blazeform.processors import Decimal as DecimalProc


def test_maxlength_bug_fix():
    assert MaxLength._messages['__buggy_toolong'] == "Enter a value less than %(maxLength)i " \
        "characters long", 'looks like formencode may have fixed the MaxLength message bug'
    ml = MaxLength(5)
    ml.to_python('12345')
    try:
        ml.to_python('123456')
        assert False, 'expected exception'
    except Invalid as e:
        assert str(e) == 'Enter a value not greater than 5 characters long'


def test_decimal():
    proc = DecimalProc()

    @raises(Invalid, 'Not a valid number')
    def check():
        proc.to_python('foo')
    check()

    assert proc.to_python('1.123') == Decimal('1.123')
