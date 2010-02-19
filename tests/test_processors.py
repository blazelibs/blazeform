from formencode.validators import MaxLength
from formencode import Invalid

def test_maxlength_bug_fix():
    assert MaxLength._messages['__buggy_toolong'] == "Enter a value less than %(maxLength)i characters long", 'looks like formencode may have fixed the MaxLength message bug'
    ml = MaxLength(5)
    ml.to_python('12345')
    try:
        ml.to_python('123456')
        assert False, 'expected exception'
    except Invalid, e:
        assert str(e) == 'Enter a value not greater than 5 characters long'