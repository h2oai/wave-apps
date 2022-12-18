from h2o_wave import Q, ui, main, app
import pandas as pd
from siuba import *
from siuba.siu import call
from charts import show_table, streaming_service, fav_age_effect, fav_depression, fav_insomnia


# read the data anc cover
music = pd.read_csv("../music_mental_survey_clean.csv")
music = music >> select(~_["Unnamed: 0"])  # remove unwanted column


@app("/")
async def serve(q: Q):
    q.page["meta"] = ui.meta_card(
        box="",
        themes=[
            ui.theme(
                name="cool7",
                primary="#ffffff",
                text="#ffffff",
                card="#111111",
                page="#ffffff",
            )
        ],
        theme="cool7",
    )
    q.page["header"] = ui.header_card(
        box=("1 1 10 1"),
        icon="HealthRefresh",
        color="card",
        title="Music's effect on Mental Health",
        subtitle="Can music impact mental health? Let's find out",
    )
    q.page["table"] = ui.form_card(
        box=("1 2 3 5"),
        title="Music and Mental Condition Dataset",
        items=[await show_table(df=music)],
    )

    q.page["streaming_service"] = ui.frame_card(
        box=("4 2 3 5"),
        title="Most popular streaming service",
        content=await streaming_service(df=music),
    )

    q.page["fav_depression"] = ui.frame_card(
        box=("7 2 4 5"),
        title="",
        content=await fav_depression(df=music),
    )

    q.page["fav_age_effect"] = ui.frame_card(
        box=("1 7 5 5"),
        title="",
        content=await fav_age_effect(df=music),
    )

    q.page["fav_insomnia"] = ui.frame_card(
        box=("6 7 5 5"),
        title="",
        content=await fav_insomnia(df=music),
    )

    q.page["foot"] = ui.markdown_card(
        box="1 12 10 1",
        title="",
        content="""<br/>**[Daniel Boadzie](https://www.linkedin.com/in/boadzie/) -
        The dataset for this project was obtained from [kaggle](https://www.kaggle.com/code/totoro29/music-and-mental-condition/notebook)**
        """,
    )

    await q.page.save()
