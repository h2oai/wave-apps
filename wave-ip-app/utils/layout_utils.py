from h2o_wave import ui, main, Q, app
import utils.ip_utils as ip
import os


async def blur_layout(q: Q):
    q.client.blur_controls = True

    if q.page['controls']:
        del q.page['controls']

    q.page['controls_b0'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as fourth item in content zone.
            ui.box(zone='content', order=4),
            # If the viewport width >= 768, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 1200, place in content zone.
            ui.box(zone='content', order=1, height='400px', size=1),
        ),
        title='',
        items=[
            ui.textbox(name='ave_filter_w', label='Filter Width', placeholder='3 or 5 or ...'),
            ui.textbox(name='ave_filter_h', label='Filter Height', placeholder='3 or 5 or ...'),
            ui.buttons(
                items=[
                    ui.button(name='ave_blur', label='Average Blurring', primary=True,
                              tooltip='Click to apply average blur'),
                    ui.button(name='reset_blur', label='Reset Image', tooltip='Click to Reset')
                ]
            )

        ]
    )

    q.page['controls_b1'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as fourth item in content zone.
            ui.box(zone='content', order=4),
            # If the viewport width >= 768, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 1200, place in content zone.
            ui.box(zone='content', order=2, height='400px', size=1),
        ),
        title='',
        items=[
            ui.textbox(name='gb_filter_w', label='Filter Width', placeholder='3 or 5 or ...'),
            ui.textbox(name='gb_filter_h', label='Filter Height', placeholder='3 or 5 or ...'),
            ui.textbox(name='gb_std', label='Standard Deviation'),
            ui.buttons(
                items=[
                    ui.button(name='gaussian_blur', label='Gaussian Blurring', primary=True,
                              tooltip='Click to apply gaussian blur'),
                    ui.button(name='reset_blur', label='Reset Image', tooltip='Click to Reset')
                ]
            )

        ]
    )
    q.page['controls_b2'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as fourth item in content zone.
            ui.box(zone='content', order=4),
            # If the viewport width >= 768, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 1200, place in content zone.
            ui.box(zone='content', order=3, height='400px', size=1),
        ),
        title='',
        items=[
            ui.textbox(name='med_kernel', label='Kernel Size', placeholder='3 or 5 or ...'),
            ui.buttons(
                items=[
                    ui.button(name='median_blur', label='Median Blurring', primary=True,
                              tooltip='Click to apply median blur'),
                    ui.button(name='reset_blur', label='Reset Image', tooltip='Click to Reset')
                ]
            )
        ]
    )

    q.page['controls_b3'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as fourth item in content zone.
            ui.box(zone='content', order=4),
            # If the viewport width >= 768, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 1200, place in content zone.
            ui.box(zone='content', order=4, height='400px', size=1),
        ),
        title='',
        items=[
            ui.textbox(name='bil_kernel', label='Kernel Size', placeholder='3 or 5 or ...'),
            ui.textbox(name='bil_color', label='Number of Colors'),
            ui.textbox(name='bil_sigma', label='Sigma'),
            ui.buttons(
                items=[
                    ui.button(name='bil_blur', label='Bilateral Blurring', primary=True,
                              tooltip='Click to apply bilateral blur'),
                    ui.button(name='reset_blur', label='Reset Image', tooltip='Click to Reset')
                ]
            )
        ]
    )

    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})'''
    await q.page.save()


async def remove_blur_controls(q: Q):
    del q.page['controls_b0']
    del q.page['controls_b1']
    del q.page['controls_b2']
    del q.page['controls_b3']
    await get_standard_control(q)


async def histogram_layout(q: Q):
    if q.client.blur_controls:
        await remove_blur_controls(q)
        q.client.blur_control = False

    q.page['controls'].items = [
        ui.buttons(
            items=[
                ui.button(name='histogram', label='Produce Histogram', primary=True,
                          tooltip='Click to generate Histogram')
            ]
        )

    ]
    # image_filename = ip.plot_image(q.client.image)
    # content, = await q.site.upload([image_filename])
    # os.remove(image_filename)
    q.page['transformed_image'].content = f'''Your histogram will be displayed here'''
    await q.page.save()


async def rgb2gray_layout(q: Q):
    if q.client.blur_controls:
        await remove_blur_controls(q)
        q.client.blur_control = False

    q.page['controls'].items = [
        ui.buttons(
            items=[
                ui.button(name='rgb2gray', label='Change RGB to GrayScale', primary=True,
                          tooltip='Click to apply RGB2GRAY'),
                ui.button(name='reset_rgb2gray', label='Reset Image', tooltip='Click to Reset')
            ]
        )

    ]
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})'''
    await q.page.save()


async def rotation_layout(q: Q):
    if q.client.blur_controls:
        await remove_blur_controls(q)
        q.client.blur_control = False

    q.page['controls'].items = [
        ui.slider(name='rotate', label='Translation on X axis', min=-180, max=180, step=1),
        ui.textbox(name='x_point', label='X coordinate to rotate'),
        ui.textbox(name='y_point', label='Y coordinate to rotate'),
        ui.buttons(
            items=[
                ui.button(name='rotation', label='Apply Rotation', primary=True,
                          tooltip='Click to apply rotation transformation'),
                ui.button(name='reset_rotation', label='Reset Rotation', tooltip='Click to Reset')
            ]
        )

    ]
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})\n
            Last Rotation = {q.args.rotation} '''
    await q.page.save()


async def translation_layout(q: Q):
    if q.client.blur_controls:
        await remove_blur_controls(q)
        q.client.blur_control = False

    q.page['controls'].items = [
        ui.slider(name='translate_X', label='Translation on X axis', min=0, max=360, step=1),
        ui.slider(name='translate_Y', label='Translation on Y axis', min=0, max=360, step=1),
        ui.buttons(
            items=[
                ui.button(name='translation', label='Apply Translation', primary=True,
                          tooltip='Click to apply translation transformation'),
                ui.button(name='reset_translation', label='Reset Translation', tooltip='Click to Reset')
            ]
        )
    ]
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'![plot]({content})'
    q.page['controls'].items[1].value = q.page['controls'].items[2].value = 0

    await q.page.save()


async def transformation_layout(q: Q, content):
    if q.client.blur_controls:
        await remove_blur_controls(q)
        q.client.blur_control = False

    q.page['original_image'] = ui.markdown_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as second item in content zone.
            ui.box(zone='content', order=2),
            # If the viewport width >= 768, place in content zone.
            'content',
            # If the viewport width >= 1200, place as first item in charts zone, use 2 parts of available space.
            ui.box(zone='charts', order=1, size=1),
        ),
        title='Original Image',
        content=f'![plot]({content})',
    )
    q.page['transformed_image'] = ui.markdown_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 768, place as second item in content zone.
            ui.box(zone='content', order=2),
            # If the viewport width >= 1200, place as second item in charts zone, use 1 part of available space.
            ui.box(zone='charts', order=2, size=1),
        ),
        title='Transformed Image',
        content=f'''![plot]({content})\n
        Last Translation X = {q.args.translate_X}  Y = {q.args.translate_Y}
        ''',
    )
    await get_standard_control(q)

    q.page['controls'].items = [
        ui.slider(name='translate_X', label='Translation on X axis', min=0, max=360, step=1),
        ui.slider(name='translate_Y', label='Translation on Y axis', min=0, max=360, step=1),
        ui.buttons(
            items=[
                ui.button(name='translation', label='Apply Translation', primary=True,
                          tooltip='Click to apply translation transformation'),
                ui.button(name='reset_translation', label='Reset Translation', tooltip='Click to Reset')
            ]
        )
    ]

    await q.page.save()


async def get_standard_control(q: Q):
    q.page['controls'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as fourth item in content zone.
            ui.box(zone='content', order=4),
            # If the viewport width >= 768, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 1200, place in content zone.
            ui.box(zone='content', height='400px', size=1),
        ),
        title='',
        items=[]
    )
    await q.page.save()


async def responsive_layout(q: Q, content, layout):
    # The meta card's 'zones' attribute defines placeholder zones to lay out cards for different viewport sizes.
    # We define three layout schemes here.
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            # If the viewport width >= 0:
            breakpoint='xs',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for content
                ui.zone('content')
            ]
        ),
        ui.layout(
            # If the viewport width >= 768:
            breakpoint='m',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    # 250px wide sidebar
                    ui.zone('sidebar', size='250px'),
                    # Use remaining space for content
                    ui.zone('content'),
                ]),
                ui.zone('footer'),
            ]
        ),
        ui.layout(
            # If the viewport width >= 1200:
            breakpoint='xl',
            # width='1500px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    # 300px wide sidebar
                    ui.zone('sidebar', size='450px'),
                    # Use remaining space for other widgets
                    ui.zone('other', zones=[
                        # Use one half for charts
                        ui.zone('charts', direction=ui.ZoneDirection.ROW),
                        # Use other half for content
                        ui.zone('content', direction=ui.ZoneDirection.ROW),
                    ]),
                ]),
                ui.zone('footer'),
            ]
        )
    ])
    q.page['header'] = ui.header_card(
        # Place card in the header zone, regardless of viewport size.
        box='header',
        title='Wave Image Processor',
        subtitle="Let's process your images",
        nav=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#menu/translation', label='Translation'),
                ui.nav_item(name='#menu/rotation', label='Rotation'),
                ui.nav_item(name='#menu/rgb2gray', label='RGB2GRAY'),
                ui.nav_item(name='#menu/histogram', label='Histogram'),
                ui.nav_item(name='#menu/blur', label='Blur'),
            ]),
            ui.nav_group('Help', items=[
                ui.nav_item(name='#about', label='About'),
                ui.nav_item(name='#support', label='Support'),
            ])
        ],
    )

    q.page['main_sidebar'] = ui.form_card(
        # If the viewport width >= 0, place in content zone.
        # If the viewport width >= 768, place in sidebar zone.
        # If the viewport width >= 1200, place in sidebar zone.
        box=ui.boxes('content', 'sidebar', 'sidebar'),
        title='',
        items=[
            ui.text_xl(name='image_uploader_header', content="<h4 align='center'>Upload Your Images</h4>"),
            ui.file_upload(name='image_upload', label='Upload Image', multiple=True,
                           file_extensions=['jpg', 'jpeg', 'png']),
            ui.table(
                name='image_table',
                columns=q.client.columns,
                rows=[ui.table_row(
                    name='images',
                    cells=[row.Image, row.Timestamp]
                ) for row in q.client.image_df.itertuples()],
                groupable=False,
                downloadable=True,
                resettable=False,
                height='425px',
            ),
        ],
    )

    await layout(q, content)

    q.page['footer'] = ui.footer_card(box='footer', caption='(c) 2020 Lowest Common Denominator, Inc. ')

    await q.page.save()
