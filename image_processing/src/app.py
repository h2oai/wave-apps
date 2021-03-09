from h2o_wave import Q, app, ui, main, core
import src.ip_utils as ip
import src.ui_utils as U
from src import helper
import cv2
import os
import pandas as pd
import src.layout_utils as layouts


@app('/ip')
async def serve(q: Q):
    _hash = q.args['#']

    if not q.client.flag:
        q.client.image = cv2.imread('data/h2o.png')[:, :, ::-1]
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
            await layouts.translation_layout(q)
        elif _hash == 'menu/rotation':
            await layouts.rotation_layout(q)
        elif _hash == 'menu/rgb2gray':
            await layouts.rgb2gray_layout(q)
        elif _hash == 'menu/histogram':
            await layouts.histogram_layout(q)
        elif _hash == 'menu/blur':
            await layouts.blur_layout(q)
        elif _hash == 'menu/histogram_eq':
            await layouts.histogram_eq_layout(q)

    if q.args.image_table:
        temp = await q.site.download(q.args.image_table[-1], '../data/')
        q.client.image = cv2.imread(temp)[:, :, ::-1]

        image_filename = ip.plot_image(q.client.image)
        content, = await q.site.upload([image_filename])
        os.remove(image_filename)
        await layouts.responsive_layout(q, content, layouts.transformation_layout)

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

    if q.args.ave_blur:
        await U.average_blur(q)
    elif q.args.gaussian_blur:
        await U.gaussian_blur(q)
    elif q.args.median_blur:
        await U.median_blur(q)
    elif q.args.bil_blur:
        await U.bilateral_blur(q)
    elif q.args.reset_blur:
        await U.reset_blur(q)

    if not q.client.initialized:
        q.client.initialized = True
        image_filename = ip.plot_image(q.client.image)
        content, = await q.site.upload([image_filename])
        os.remove(image_filename)

        await layouts.responsive_layout(q, content, layouts.transformation_layout)

    await q.page.save()


