from h2o_wave import Q, ui


async def render_main(q: Q):
    q.page["main"] = ui.form_card(
        box="1 1 4 10",
        items=[
            ui.choice_group(
                name="function",
                label="Choose function",
                value="factorial",
                choices=[
                    ui.choice(name="factorial", label="Factorial"),
                    ui.choice(name="sum", label="Sum"),
                ],
            ),
            ui.range_slider(name="number", label="Number", min=5, max=10),
            ui.button(name="calculate", label="Calculate", primary=True),
        ],
    )
    await q.page.save()


async def render_calculate(q: Q):
    q.page["main"] = ui.form_card(
        box="1 1 4 10",
        items=[
            (
                ui.progress(
                    label=f"A {q.app.function} in progress...",
                    value=q.app.progress,
                    name="progress",
                )
                if q.app.result is None
                else ui.label(label=f"Result: {q.app.result}", name="result")
            ),
            (
                ui.button(
                    name="stop",
                    label="Stop",
                    primary=True,
                )
                if q.app.result is None
                else ui.button(
                    name="again",
                    label="Again",
                    primary=True,
                )
            ),
        ],
    )
    await q.page.save()
