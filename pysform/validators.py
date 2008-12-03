from formencode.validators import FancyValidator
from formencode import Invalid

class Select(FancyValidator):
    """
    Invalid if the value(s) did not come from the options or came from the
    invalid options list
    """
    
    invalid = []
    __unpackargs__ = ('options', 'invalid')
    messages = {
        'notthere': "the value did not come from the given options",
        'invalid': "the value chosen was invalid",
        }

    def validate_python(self, values, state):
        soptions = set([unicode(d[0]) for d in self.options])
        sinvalid = set(self.invalid)
        if isinstance(values, list):
            svalues = set(values)
        else:
            svalues = set([values])

        if len(sinvalid.intersection(svalues)) != 0:
            raise Invalid(self.message('invalid', state), values, state)

        if len(soptions.intersection(svalues)) != len(svalues):
            raise Invalid(self.message('notthere', state), values, state)
        
        return