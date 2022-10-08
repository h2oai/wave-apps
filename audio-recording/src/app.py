from h2o_wave import main, app, Q, ui
import pathlib

LIGHT_THEME = "benext"
DARK_THEME = "winter-is-coming"


@app("/")
async def serve(q: Q):
    # Initialize the page with a single button.
    if not q.client.initialized:
        # Load JS polyfills to record on older browsers as well.
        q.page["meta"] = ui.meta_card(
            box="",
            scripts=[
                ui.script(
                    "https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/OpusMediaRecorder.umd.js",
                    asynchronous=False,
                ),
                ui.script(
                    "https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/encoderWorker.umd.js",
                    asynchronous=False,
                ),
            ],
            layouts=[
                ui.layout(
                    breakpoint="xs",
                    zones=[
                        ui.zone(name="header"),
                        ui.zone(
                            name="content",
                            direction=ui.ZoneDirection.ROW,
                            size="500px",
                            align="center",
                            justify="center",
                        ),
                        ui.zone(name="footer"),
                    ],
                )
            ],
            theme=DARK_THEME,
        )
        #header_card
        q.page["header"] = ui.header_card(
            box="header",
            title="Audio Recording App",
            subtitle="Record audio and save it as a WAV file.",
            image="https://wave.h2o.ai/img/h2o-logo.svg",
            items=[ui.button(name="toggle_theme", label="🌙 Dark", primary=True)],
        )
        #form-card creation
        q.page["form"] = ui.form_card(
            box=ui.box(
                zone="content",
                width="500px",
            ),
            items=[
                ui.inline(
                    justify="center",
                    items=[
                        ui.text_xl(content="Record Audio"),
                    ],
                ),
                ui.image(
                    title="Image title",
                    path="https://cdn.pixabay.com/photo/2016/10/29/20/58/sound-1781570_1280.png",
                    width="100%",
                ),
                ui.inline(
                    justify="center",
                    items=[
                        ui.button(
                            name="start_recording",
                            label="Start recording",
                            primary=True,
                            icon="Play",
                        ),
                    ],
                ),
            ],
        )
        #footer-card creation
        q.page["footer"] = ui.footer_card(
            box="footer",
            caption="Made with 💛 by [Ashish Lamsal](https://lamsalashish.com.np/) - community member.",
        )

        # absolute path for record.js
        script_path = pathlib.Path(__file__).parent.resolve() / "record.js"

        # Load initial JS from file record.js
        with open(script_path, encoding="utf-8") as f:
            q.page["meta"].script = ui.inline_script(f.read())
        #Dark-Theme
        q.client.theme = DARK_THEME
        q.client.initialized = True

    # Toggle theme
    if q.args.toggle_theme:
        if q.client.theme == DARK_THEME:
            q.client.theme = LIGHT_THEME
            #LIGHT-THEME
            q.page["header"].items[0].button.label = "☀️ Light"
        else:
            #DARK-THEME
            q.client.theme = DARK_THEME
            q.page["header"].items[0].button.label = "🌙 Dark"
        #CLIENT-THEME
        q.page["meta"].theme = q.client.theme

    # referenced to update content
    title = q.page["form"].items[0].inline.items[0].text_xl
    btn = q.page["form"].items[2].inline.items[0].button
    #CONDITION-TO-START-RECORDING:
    if q.args.start_recording:
        # Start recording via JS.
        q.page["meta"].script = ui.inline_script("startRecording()")

        # Update Wave UI.
        title.content = "Recording..."
        # buttons used
        btn.name = "stop_recording"
        btn.label = "Stop recording"
        btn.icon = "CircleStopSolid"
        #stop recording condition
    elif q.args.stop_recording:
        # Stop recording via JS.
        q.page["meta"].script = ui.inline_script("stopRecording()")

        # Update Wave UI.
        btn.name = "start_recording"
        btn.label = "Start recording"
        btn.icon = "Play"

    if q.events.audio and q.events.audio.captured:
        # Download the result audio locally and consume it in a model.
        local_audio = await q.site.download(q.events.audio.captured, ".")

        # Just for demo purposes, allow for listening to recorded file.
        title.content = f"Listen to [recording]({q.events.audio.captured})"
    #waiting for the page to response
    await q.page.save()
