from h2o_wave import main, app, Q, ui
import pathlib


@app("/")
async def serve(q: Q):
    # Initialize the page with a single button.
    if not q.client.initialized:
        q.page["form"] = ui.form_card(
            box="1 1 2 1",
            items=[ui.button(name="start_recording", label="Start recording")],
        )

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
        )

        # absolute path for record.js
        script_path = pathlib.Path(__file__).parent.resolve() / "record.js"

        # Load initial JS from file record.js
        with open(script_path, encoding="utf-8") as f:
            q.page["meta"].script = ui.inline_script(f.read())

        q.client.initialized = True

    if q.args.start_recording:
        # Start recording via JS.
        q.page["meta"].script = ui.inline_script("startRecording()")

        # Update Wave UI.
        btn = q.page["form"].items[0].button
        btn.name = "stop_recording"
        btn.label = "Stop recording"

    elif q.args.stop_recording:
        # Stop recording via JS.
        q.page["meta"].script = ui.inline_script("stopRecording()")

        # Update Wave UI.
        btn = q.page["form"].items[0].button
        btn.name = "start_recording"
        btn.label = "Start recording"

    if q.events.audio and q.events.audio.captured:
        # Download the result audio locally and consume it in a model.
        local_audio = await q.site.download(q.events.audio.captured, ".")

        # Just for demo purposes, allow for listening to recorded file.
        q.page["form"].items = [
            ui.text(f"Listen to [recording]({q.events.audio.captured})")
        ]

    await q.page.save()
