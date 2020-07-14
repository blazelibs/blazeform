from __future__ import absolute_import
import datetime
from blazeform.form import Form


class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'testform')

        self.add_header('input-els', 'Optional Elements')
        self.add_button('button', 'Button', defaultval='PushMe')
        self.add_checkbox('checkbox', 'Checkbox')
        self.add_file('file', 'File')
        self.add_hidden('hidden', defaultval='my hidden val')
        self.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
        el = self.add_text('text', 'Text')
        el.add_note('a note')
        el.add_note('an <strong>HTML</strong> note', False)
        el = self.add_text('nolabel', defaultval='No Label')
        el.add_note('a note')
        self.add_password('password', 'Password')
        el = self.add_confirm('confirm', 'Confirm Password', match='password')
        el.add_note('confirm characters for password field are automatically masked')
        el = self.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
        el.add_note('note the automatic conversion from datetime object')
        emel = self.add_email('email', 'Email')
        el = self.add_confirm('confirmeml', 'Confirm Email', match=emel)
        el.add_note('note you can confirm with the name of the field or the element object')
        el.add_note('when not confirming password field, characters are not masked')
        self.add_time('time', 'Time')
        self.add_url('url', 'URL')
        options = [('1', 'one'), ('2', 'two')]
        self.add_select('select', options, 'Select')
        self.add_mselect('mselect', options, 'Multi Select')
        self.add_textarea('textarea', 'Text Area')
        self.add_fixed('fixed', 'Fixed', 'fixed val')
        self.add_fixed('fixed-no-label', defaultval='fixed no label')
        self.add_static('static', 'Static', 'static val')
        self.add_static('static-no-label', defaultval='static val no label')

        # want a header for div wrapping only, header element should not actually render
        self.add_header('header-for-div-wrap-only')
        self.add_text('hfdwo-t1', 'Text1')
        self.add_text('hfdwo-t2', 'Text2')

        # test header with blank text
        self.add_header('header-blank-text', '')
        self.add_text('hbt-t1', 'Text1')
        self.add_text('hbt-t2', 'Text2')

        # test element group with class attribute
        self.add_header('eg-class-attr', 'Element Group with Class Attribute')
        sg = self.add_elgroup('submit-group', class_='submit-only')
        sg.add_submit('preview', defaultval="Preview")
        el = sg.add_submit('submit')
        el.add_attr('class', 'customclass')
