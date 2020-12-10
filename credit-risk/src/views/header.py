from h2o_wave import ui, Q

from ..config import config


def render_header(q: Q):
    q.page["title"] = ui.header_card(
        box='title',
        title=config.title,
        subtitle=config.subtitle,
        icon=config.icon,
        icon_color=config.color,
    )

    q.page["menu"] = ui.breadcrumbs_card(
        box='menu',
        items=[
            ui.breadcrumb(name='home', label='Home'),
        ],
    )
