from h2o_wave import ui

import pandas as pd
import os


def ui_table_from_df(df: pd.DataFrame, rows: int, name: str):
    """
    Convert a dataframe into wave ui table format.
    """
    df = df.copy().reset_index(drop=True)
    columns = [ui.table_column(name=str(x), label=str(x)) for x in df.columns.values]
    rows = min(rows, df.shape[0])

    try:
        table = ui.table(
            name=name,
            columns=columns,
            rows=[
                ui.table_row(
                    name=str(i),
                    cells=[str(df[col].values[i]) for col in df.columns.values]
                ) for i in range(rows)
            ]
        )
    except Exception:
        table = ui.table(
            name=name,
            columns=[ui.table_column('0', '0')],
            rows=[ui.table_row(name='0', cells=[str('No data found')])]
        )

    return table


# Returns a list of UI objects that can be used in a Form_Card: header and python code of the provided file
# Usage: q.page['code'] = ui.form_card(box='3 4 -1 -1', items=python_code_content("run.py"))
def python_code_content(file_to_display):
    from pygments import highlight
    from pygments.formatters.html import HtmlFormatter
    from pygments.lexers import get_lexer_by_name

    local_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(local_dir, file_to_display)) as f:
        contents = f.read()

    py_lexer = get_lexer_by_name('python')
    html_formatter = HtmlFormatter(full=True, style='xcode')
    code = highlight(contents, py_lexer, html_formatter)

    return [ui.text_xl(f'Application Code'), ui.frame(content=code, height="100%")]