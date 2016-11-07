from __future__ import absolute_import
from blazeform.form import Form


class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'withactionform', action='/submitto')
        self.add_text('text', 'Text')
