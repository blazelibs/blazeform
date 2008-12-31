
class ElementInvalid(Exception):
    def __init__(self, label):
        desc = '"value" attribute accessed, but element "%s" is invalid' % label
        Exception.__init__(self, desc)

class ValueInvalid(Exception):
    def __init__(self, desc):
        Exception.__init__(self, desc)