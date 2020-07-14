from os import path

renderers = ('default', 'withaction', 'all_els', 'static', 'noteprefix',
             'reqnote_formtop', 'reqnote_formtop_header', 'reqnote_section')
rendir = ''


def test_all():
    global rendir
    for rname in renderers:
        rmod = __import__('blazeform.tests.renderers.%s' % rname, globals(), locals(), ['TestForm'])
        if rendir == '':
            rendir = path.dirname(rmod.__file__)
        tf = rmod.TestForm()
        try:
            tf.set_submitted(rmod.submitted_vals)
            tf.is_valid()
        except AttributeError as e:
            if 'submitted_vals' not in str(e):
                raise
        try:
            form_html = tf.render(**rmod.render_opts)
        except AttributeError as e:
            if 'render_opts' not in str(e):
                raise
            form_html = tf.render()
        form_html_lines = form_html.strip().splitlines()
        htmlfile = open(path.join(rendir, '%s.html' % rname))
        try:
            file_html_lines = htmlfile.read().strip().splitlines()
        finally:
            htmlfile.close()

        try:
            for lnum in range(0, len(form_html_lines)):
                try:
                    formstr = form_html_lines[lnum]
                except IndexError:
                    if lnum != 0:
                        raise
                    formstr = '**form output empty**'
                try:
                    filestr = file_html_lines[lnum]
                except IndexError:
                    if lnum != 0:
                        raise
                    filestr = '**file empty**'
                # TODO: Restore to normal, changed for testing.
                assert formstr == filestr, 'line %d not equal in %s\n  form: %s\n  file: %s' % \
                    (lnum + 1, '%s.html' % rname, formstr, filestr)
        except AssertionError:
            # write the form output next to the test file for an easy diff
            formfile = open(path.join(rendir, '%s.form.html' % rname), 'w')
            try:
                formfile.write(form_html)
            finally:
                formfile.close()
            raise
