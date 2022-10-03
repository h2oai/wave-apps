from h2o_wave import main, app, Q, ui
import pathlib

# UNIMPORTANT: Helper function to read the file.
def read_file(p: str) -> str:
    # absolute path for app.js
    script_path = pathlib.Path(__file__).parent.resolve() / p

    with open(script_path, encoding="utf-8") as f:
        return f.read()


@app("/")
async def serve(q: Q):
    if not q.client.initialized:
        q.page["editor"] = ui.markup_card(
            box="1 1 6 10",
            title="Editor",
            # Render a container div and expand it to occupy whole card.
            content="""
<div id="editor" style="position:absolute;top:45px;bottom:15px;right:15px;left:15px"/>
""",
        )
        q.page["text"] = ui.markdown_card(box="7 1 5 10", title="Text", content="")

        # Make sure to render the div prior to loading Javascript.
        await q.page.save()

        # Download the necessary javascript and render the actual Monaco editor.
        q.page["meta"] = ui.meta_card(
            box="",
            # Download external JS loader script.
            scripts=[
                ui.script(
                    """
https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.33.0/min/vs/loader.min.js
"""
                )
            ],
            script=ui.inline_script(
                # Read our JS file and pass it as a string.
                content=read_file("app.js"),
                # Only run this script if "require" object is present
                # in browser's window object.
                requires=["require"],
                # Only run this script if our div container
                # with id "monaco-editor" is rendered.
                targets=["editor"],
            ),
        )
        q.client.initialized = True

    if q.events.editor:
        if q.events.editor.save:
            q.page["text"].content = q.events.editor.save
            q.page["editor"].title = "Editor"
        elif q.events.editor.change:
            # Show "dirty" state by appending an * to editor card title.
            q.page["editor"].title = "*Editor"

    await q.page.save()
