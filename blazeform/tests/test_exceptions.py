from blazeform.exceptions import ValueInvalid


def test_invalid_str():
    e = ValueInvalid('foo')
    assert str(e) == 'foo'


def test_invalid_exc():
    e = ValueInvalid(ValueError('foo'))
    assert str(e) == 'foo'
