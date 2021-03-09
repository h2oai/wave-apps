from h2o_wave import Q, app, ui, main
import os
import ip_utils as ip
import views.layout_utils as layouts
import cv2


async def do_translation(q: Q):
    image_name = ip.plot_image(ip.image_translation(q.client.image, q.args.translate_X, q.args.translate_Y))
    temp, = await q.site.upload([image_name])
    os.remove(image_name)
    q.page['transformed_image'].content = f'''![plot]({temp})\n
            Last Translation X = {q.args.translate_X}  Y = {q.args.translate_Y}
            '''


async def reset_translation(q: Q):
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})\n
            Last Translation X = {q.args.translate_X}  Y = {q.args.translate_Y}
            '''
    q.page['controls'].items[1].value = q.page['controls'].items[2].value = 0


async def do_rotation(q: Q):
    if q.args.x_point and q.args.y_point:
        point = (int(q.args.x_point), int(q.args.y_point))
        image_name = ip.plot_image(
            ip.image_rotation(q.client.image, point=point, angle=q.args.rotate))
    else:
        image_name = ip.plot_image(
            ip.image_rotation(q.client.image, angle=q.args.rotate))
    temp, = await q.site.upload([image_name])
    os.remove(image_name)
    q.page['transformed_image'].content = f'''![plot]({temp})\n
                    Last Rotation= {q.args.rotate} around point ({q.args.x_point}, {q.args.y_point})'''


async def reset_rotation(q: Q):
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})\n
                    Last Rotation= {q.args.rotate}'''
    q.page['controls'].items[0].value = 0


async def do_rgb2gray(q: Q):
    image_name = ip.plot_image(ip.rgb2gray(q.client.image), cmap='gray')
    temp, = await q.site.upload([image_name])
    os.remove(image_name)
    q.page['transformed_image'].content = f'''![plot]({temp})'''


async def reset_rgb2gray(q: Q):
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})'''


async def get_histogram(q: Q):
    hist_name = ip.generate_histogram(q.client.image)
    hist, = await q.site.upload([hist_name])
    os.remove(hist_name)
    q.page['transformed_image'].content = f'''![plot]({hist})'''


async def average_blur(q: Q):
    if q.args.ave_filter_h and q.args.ave_filter_w:
        image_name = ip.plot_image(ip.average_blurring(
            q.client.image, filter_size=(int(q.args.ave_filter_w), int(q.args.ave_filter_h))))
    else:
        image_name = ip.plot_image(
            ip.average_blurring(q.client.image))

    temp, = await q.site.upload([image_name])
    os.remove(image_name)
    q.page['transformed_image'].content = f'''![plot]({temp})'''


async def gaussian_blur(q: Q):
    if q.args.gb_filter_h and q.args.gb_filter_w and q.args.gb_std:
        image_name = ip.plot_image(
            ip.gaussian_blurring(
                q.client.image, filter_size=(int(q.args.gb_filter_w), int(q.args.gb_filter_h)), std=float(q.args.gb_std)
            )
        )
    else:
        image_name = ip.plot_image(
            ip.gaussian_blurring(q.client.image))

    temp, = await q.site.upload([image_name])
    os.remove(image_name)
    q.page['transformed_image'].content = f'''![plot]({temp})'''


async def median_blur(q: Q):
    if q.args.med_kernel:
        image_name = ip.plot_image(ip.median_blurring(q.client.image, int(q.args.med_kernel)))
    else:
        image_name = ip.plot_image(
            ip.median_blurring(q.client.image))

    temp, = await q.site.upload([image_name])
    os.remove(image_name)
    q.page['transformed_image'].content = f'''![plot]({temp})'''


async def bilateral_blur(q: Q):
    if q.args.bil_kernel and q.args.bil_color and q.args.bil_sigma:
        image_name = ip.plot_image(ip.bilateral_blurring(
            q.client.image, int(q.args.bil_kernel), int(q.args.bil_color), int(q.args.bil_sigma)))
    else:
        image_name = ip.plot_image(
            ip.bilateral_blurring(q.client.image))

    temp, = await q.site.upload([image_name])
    os.remove(image_name)
    q.page['transformed_image'].content = f'''![plot]({temp})'''


async def reset_blur(q: Q):
    image_filename = ip.plot_image(q.client.image)
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)
    q.page['transformed_image'].content = f'''![plot]({content})'''

    q.page['controls_b0'].items[0].value = \
        q.page['controls_b0'].items[1].value = 0
    q.page['controls_b1'].items[0].value = \
        q.page['controls_b1'].items[1].value = q.page['controls_b1'].items[2].value = 0
    q.page['controls_b2'].items[0].value = 0
    q.page['controls_b2'].items[0].value = \
        q.page['controls_b2'].items[1].value = q.page['controls_b2'].items[2].value = 0


async def load_image(q: Q):
    if q.client.load_image_hist_eq:
        if q.client.load_count == 0:
            temp = await q.site.download(q.args.image_table[-1], '../data/')
            q.client.image = cv2.imread(temp)[:, :, ::-1]

            # keep copy of src image for histogram matching
            q.client.hm_dict = {'src': q.client.image.copy()}

            image_filename = ip.hist_match_plot(q.client.image, 'Source')
            content, = await q.site.upload([image_filename])
            os.remove(image_filename)

            q.page['chart_hm0'].content = f'''![plot]({content})'''
            q.client.load_count += 1
        elif q.client.load_count == 1:
            temp = await q.site.download(q.args.image_table[-1], '../data/')
            q.client.image = cv2.imread(temp)[:, :, ::-1]

            # keep copy of reference image
            q.client.hm_dict['reference'] = q.client.image.copy()

            image_filename = ip.hist_match_plot(q.client.image, 'Reference')
            content, = await q.site.upload([image_filename])
            os.remove(image_filename)

            q.page['chart_hm1'].content = f'''![plot]({content})'''
            q.client.load_count += 1
    else:
        temp = await q.site.download(q.args.image_table[-1], '../data/')
        q.client.image = cv2.imread(temp)[:, :, ::-1]

        image_filename = ip.plot_image(q.client.image)
        content, = await q.site.upload([image_filename])
        os.remove(image_filename)
        q.page['original_image'].content = f'''![plot]({content})'''
        q.page['transformed_image'].content = f'''![plot]({content})'''


async def do_histogram_matching(q: Q):
    matched_image = ip.histogram_matching(q.client.hm_dict['src'], q.client.hm_dict['reference'])

    image_filename = ip.hist_match_plot(matched_image, 'Matched')
    content, = await q.site.upload([image_filename])
    os.remove(image_filename)

    q.page['matched_hm'].content = f'''![plot]({content})'''
