
class ElementInvalid(Exception):
    def __init__(self, label):
        des = '"value" attribute accessed, but element "%s" is invalid' % label
        Exception.__init__(self, des)