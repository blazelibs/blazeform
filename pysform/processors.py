from formencode.validators import *
from formencode import Invalid
from pysform.util import tolist, is_iterable, is_notgiven

class Select(FancyValidator):
    """
    Invalid if the value(s) did not come from the options or came from the
    invalid options list
    """
    
    invalid = []
    __unpackargs__ = ('options', 'invalid')
    messages = {
        'notthere': "the value did not come from the given options",
        'invalid': "the value chosen is invalid",
        }

    def validate_python(self, values, state):
        soptions = set([unicode(d[0]) for d in self.options])
        sinvalid = set([unicode(d) for d in tolist(self.invalid)])
        svalues = set([unicode(d) for d in tolist(values)])

        if len(sinvalid.intersection(svalues)) != 0:
            raise Invalid(self.message('invalid', state), values, state)

        if len(soptions.intersection(svalues)) != len(svalues):
            raise Invalid(self.message('notthere', state), values, state)
        
        return
    
class Confirm(FancyValidator):
    """
        Matches one field's value with another
    """
    
    __unpackargs__ = ('tomatch', )
    messages = {
        'notequal': 'does not match field "%(field)s"'
        }

    def validate_python(self, value, state):
        if self.tomatch.value != value:
            raise Invalid(self.message('notequal', state, field=str(self.tomatch.label)), value, state)

    
class MultiValues(FancyValidator):
    """
        Ensures that single value fields never get a list/tuple and therefore
        always return a non-iterable value.  For INTERNAL use.
    """
    
    multi_check = True
    __unpackargs__ = ('validator','multi_check')
    messages = {
        'nonmultiple': 'this field does not accept more than one value"'
        }
    
    def _to_python(self, value, state):
        field = state
        multiple = getattr(field, 'multiple', False)
        if self.multi_check:
            if not multiple:
                if is_iterable(value):
                    raise Invalid(self.message('nonmultiple', state), value, state)

        # now apply the validator to the value
        if not multiple or is_notgiven(value):
            return self.validator.to_python(value, state)
        else:
            retval = []
            for v in tolist(value):
                retval.append(self.validator.to_python(v, state))
            return retval

