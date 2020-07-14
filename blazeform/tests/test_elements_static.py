import datetime

from webhelpers2.html import literal

from blazeform.form import Form

L = literal


def test_el_button():
    el = Form('f', static=True).add_button('field', 'Field')
    assert el.render() == '', el.render()

    el = Form('f', static=True).add_button('field', 'Field', defaultval='the button')
    assert el.render() == '', el.render()


def test_el_checkbox():
    not_checked = '<span class="checkbox static" id="f-f">no</span>'
    checked = '<span class="checkbox static" id="f-f">yes</span>'

    # no default
    f = Form('f', static=True)
    el = f.add_checkbox('f', 'f')
    assert el.render() == not_checked, el.render()
    el.defaultval = True
    assert el.render() == checked, el.render()

    # checked attribute
    f = Form('f', static=True)
    el = f.add_checkbox('f', 'f', checked='checked')
    assert el.render(checked='checked') == checked, el.render(checked='checked')


def test_el_file():
    el = Form('f', static=True).add_file('f')
    assert el() == '', el()


def test_el_hidden():
    el = Form('f', static=True).add_hidden('f')
    assert el() == '', el()


def test_el_image():
    el = Form('f', static=True).add_image('f')
    assert el() == '', el()


def test_el_reset():
    el = Form('f', static=True).add_reset('f')
    assert el() == '', el()


def test_el_submit():
    el = Form('f', static=True).add_submit('f')
    assert el() == '', el()


def test_el_cancel():
    el = Form('f', static=True).add_cancel('f')
    assert el() == '', el()


def test_el_text():
    html = '<span class="text static" id="f-field">&nbsp;</span>'
    form = Form('f', static=True)
    el = form.add_text('field', 'Field')
    assert el() == html, el()

    form = Form('f', static=True)
    el = form.add_text('field', 'Field', maxlength=1)
    assert el() == html, el()

    html = '<span class="text static" id="f-field">one</span>'
    form = Form('f', static=True)
    el = form.add_text('field', 'Field', defaultval='one')
    assert el() == html, el()


def test_el_confirm():
    f = Form('f', static=True)
    f.add_password('p', 'password')
    cel = f.add_confirm('f', match='p')
    assert cel() == '', cel()


def test_el_date():
    html = '<span class="text static" id="f-field">&nbsp;</span>'
    el = Form('f', static=True).add_date('field', 'Field')
    assert el() == html, el()

    # our date-time object should get converted to the appropriate format
    html = '<span class="text static" id="f-field">12/03/2009</span>'
    el = Form('f', static=True).add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3))
    assert el() == html, el()

    # european style dates
    html = '<span class="text static" id="f-field">03/12/2009</span>'
    el = Form('f', static=True).add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3),
                                         month_style='dd/mm/yyyy')
    assert el() == html, el()


def test_el_email():
    html = '<span class="text static" id="f-field">bob@example.com</span>'
    el = Form('f', static=True).add_email('field', 'Field', defaultval='bob@example.com')
    assert el() == html, el()


def test_el_password():
    f = Form('f', static=True)
    el = f.add_password('p', 'password')
    assert el() == '', el()


def test_el_time():
    html = '<span class="text static" id="f-field">13:00:00</span>'
    el = Form('f', static=True).add_time('field', 'Field', defaultval=(13, 0))
    assert el() == html, el()


def test_el_url():
    html = '<span class="text static" id="f-f">&nbsp;</span>'
    el = Form('f', static=True).add_url('f')
    assert el() == html, el()

    html = '<span class="text static" id="f-f">example.org</span>'
    el = Form('f', static=True).add_url('f', defaultval="example.org")
    assert el() == html, el()

    html = '<span class="text static" id="f-f"><a href="http://example.org">' \
        'http://example.org</a></span>'
    el = Form('f', static=True).add_url('f', defaultval="http://example.org")
    assert el() == html, el()


def test_el_select_list_tuples():
    o = [(1, 'a'), (2, 'b')]
    html = '<span class="select" id="f-f">&nbsp;</span>'
    el = Form('f', static=True).add_select('f', o)
    assert el() == html, el()

    html = '<span class="select" id="f-f">a</span>'
    el = Form('f', static=True).add_select('f', o, defaultval=1)
    assert el() == html, el()
    el = Form('f', static=True).add_select('f', o, defaultval='1')
    assert el() == html, el()
    el = Form('f', static=True).add_select('f', o, defaultval=u'1')
    assert el() == html, el()


def test_el_select_list():
    o = ['foo', 'bar']
    html = '<span class="select" id="f-f">&nbsp;</span>'
    el = Form('f', static=True).add_select('f', o)
    assert el() == html, el()

    html = '<span class="select" id="f-f">foo</span>'
    el = Form('f', static=True).add_select('f', o, defaultval='foo')
    assert el() == html, el()
    el = Form('f', static=True).add_select('f', o, defaultval=u'foo')
    assert el() == html, el()

    html = '<span class="select" id="f-f">bar</span>'
    el = Form('f', static=True).add_select('f', o, defaultval='bar')
    assert el() == html, el()


def test_el_select_multiple():
    o = [(1, 'foo'), (2, 'bar')]
    html = '<span class="select" id="f-f">&nbsp;</span>'
    el = Form('f', static=True).add_select('f', o, multiple=True)
    assert el() == html, el()

    html = '<span class="select" id="f-f">foo</span>'
    el = Form('f', static=True).add_select('f', o, multiple=True, defaultval=1)
    assert el() == html, el()
    el = Form('f', static=True).add_select('f', o, multiple=True, defaultval='1')
    assert el() == html, el()
    el = Form('f', static=True).add_select('f', o, multiple=True, defaultval=u'1')
    assert el() == html, el()
    el = Form('f', static=True).add_select('f', o, multiple=True, defaultval=[1, 3])
    assert el() == html, el()

    html = '<span class="select" id="f-f">foo, bar</span>'
    el = Form('f', static=True).add_select('f', o, multiple=True, defaultval=[1, 2])
    assert el() == html, el()


def test_el_textarea():
    html = '<span class="foo textarea" id="f-f">&nbsp;</span>'
    el = Form('f', static=True).add_textarea('f')
    assert el(class_='foo') == html, el()

    html = '<span class="textarea" id="f-f">foo</span>'
    el = Form('f', static=True).add_textarea('f', defaultval='foo')
    assert el() == html, el()


def test_el_fixed():
    html = '<div class="bar" id="f-f" title="baz">foo</div>'
    f = Form('f', static=True)
    el = f.add_fixed('f', defaultval='foo', title='baz')
    assert el(class_='bar') == html, el(class_='bar')


def test_el_static():
    html = '<span class="bar" id="f-f" title="baz">foo</span>'
    f = Form('f', static=True)
    el = f.add_static('f', defaultval='foo', title='baz')
    assert el(class_='bar') == html, el(class_='bar')


def test_el_header():
    html = '<h2 class="bar" id="f-f" title="baz">foo</h2>'
    el = Form('f', static=True).add_header('f', 'foo', 'h2', title='baz')
    assert el(class_='bar') == html, el(class_='bar')


def test_mcheckbox():
    no_value = '<span class="checkbox static" id="f-f">&nbsp;</span>'
    el = Form('f', static=True).add_mcheckbox('f', 'label', group='thegroup')
    assert el() == no_value, el()
    el = Form('f', static=True).add_mcheckbox('f', 'label', group='thegroup', checked=True)
    assert el() == no_value, el()
    el = Form('f', static=True).add_mcheckbox('f', 'label', group='thegroup')
    assert el(checked='checked') == no_value, el(checked='checked')

    value = '<span class="checkbox static" id="f-f">foo</span>'
    el = Form('f', static=True).add_mcheckbox('f', 'label', defaultval='foo', group='thegroup')
    assert el() == no_value, el()
    el = Form('f', static=True).add_mcheckbox('f', 'label', defaultval='foo', group='thegroup',
                                              checked=True)
    assert el() == value, el()
    el = Form('f', static=True).add_mcheckbox('f', 'label', defaultval='foo', group='thegroup')
    assert el(checked='checked') == value, el(checked='checked')

    # test the elements getting chosen by setting form defaults
    no_value1 = '<span class="checkbox static" id="f-f1">&nbsp;</span>'
    value1 = '<span class="checkbox static" id="f-f1">foo</span>'
    no_value2 = '<span class="checkbox static" id="f-f2">&nbsp;</span>'
    f = Form('f', static=True)
    el1 = f.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
    el2 = f.add_mcheckbox('f2', 'label', 'bar', 'thegroup')
    assert el1() == no_value1, el1()
    assert el2() == no_value2, el2()
    f.set_defaults({'thegroup': 'foo'})
    assert el1() == value1, el1()
    assert el2() == no_value2, el2()


def test_radio():
    no_value = '<span class="radio static" id="f-f">&nbsp;</span>'
    el = Form('f', static=True).add_radio('f', 'label', group='thegroup')
    assert el() == no_value, el()
    el = Form('f', static=True).add_radio('f', 'label', group='thegroup', selected=True)
    assert el() == no_value, el()
    el = Form('f', static=True).add_radio('f', 'label', group='thegroup')
    assert el(selected='selected') == no_value, el(selected='selected')

    value = '<span class="radio static" id="f-f">foo</span>'
    el = Form('f', static=True).add_radio('f', 'label', defaultval='foo', group='thegroup')
    assert el() == no_value, el()
    el = Form('f', static=True).add_radio('f', 'label', defaultval='foo', group='thegroup',
                                          selected=True)
    assert el() == value, el()
    el = Form('f', static=True).add_radio('f', 'label', defaultval='foo', group='thegroup')
    assert el(checked='checked') == value, el(selected='selected')

    # test the elements getting chosen by setting form defaults
    no_value1 = '<span class="radio static" id="f-f1">&nbsp;</span>'
    value1 = '<span class="radio static" id="f-f1">foo</span>'
    no_value2 = '<span class="radio static" id="f-f2">&nbsp;</span>'
    f = Form('f', static=True)
    el1 = f.add_radio('f1', 'label', 'foo', 'thegroup')
    el2 = f.add_radio('f2', 'label', 'bar', 'thegroup')
    assert el1() == no_value1, el1()
    assert el2() == no_value2, el2()
    f.set_defaults({'thegroup': 'foo'})
    assert el1() == value1, el1()
    assert el2() == no_value2, el2()
