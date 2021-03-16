import os

from h2o_wave import ui


def python_code_content(file_to_display):
    """
    Returns a list of UI objects that can be used in a Form_Card: header and python code of the provided file.
    Usage: q.page['code'] = ui.form_card(box='3 4 -1 -1', items=python_code_content("run.py"))

    :param file_to_display

    :return: wave UI items
    """
    from pygments import highlight
    from pygments.formatters.html import HtmlFormatter
    from pygments.lexers import get_lexer_by_name

    local_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(local_dir, file_to_display)) as f:
        contents = f.read()

    py_lexer = get_lexer_by_name("python")
    html_formatter = HtmlFormatter(full=True, style="xcode")
    code = highlight(contents, py_lexer, html_formatter)

    return [ui.text_xl("Application Code"), ui.frame(content=code, height="800px")]
