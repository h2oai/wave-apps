# Step 3
# Read data and add plot
# ---
from h2o_wave import main, app, Q, ui, on, handle_on, data

import pandas as pd


@app('/')
async def serve(q: Q):
    # First time a browser comes to the app
    if not q.client.initialized:
        await init(q)
        q.client.initialized = True

    # Other browser interactions
    await handle_on(q)
    await q.page.save()


async def init(q: Q) -> None:
    q.client.cards = set()
    q.client.dark_mode = False

    q.page['meta'] = ui.meta_card(
        box='',
        title='Employee Churn Prediction',
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
    q.page['header'] = ui.header_card(
        box='header',
        title='Employee Churn Prediction',
        subtitle="Predict which employees are at risk and identify relevant factors."
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )

    q.client.shapley = pd.read_csv("./src/static/shapley_values.csv")

    await home(q)


@on()
async def home(q: Q):
    clear_cards(q)
    # Variable importance graph
    varimp = get_varimp(q.client.shapley)

    add_card(q, 'varimp_card', ui.plot_card(box='horizontal', title='Top Factors Affecting Churn',
        data=data('feature importance', 5, rows=varimp),
        plot=ui.plot([ui.mark(type='interval', x='=importance', y='=feature', x_min=0, color='#9c3a3a')])
    ))


def get_varimp(shapley_vals, top_n=5):
    varimp = shapley_vals[[i for i in shapley_vals.columns if ('contrib' in i) & (i != 'contrib_bias')]]
    varimp = varimp.abs().mean().reset_index()
    varimp.columns = ["Feature", "Importance"]
    varimp['Feature'] = varimp['Feature'].str.replace("contrib_", "")
    varimp = varimp.sort_values(by="Importance", ascending=False).head(n=top_n)
    varimp = varimp.values.tolist()[::-1]
    
    return varimp

# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)