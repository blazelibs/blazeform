from __future__ import absolute_import
import datetime
from blazeform.form import Form

class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'withactionform', action='/submitto')
        el = self.add_text('text', 'Text')