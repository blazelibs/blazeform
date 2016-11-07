from __future__ import absolute_import
import datetime
from blazeform.form import Form


class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'testform', action='/toresult', method='post', static=True)

        self.add_button('button', 'Button', defaultval='PushMe')
        self.add_checkbox('checkbox', 'Checkbox')
        self.add_file('file', 'File')
        self.add_hidden('hidden', defaultval='my hidden val')
        self.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
        self.add_reset('reset')
        self.add_submit('submit')
        self.add_cancel('cancel')
        self.add_text('text', 'Text')
        # a little out of order
        self.add_password('password', 'Password')
        self.add_confirm('confirm', 'Confirm Password', match='password')
        self.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
        self.add_email('email', 'Email')
        self.add_time('time', 'Time')
        self.add_url('url', 'URL')
        options = [('1', 'one'), ('2', 'two')]
        self.add_select('select', options, 'Select')
        self.add_mselect('mselect', options, 'Multi Select')
        self.add_textarea('textarea', 'Text Area')
        self.add_passthru('passthru', 123)
        self.add_fixed('fixed', 'Fixed', 'fixed val')
        self.add_static('static', 'Static', 'static val')
        self.add_header('header', 'header')

        # test element group with class attribute
        sg = self.add_elgroup('group')
        sg.add_text('ingroup1', 'ingroup1')
        sg.add_text('ingroup2', 'ingroup2')

        self.add_mcheckbox('mcb1', 'mcb1', defaultval='red', group='mcbgroup')
        self.add_mcheckbox('mcb2', 'mcb2', defaultval='green', group='mcbgroup')

        self.add_radio('r1', 'r1', defaultval='truck', group='rgroup')
        self.add_radio('r2', 'r2', defaultval='car', group='rgroup')
