import base64
import io


def get_image_from_matplotlib(matplotlib_obj, dpi=90):
    buffer = io.BytesIO()
    matplotlib_obj.savefig(buffer, format="png", dpi=dpi)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
