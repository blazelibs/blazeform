import datetime
from blazeform import Form

class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'withactionform', action='/submitto')
        el = self.add_text('text', 'Text')