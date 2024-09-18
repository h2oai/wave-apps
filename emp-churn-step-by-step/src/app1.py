# Step 1
# Setting Up Layout:Header, main page and footer
# ---
from h2o_wave import main, app, Q, ui, on, run_on, data


@app('/')
async def serve(q: Q):
    # First time a browser comes to the app
    if not q.client.initialized:
        await init(q)
        q.client.initialized = True

    # Other browser interactions
    await run_on(q)
    await q.page.save()


async def init(q: Q) -> None:
    q.client.cards = set()
    q.client.dark_mode = False
    # First we define the layout of the page
    # The layout contains the header, footer and the main content
    # To place content into the layout, we use zones and cards
    # Zones are like containers that hold cards
    # Cards are like the content that we want to display
    # We can have multiple zones and cards in a layout
    # We can also have multiple layouts
    # Here we define a single layout with 3 zones: header, content and footer
    # The content zone is further divided into 2 zones: horizontal and vertical
    # The horizontal zone is for the cards that contain static content: main factors impacting Employee Churn
    # and the histogram of model predictions
    #
    # The vertical zone is for the cards that contain dynamic content: threshold slider, the table of predictions and
    # the local Shapley values
    # The header and footer zones are for the header and footer
    # The header and footer zones are not divided into further zones
    q.page['meta'] = ui.meta_card(
        box='',
        title='My Wave App',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                        ui.zone('vertical', size='1', )
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )
    # Place the header and footer into the layout
    q.page['header'] = ui.header_card(
        box='header',
        title='My Wave App',
        subtitle="Example to get us started"
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )

    await home(q)


@on()
async def home(q: Q):
    clear_cards(q)
    add_card(q, 'form', ui.form_card(box='vertical', items=[ui.text('This is my app!')]))
    add_card(q, 'form', ui.form_card(box='horizontal', items=[ui.text('This is Horizontal my app!')]))


# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)