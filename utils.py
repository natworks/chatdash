import time
import base64
from io import BytesIO as _BytesIO


# Image utility functions
def pil_to_b64(im, enc_format="png", verbose=False, **kwargs):
    """
    Converts a PIL Image into base64 string for HTML displaying
    Shamelessly copied from https://github.com/plotly/dash-image-processing/blob/master/dash_reusable_components.py
    :param im: PIL Image object
    :param enc_format: The image format for displaying. If saved the image will have that extension.
    :return: base64 encoding
    """
    t_start = time.time()
    buff = _BytesIO()
    im.save(buff, format=enc_format, **kwargs)
    encoded = base64.b64encode(buff.getvalue()).decode("utf-8")

    if verbose:
        print(f"PIL converted to b64 in {time.time() - t_start:.3f} sec")

    return encoded
