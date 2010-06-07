import unittest
import datetime
import warnings
from pysutils import DumbObject
from formencode.validators import Int
from nose.plugins.skip import SkipTest

from pysform import Form
from pysform.element import TextElement
from pysform.util import NotGiven, NotGivenIter, literal
from pysform.exceptions import ValueInvalid, ProgrammingError

L = literal

def test_el_button():
    el = Form('f', static=True).elements.add_button('field', 'Field')
    assert el.render() == '', el.render()
    
    el = Form('f', static=True).elements.add_button('field', 'Field', defaultval='the button')
    assert el.render() == '', el.render()

def test_el_checkbox():
    not_checked = '<div class="checkbox" id="f-f">no</div>'
    checked = '<div class="checkbox" id="f-f">yes</div>'
    
    # no default
    f = Form('f', static=True)
    el = f.elements.add_checkbox('f', 'f')
    assert el.render() == not_checked, el.render()
    el.defaultval = True
    assert el.render() == checked, el.render()
    
    # checked attribute    
    f = Form('f', static=True)
    el = f.elements.add_checkbox('f', 'f', checked='checked')
    assert el.render(checked='checked') == checked, el.render(checked='checked')

def test_el_file():
        el = Form('f', static=True).elements.add_file('f')
        assert el() == '', el()
        
def test_el_hidden():
    el = Form('f', static=True).elements.add_hidden('f')
    assert el() == '', el()
        
def test_el_image():
    el = Form('f', static=True).elements.add_image('f')
    assert el() == '', el()
        
def test_el_reset():
    el = Form('f', static=True).elements.add_reset('f')
    assert el() == '', el()
        
def test_el_submit():
    el = Form('f', static=True).elements.add_submit('f')
    assert el() == '', el()
        
def test_el_cancel():
    el = Form('f', static=True).elements.add_cancel('f')
    assert el() == '', el()

def test_el_text():
    html = '<div class="text" id="f-field">&nbsp;</div>'
    form = Form('f', static=True)
    el = form.elements.add_text('field', 'Field')
    assert el() == html, el()
    
    form = Form('f', static=True)
    el = form.elements.add_text('field', 'Field', maxlength=1)
    assert el() == html, el()
    
    html = '<div class="text" id="f-field">one</div>'
    form = Form('f', static=True)
    el = form.elements.add_text('field', 'Field', defaultval='one')
    assert el() == html, el()

def test_el_confirm():
    f = Form('f', static=True)
    pel = f.elements.add_password('p', 'password')
    cel = f.elements.add_confirm('f', match='p')
    assert cel() == '', cel()

def test_el_date():
    html = '<div class="text" id="f-field">&nbsp;</div>'
    el = Form('f', static=True).elements.add_date('field', 'Field')
    assert el() == html, el()
    
    # our date-time object should get converted to the appropriate format
    html = '<div class="text" id="f-field">12/03/2009</div>'
    el = Form('f', static=True).elements.add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3))
    assert el() == html, el()
    
    # european style dates
    html = '<div class="text" id="f-field">03/12/2009</div>'
    el = Form('f', static=True).elements.add_date('field', 'Field', defaultval=datetime.date(2009, 12, 3), month_style='dd/mm/yyyy')
    assert el() == html, el()

def test_el_email():
    html = '<div class="text" id="f-field">bob@example.com</div>'
    el = Form('f', static=True).elements.add_email('field', 'Field', defaultval='bob@example.com')
    assert el() == html, el()

def test_el_password():
    f = Form('f', static=True)
    el = f.elements.add_password('p', 'password')
    assert el() == '', el()

def test_el_time():
    html = '<div class="text" id="f-field">13:00:00</div>'
    el = Form('f', static=True).elements.add_time('field', 'Field', defaultval=(13, 0))
    assert el() == html, el()

def test_el_url():
    html = '<div class="text" id="f-f">&nbsp;</div>'
    el = Form('f', static=True).elements.add_url('f')
    assert el() == html, el()
    
    html = '<div class="text" id="f-f">example.org</div>'
    el = Form('f', static=True).elements.add_url('f', defaultval="example.org")
    assert el() == html, el()
    
    html = '<div class="text" id="f-f"><a href="http://example.org">http://example.org</a></div>'
    el = Form('f', static=True).elements.add_url('f', defaultval="http://example.org")
    assert el() == html, el()

def test_el_select():
    o = [(1, 'a'), (2, 'b')]
    html = '<div class="select" id="f-f">&nbsp;</div>'
    el = Form('f', static=True).elements.add_select('f', o)
    assert el() == html, el()
    
    html = '<div class="select" id="f-f">a</div>'
    el = Form('f', static=True).elements.add_select('f', o, defaultval=1)
    assert el() == html, el()
    el = Form('f', static=True).elements.add_select('f', o, defaultval='1')
    assert el() == html, el()
    el = Form('f', static=True).elements.add_select('f', o, defaultval=u'1')
    assert el() == html, el()

def test_el_select_multiple():
    o = [(1, 'a'), (2, 'b')]
    html = '<div class="select" id="f-f">&nbsp;</div>'
    el = Form('f', static=True).elements.add_select('f', o, multiple=True)
    assert el() == html, el()
    
    html = '<div class="select" id="f-f">a</div>'
    el = Form('f', static=True).elements.add_select('f', o, multiple=True, defaultval=1)
    assert el() == html, el()
    el = Form('f', static=True).elements.add_select('f', o, multiple=True, defaultval='1')
    assert el() == html, el()
    el = Form('f', static=True).elements.add_select('f', o, multiple=True, defaultval=u'1')
    assert el() == html, el()
    el = Form('f', static=True).elements.add_select('f', o, multiple=True, defaultval=[1,3])
    assert el() == html, el()
    
    html = '<div class="select" id="f-f">a, b</div>'
    el = Form('f', static=True).elements.add_select('f', o, multiple=True, defaultval=[1,2])
    assert el() == html, el()

def test_el_textarea():
    html = '<div class="foo textarea" id="f-f">&nbsp;</div>'
    el = Form('f', static=True).elements.add_textarea('f')
    assert el(class_='foo') == html, el()
    
    html = '<div class="textarea" id="f-f">foo</div>'
    el = Form('f', static=True).elements.add_textarea('f', defaultval='foo')
    assert el() == html, el()

def test_el_fixed():
    html = '<div class="bar" id="f-f" title="baz">foo</div>'
    f = Form('f', static=True)
    el = f.elements.add_fixed('f', defaultval='foo', title='baz')
    assert el(class_='bar') == html, el(class_='bar')
    
def test_el_static():
    html = '<div class="bar" id="f-f" title="baz">foo</div>'
    f = Form('f', static=True)
    el = f.elements.add_static('f', defaultval='foo', title='baz')
    assert el(class_='bar') == html, el(class_='bar')

def test_el_header():
    html = '<h2 class="bar" id="f-f" title="baz">foo</h2>'
    el = Form('f', static=True).elements.add_header('f', 'foo', 'h2', title='baz')
    assert el(class_='bar') == html, el(class_='bar')

def test_mcheckbox():
    no_value = '<div class="checkbox" id="f-f">&nbsp;</div>'
    el = Form('f', static=True).elements.add_mcheckbox('f', 'label', group='thegroup' )
    assert el() == no_value, el()
    el = Form('f', static=True).elements.add_mcheckbox('f', 'label', group='thegroup', checked=True)
    assert el() == no_value, el()
    el = Form('f', static=True).elements.add_mcheckbox('f', 'label', group='thegroup')
    assert el(checked='checked') == no_value, el(checked='checked')
    
    value = '<div class="checkbox" id="f-f">foo</div>'
    el = Form('f', static=True).elements.add_mcheckbox('f', 'label', defaultval='foo', group='thegroup' )
    assert el() == no_value, el()
    el = Form('f', static=True).elements.add_mcheckbox('f', 'label', defaultval='foo', group='thegroup', checked=True)
    assert el() == value, el()
    el = Form('f', static=True).elements.add_mcheckbox('f', 'label', defaultval='foo', group='thegroup')
    assert el(checked='checked') == value, el(checked='checked')
    
    # test the elements getting chosen by setting form defaults
    no_value1 = '<div class="checkbox" id="f-f1">&nbsp;</div>'
    value1 = '<div class="checkbox" id="f-f1">foo</div>'
    no_value2 = '<div class="checkbox" id="f-f2">&nbsp;</div>'
    f = Form('f', static=True)
    el1 = f.elements.add_mcheckbox('f1', 'label', 'foo', 'thegroup')
    el2 = f.elements.add_mcheckbox('f2', 'label', 'bar', 'thegroup')
    assert el1() == no_value1, el1()
    assert el2() == no_value2, el2()
    f.set_defaults({'thegroup':'foo'})
    assert el1() == value1, el1()
    assert el2() == no_value2, el2()

def test_radio():
    no_value = '<div class="radio" id="f-f">&nbsp;</div>'
    el = Form('f', static=True).elements.add_radio('f', 'label', group='thegroup' )
    assert el() == no_value, el()
    el = Form('f', static=True).elements.add_radio('f', 'label', group='thegroup', selected=True)
    assert el() == no_value, el()
    el = Form('f', static=True).elements.add_radio('f', 'label', group='thegroup')
    assert el(selected='selected') == no_value, el(selected='selected')
    
    value = '<div class="radio" id="f-f">foo</div>'
    el = Form('f', static=True).elements.add_radio('f', 'label', defaultval='foo', group='thegroup' )
    assert el() == no_value, el()
    el = Form('f', static=True).elements.add_radio('f', 'label', defaultval='foo', group='thegroup', selected=True)
    assert el() == value, el()
    el = Form('f', static=True).elements.add_radio('f', 'label', defaultval='foo', group='thegroup')
    assert el(selected='selected') == value, el(selected='selected')
    
    # test the elements getting chosen by setting form defaults
    no_value1 = '<div class="radio" id="f-f1">&nbsp;</div>'
    value1 = '<div class="radio" id="f-f1">foo</div>'
    no_value2 = '<div class="radio" id="f-f2">&nbsp;</div>'
    f = Form('f', static=True)
    el1 = f.elements.add_radio('f1', 'label', 'foo', 'thegroup')
    el2 = f.elements.add_radio('f2', 'label', 'bar', 'thegroup')
    assert el1() == no_value1, el1()
    assert el2() == no_value2, el2()
    f.set_defaults({'thegroup':'foo'})
    assert el1() == value1, el1()
    assert el2() == no_value2, el2()