from __future__ import absolute_import
import datetime
from blazeform.form import Form

class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'reqnoteform')
        el = self.add_text('text', 'Text')
        el = self.add_header('header2', 'Header2')
        el = self.add_text('text2', 'Text2')
        
render_opts = {
    'req_note' : '<div class="req_note"><span class="star">*</span> = required field</div>',
    'req_note_pos' : 'form-top'
}