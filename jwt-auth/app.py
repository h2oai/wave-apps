from h2o_wave import main, app, Q, ui, on, data

from util import add_card, clear_cards
from wave_auth import handle_auth_on


@on('#page1')
async def page1(q: Q):
    clear_cards(q)
    print("Loading page1")
    q.page['sidebar'].value = '#page1'

    for i in range(3):
        add_card(q, f'info{i}', ui.tall_info_card(box='horizontal', name='', title='Speed',
                                                  caption='The models are performant thanks to...', icon='SpeedHigh'))
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='600px'), title='How does magic work',
        image='https://images.pexels.com/photos/624015/pexels-photo-624015.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
        content='''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ac sodales felis. Duis orci enim, iaculis at augue vel, mattis imperdiet ligula. Sed a placerat lacus, vitae viverra ante. Duis laoreet purus sit amet orci lacinia, non facilisis ipsum venenatis. Duis bibendum malesuada urna. Praesent vehicula tempor volutpat. In sem augue, blandit a tempus sit amet, tristique vehicula nisl. Duis molestie vel nisl a blandit. Nunc mollis ullamcorper elementum.
Donec in erat augue. Nullam mollis ligula nec massa semper, laoreet pellentesque nulla ullamcorper. In ante ex, tristique et mollis id, facilisis non metus. Aliquam neque eros, semper id finibus eu, pellentesque ac magna. Aliquam convallis eros ut erat mollis, sit amet scelerisque ex pretium. Nulla sodales lacus a tellus molestie blandit. Praesent molestie elit viverra, congue purus vel, cursus sem. Donec malesuada libero ut nulla bibendum, in condimentum massa pretium. Aliquam erat volutpat. Interdum et malesuada fames ac ante ipsum primis in faucibus. Integer vel tincidunt purus, congue suscipit neque. Fusce eget lacus nibh. Sed vestibulum neque id erat accumsan, a faucibus leo malesuada. Curabitur varius ligula a velit aliquet tincidunt. Donec vehicula ligula sit amet nunc tempus, non fermentum odio rhoncus.
Vestibulum condimentum consectetur aliquet. Phasellus mollis at nulla vel blandit. Praesent at ligula nulla. Curabitur enim tellus, congue id tempor at, malesuada sed augue. Nulla in justo in libero condimentum euismod. Integer aliquet, velit id convallis maximus, nisl dui porta velit, et pellentesque ligula lorem non nunc. Sed tincidunt purus non elit ultrices egestas quis eu mauris. Sed molestie vulputate enim, a vehicula nibh pulvinar sit amet. Nullam auctor sapien est, et aliquet dui congue ornare. Donec pulvinar scelerisque justo, nec scelerisque velit maximus eget. Ut ac lectus velit. Pellentesque bibendum ex sit amet cursus commodo. Fusce congue metus at elementum ultricies. Suspendisse non rhoncus risus. In hac habitasse platea dictumst.
        '''
    ))


@on('#page2')
async def page2(q: Q):
    clear_cards(q)
    q.page['sidebar'].value = '#page2'
    add_card(q, 'chart1', ui.plot_card(
        box='horizontal',
        title='Chart 1',
        data=data('category country product price', 10, rows=[
            ('G1', 'USA', 'P1', 124),
            ('G1', 'China', 'P2', 580),
            ('G1', 'USA', 'P3', 528),
            ('G1', 'China', 'P1', 361),
            ('G1', 'USA', 'P2', 228),
            ('G2', 'China', 'P3', 418),
            ('G2', 'USA', 'P1', 824),
            ('G2', 'China', 'P2', 539),
            ('G2', 'USA', 'P3', 712),
            ('G2', 'USA', 'P1', 213),
        ]),
        plot=ui.plot([ui.mark(type='interval', x='=product', y='=price', color='=country', stack='auto',
                              dodge='=category', y_min=0)])
    ))
    add_card(q, 'chart2', ui.plot_card(
        box='horizontal',
        title='Chart 2',
        data=data('date price', 10, rows=[
            ('2020-03-20', 124),
            ('2020-05-18', 580),
            ('2020-08-24', 528),
            ('2020-02-12', 361),
            ('2020-03-11', 228),
            ('2020-09-26', 418),
            ('2020-11-12', 824),
            ('2020-12-21', 539),
            ('2020-03-18', 712),
            ('2020-07-11', 213),
        ]),
        plot=ui.plot([ui.mark(type='line', x_scale='time', x='=date', y='=price', y_min=0)])
    ))
    add_card(q, 'table', ui.form_card(box='vertical', items=[ui.table(
        name='table',
        downloadable=True,
        resettable=True,
        groupable=True,
        columns=[
            ui.table_column(name='text', label='Process', searchable=True),
            ui.table_column(name='tag', label='Status', filterable=True, cell_type=ui.tag_table_cell_type(
                name='tags',
                tags=[
                    ui.tag(label='FAIL', color='$red'),
                    ui.tag(label='DONE', color='#D2E3F8', label_color='#053975'),
                    ui.tag(label='SUCCESS', color='$mint'),
                ]
            ))
        ],
        rows=[
            ui.table_row(name='row1', cells=['Process 1', 'FAIL']),
            ui.table_row(name='row2', cells=['Process 2', 'SUCCESS,DONE']),
            ui.table_row(name='row3', cells=['Process 3', 'DONE']),
            ui.table_row(name='row4', cells=['Process 4', 'FAIL']),
            ui.table_row(name='row5', cells=['Process 5', 'SUCCESS,DONE']),
            ui.table_row(name='row6', cells=['Process 6', 'DONE']),
        ])
    ]))


@on('#page3')
async def page3(q: Q):
    clear_cards(q)
    q.page['sidebar'].value = '#page3'
    for i in range(12):
        add_card(q, f'item{i}', ui.wide_info_card(box=ui.box('grid', width='400px'), name='', title='Tile',
                                                  caption='Lorem ipsum dolor sit amet'))


@on('#page4')
async def handle_page4(q: Q):
    clear_cards(q, ['form'])
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card instead of recreating it every time, so ignore 'form' card on drop.
    q.page['sidebar'].value = '#page4'

    if q.args.step1:
        # Just update the existing card, do not recreate.
        q.page['form'].items = [
            ui.stepper(name='stepper', items=[
                ui.step(label='Step 1'),
                ui.step(label='Step 2'),
                ui.step(label='Step 3'),
            ]),
            ui.textbox(name='textbox2', label='Textbox 1'),
            ui.buttons(justify='end', items=[
                ui.button(name='step2', label='Next', primary=True),
            ])
        ]
    elif q.args.step2:
        # Just update the existing card, do not recreate.
        q.page['form'].items = [
            ui.stepper(name='stepper', items=[
                ui.step(label='Step 1', done=True),
                ui.step(label='Step 2'),
                ui.step(label='Step 3'),
            ]),
            ui.textbox(name='textbox2', label='Textbox 2'),
            ui.buttons(justify='end', items=[
                ui.button(name='step1', label='Cancel'),
                ui.button(name='step3', label='Next', primary=True),
            ])
        ]
    elif q.args.step3:
        # Just update the existing card, do not recreate.
        q.page['form'].items = [
            ui.stepper(name='stepper', items=[
                ui.step(label='Step 1', done=True),
                ui.step(label='Step 2', done=True),
                ui.step(label='Step 3'),
            ]),
            ui.textbox(name='textbox3', label='Textbox 3'),
            ui.buttons(justify='end', items=[
                ui.button(name='step2', label='Cancel'),
                ui.button(name='submit', label='Next', primary=True),
            ])
        ]
    else:
        # If first time on this page, create the card.
        add_card(q, 'form', ui.form_card(box='vertical', items=[
            ui.stepper(name='stepper', items=[
                ui.step(label='Step 1'),
                ui.step(label='Step 2'),
                ui.step(label='Step 3'),
            ]),
            ui.textbox(name='textbox1', label='Textbox 1'),
            ui.buttons(justify='end', items=[
                ui.button(name='step2', label='Next', primary=True),
            ]),
        ]))


async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='250px'),
            ui.zone('body', zones=[
                ui.zone('header'),
                ui.zone('content', zones=[
                    # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                    ui.zone('horizontal', size='1', direction=ui.ZoneDirection.ROW),
                    ui.zone('centered', size='1 1 1 1', align='center'),
                    ui.zone('vertical', size='1'),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                ]),
            ]),
        ])
    ])])
    q.page['sidebar'] = ui.nav_card(
        box='sidebar', color='primary', title='My App', subtitle="Let's conquer the world!",
        value=f'#{q.args["#"]}' if q.args['#'] else '#page1',
        image='https://wave.h2o.ai/img/h2o-logo.svg', items=[])
    q.page['header'] = ui.header_card(
        box='header', title='', subtitle='',
    )
    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page1(q)


@on('#profile')
async def profile(q: Q):
    """Example of a profile page"""
    clear_cards(q)
    q.page['sidebar'].value = ''

    add_card(q, 'profile-card', ui.form_card('vertical', items=[
        ui.text_l(f"**Username**: {q.user.username}"),
        ui.text_l(f"**Role**: User")
    ]))
    if q.args.change_password:
        add_card(q, 'edit-password-card', ui.form_card('vertical', items=[
            ui.text_l("DUMMY FORM. FOR VISUAL DEMONSTRATION ONLY."),
            ui.textbox('old_password', 'Old Password', password=True),
            ui.textbox('new_password_one', 'New Password', password=True),
            ui.textbox('new_password_two', 'New Password (Repeat)', password=True),
            ui.button('confirm_change_password', 'Confirm change', primary=True),
        ]))
    elif q.args.confirm_change_password:
        # TODO: compare passwords
        # TODO: verify old password
        # TODO: Only if both are successful may a password change be submitted
        add_card(q, 'edit-password-card', ui.form_card('vertical', items=[
            ui.text_l("[DUMMY MESSAGE]")
        ]))
    else:
        add_card(q, 'password-card', ui.form_card('vertical', items=[
            ui.button('change_password', 'Change password'),
        ]))


async def initialize_client(q: Q):
    q.client.cards = set()
    await init(q)
    q.client.initialized = True


@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        # Run only once per client connection (e.g. new tabs by the same user).
        q.client.cards = set()
        await init(q)
        q.client.initialized = True
        q.client.new = True  # Indicate that client connected for the first time

    await handle_auth_on(q, home_page=page1)
    await q.page.save()
