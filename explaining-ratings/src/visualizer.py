import io
import base64

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

stopwords = set(STOPWORDS)


def plot_word_cloud(text):
    word_cloud = WordCloud(
        background_color='white', stopwords=stopwords, min_font_size=10).generate(text)

    plt.figure(figsize=(10, 10))
    plt.imshow(word_cloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    return get_image_from_matplotlib(plt)


def get_image_from_matplotlib(matplotlib_obj):
    buffer = io.BytesIO()
    matplotlib_obj.savefig(buffer, format="png")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
