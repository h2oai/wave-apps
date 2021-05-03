import cv2
import numpy as np
import matplotlib.pyplot as plt
import uuid
from skimage.exposure import match_histograms


def image_translation(image, tx, ty):
    m = np.float32([[1, 0, tx], [0, 1, ty]])
    translated_image = cv2.warpAffine(image, m, (image.shape[1], image.shape[0]))
    return translated_image


def image_rotation(image, point=None, angle=None, scale=1):
    if not point:
        # use center point
        point = (image.shape[1] // 2, image.shape[0] // 2)

    m = cv2.getRotationMatrix2D(point, angle, scale)
    rotated_image = cv2.warpAffine(image, m, (image.shape[1], image.shape[0]))
    return rotated_image


def rgb2gray(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


# def plot_image(image):
#     x = np.linspace(0, 10, image.shape[0])
#     y = np.linspace(0, 10, image.shape[1])
#     p = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])
#     p.x_range.range_padding = p.y_range.range_padding = 0
#
#     image = ImageRGBA()
#     # must give a vector of image data for image parameter
#     p.image(image=[image], x=0, y=0, dw=10, dh=10, palette="Spectral11", level="image")
#     html = file_html(p, CDN)
#     return html


def plot_image(image, cmap=None):
    fig = plt.figure(figsize=(10, 10))
    _ = plt.imshow(image, cmap=cmap)

    image_filename = f'{str(uuid.uuid4())}.png'
    plt.savefig(image_filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f'file saved at {image_filename}')

    return image_filename


def generate_histogram(image):
    histB = cv2.calcHist([image], [2], None, [256], [0, 256])
    histG = cv2.calcHist([image], [1], None, [256], [0, 256])
    histR = cv2.calcHist([image], [0], None, [256], [0, 256])

    _ = plt.figure()
    _ = plt.title('RGB Histogram')
    _ = plt.xlabel('Bins from 0 - 255')
    _ = plt.ylabel('# of pixels')
    _ = plt.plot(histB, color='blue')
    _ = plt.plot(histG, color='green')
    _ = plt.plot(histR, color='red')
    _ = plt.xlim([0, 256])

    hist_filename = f'{str(uuid.uuid4())}.png'
    plt.savefig(hist_filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    print(f'file saved at {hist_filename}')

    return hist_filename


def average_blurring(image: np.array, filter_size: tuple = (5, 5)):
    return cv2.blur(image, filter_size)


def gaussian_blurring(image: np.array, filter_size: tuple = (5, 5), std: float = 0):
    return cv2.GaussianBlur(image, filter_size, std)


def median_blurring(image: np.array, kernel_size: int = 5):
    return cv2.medianBlur(image, kernel_size)


def bilateral_blurring(image: np.array, kernel_size: int = 5, colors: int = 21, sigma: int = 0):
    return cv2.bilateralFilter(image, kernel_size, colors, sigma)


def histogram_matching(image: np.array, reference: np.array, multi_channel: bool = True):
    return match_histograms(image, reference, multichannel=multi_channel)


def hist_match_plot(image, title):
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))

    histB = cv2.calcHist([image], [2], None, [256], [0, 256])
    histG = cv2.calcHist([image], [1], None, [256], [0, 256])
    histR = cv2.calcHist([image], [0], None, [256], [0, 256])

    ax1.imshow(image)
    ax2.plot(histB, color='blue')
    ax2.plot(histR, color='red')
    ax2.plot(histG, color='green')

    plt.tight_layout()
    fig.suptitle(title)
    hist_filename = f'{str(uuid.uuid4())}.png'
    plt.savefig(hist_filename, pad_inches=0, transparent=True)
    plt.close()
    print(f'file saved at {hist_filename}')

    return hist_filename


def edge_detection(image: np.array, kernel: str = 'laplace', smoothing: bool = False):
    if smoothing:
        image = gaussian_blurring(image, (3, 3), 0)
    if kernel == 'laplace':
        lap_gradient = cv2.Laplacian(image, cv2.CV_64F)
        lap_gradient = np.uint(np.absolute(lap_gradient))

        return lap_gradient
    elif kernel == 'sobel':
        sob_gradient_x = cv2.Sobel(image, cv2.CV_64F, 1, 0)
        sob_gradient_y = cv2.Sobel(image, cv2.CV_64F, 0, 1)

        sob_gradient_x = np.uint(np.absolute(sob_gradient_x))
        sob_gradient_y = np.uint(np.absolute(sob_gradient_y))

        return cv2.bitwise_or(sob_gradient_x, sob_gradient_y)

