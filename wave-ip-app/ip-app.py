from h2o_wave import Q, app, ui, main, types
import utils.ip_utils as ip
import utils.ui_utils as U
from utils import helper
import cv2
import os
import pandas as pd


@app('/ip')
async def serve(q: Q):
    _hash = q.args['#']

    if not q.client.flag:
        q.client.image = cv2.imread('data/lena.jpg')[:, :, ::-1]
        q.client.image_df = pd.DataFrame({
            'Image': [],
            'Timestamp': []
        })
        q.client.columns = [
            ui.table_column(name='images_col', label='Image', searchable=True, sortable=True, link=True),
            ui.table_column(name='timestamp_col', label='Timestamp', searchable=True, sortable=True),
        ]

        q.client.flag = True

    if _hash:
        if _hash == 'menu/translation':
            await translation_layout(q)
        elif _hash == 'menu/rotation':
            await rotation_layout(q)
        elif _hash == 'menu/rgb2gray':
            await rgb2gray_layout(q)
        elif _hash == 'menu/histogram':
            await histogram_layout(q)
        elif _hash == 'menu/blur':
            await blur_layout(q)

    if q.args.image_table:
        temp = await q.site.download(q.args.image_table[-1], './data/')
        q.client.image = cv2.imread(temp)[:, :, ::-1]

        image_filename = ip.plot_image(q.client.image)
        content, = await q.site.upload([image_filename])
        os.remove(image_filename)
        await responsive_layout(q, content, transformation_layout)

    if q.args.image_upload:
        q.client.image_df = helper.update_df(q.client.image_df, q.args.image_upload[-1])
        q.page['main_sidebar'].items[2].table.rows = [ui.table_row(
            name=row.Image,
            cells=[row.Image, row.Timestamp]
        ) for row in q.client.image_df.itertuples()]

    if q.args.translation:
        await U.do_translation(q)
    elif q.args.reset_translation:
        await U.reset_translation(q)

    if q.args.rotation:
        await U.do_rotation(q)
    elif q.args.reset_rotation:
        await U.reset_rotation(q)

    if q.args.rgb2gray:
        await U.do_rgb2gray(q)
    elif q.args.reset_rgb2gray:
        await U.reset_rgb2gray(q)

    if q.args.histogram:
        await U.get_histogram(q)

    if q.args.gaussian_blur:
        await U.gaussian_blur(q)

    if not q.client.initialized:
        q.client.initialized = True
        image_filename = ip.plot_image(q.client.image)
        content, = await q.site.upload([image_filename])
        os.remove(image_filename)

        await responsive_layout(q, content, transformation_layout)

    await q.page.save()


async def blur_layout(q: Q):
    # need to add nested form_cards for different blur techniques
    # q.page['controls'].items = [ui.form_card(box='content', title='', items=[
    #         ui.textbox(name='gb_filter', label='Filter Size'),
    #         ui.textbox(name='gb_std', label='Standard Deviation'),
    #         ui.buttons(
    #             items=[
    #                 ui.button(name='gaussian_blur', label='Apply Gaussian Blurring', primary=True,
    #                           tooltip='Click to apply gaussian blur'),
    #                 ui.button(name='reset_blur', label='Reset Image', tooltip='Click to Reset')
    #             ]
    #         )
    #     ])
    # ]
    q.page['controls'].items = [
        ui.button(name='gaussian_blur', label='Apply Gaussian Blurring', primary=True,
                  tooltip='Click to apply gaussian blur'),
        ui.button(name='reset_blur', label='Reset Image', tooltip='Click to Reset')
    ]
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})'''
    await q.page.save()


async def histogram_layout(q: Q):
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
    q.page['controls'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as fourth item in content zone.
            ui.box(zone='content', order=4),
            # If the viewport width >= 768, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 1200, place in content zone.
            ui.box(zone='content', height='400px'),
        ),
        title='',
        items=[
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
                        ui.zone('content'),
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
