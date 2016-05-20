Change Log
----------


0.3.9 released 2016-05-20
=========================

* make is_empty more general with respect to input type, 0 should not be empty

0.3.8 released 2016-02-24
=========================

* update compatibility with FormEncode to include 1.3

0.3.7 released 2014-10-27
=========================

* fix checkbox element to handle empty value as on/true for IE 9/10 compat.

0.3.6 released 2014-10-15
=========================

* allow labels for logical groups, such as radio buttons or checkboxes

0.3.5 released 2014-08-20
=========================

* ensure that form validators and element processors which are FE validators
  are instances


0.3.4 released 2012-07-05
=========================

* form now has all_errors() method which returns form and field errors as (list,
  dict) tuple (respectively).
* update the way file uploads are checked for being sent.  Previously, we were
  testing for the filename header to be None, but Werkzeug is sending it over as
  an empty string in the FileStorage object now.  Could theoretically result in
  behavior change, but only in narrow edge cases.

0.3.3 released 2011-11-16
=========================

* TextAreaElement now uses maxlength kwarg

0.3.2 released 2011-06-11
=========================

* fix broken distribution of 0.3.1

0.3.1 released 2011-06-11
=========================

* fixed bug in radio button rendering after validation error
