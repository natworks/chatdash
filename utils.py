import time
import base64
from matplotlib import cm
from io import BytesIO as _BytesIO
from wordcloud import STOPWORDS

# Variables
HTML_IMG_SRC_PARAMETERS = "data:image/png;base64, "

BASE_CSS = {
    "padding": "0 18px",
    "max-height": "0",
    "overflow": "hidden",
    "transition": "max-height 0.2s ease-out",
    "background-color": "#f1f1f1",
}
SHOWY_CSS = BASE_CSS.copy()
SHOWY_CSS["max-height"] = "300px"

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
DATE_ENDINGS = {
    "1": "1st",
    "21": "21st",
    "31": "31st",
    "2": "2nd",
    "22": "22nd",
    "3": "3rd",
    "23": "23rd",
}
HOURS = [t for t in range(24)]
CMAP = cm.get_cmap("RdYlBu")

stopwords = set(STOPWORDS)
stopwords.update(
    [
        "os",
        "tb",
        "também",
        "sei",
        "para",
        "por",
        "kkkkk",
        "seu",
        "sua" "as",
        "mais",
        "mesmo",
        "hahahaha",
        "de",
        "o",
        "a",
        "se",
        "da",
        "que",
        "ai",
        "ta",
        "são",
        "aí",
        "q",
        "só",
        "foi",
        "meu",
        "por",
        "para",
        "e",
        "na",
        "image",
        "jpeg",
        "gif",
        "png",
        "pra",
        "ou",
        "pq",
        "em",
        "na",
        "e",
        "tem",
        "vc",
        "você",
        "eh",
        "não",
        "image/gif",
        "video/mp4",
        "lol",
        "LOL",
        "Yeah",
        "https",
        "haha" "pra",
        "é",
        "ma",
        "esse",
        "essa",
        "nao",
        "sim",
        "tá",
        "já",
        "to",
        "tô",
        "ja",
        "kkkkkk" "não",
        "mas",
        "eu",
        "uma",
        "um",
        "umas",
        "uns",
        "isso",
        "aqui",
        "Media",
        "omitted",
        "hahaha",
        "ele",
        "ela",
        "lol",
        "ver",
        "ser",
        "gente",
        "acho",
        "nossa",
        "dele",
        "dela",
        "mais",
        "muito",
        "já",
        "quando",
        "mesmo",
        "depois",
        "ainda",
        "hj",
        "tbm",
        "deu",
        "de",
        "pro",
        "nem",
        "Ah",
        "lá",
        "kkkkkk",
        "até",
        "como",
        "bem",
        "mim",
        "desse",
        "dessa",
        "vai",
        "tava",
        "era",
        "tipo",
        "mto",
        "mt",
        "mta",
        "te",
        "vou",
        "das",
        "dos",
        "tá",
        "minha",
        "meu",
        "dá",
        "Ahh",
        "faz",
        "rsrs",
        "kkk",
        "haha",
        "tenho",
        "quem",
        "estou",
        "ia",
        "sem",
        "kkkkkkk",
        "nas",
        "tão",
        "muita",
        "vez",
        "vcs",
        "dar",
        "vocês",
        "né",
        "está",
        "então",
        "nos",
        "nós",
        "viu",
        "ne",
        "num",
        "td",
        "kkkk",
        "sua",
        "seu",
        "ao",
        "esta",
        "fez",
        "imagem",
        "ocultada",
        "ocultado",
        "áudio",
        "figurinha",
        "omitida",
        "assim",
        "pode",
        "vem",
        "ok",
        "vi",
        "hahahahaha",
        "la",
        "bom",
        "vídeo",
        "omitido",
        "msm",
        "ir",
        "youtube",
        "youtu",
        "S",
        "Oh",
        "though",
        "tho",
        "well",
        "omis",
        "absente",
        "retiré",
    ]
)

GIF_OMITTED_LANG = {"pt": "GIF omitido", "en": "GIF omitted", "fr": "GIF retiré"}

AUDIO_OMITTED_LANG = {"pt": "áudio ocultado", "en": "audio omitted", "fr": "audio omis"}

ANDROID_MEDIA_OMITTED_TO_LANG = {
    "<Média omis>": "fr",
    "<Mídia omitida>": "pt",
    "<Media omitted>": "en",
}

ANDROID_MEDIA_OMITTED = list(ANDROID_MEDIA_OMITTED_TO_LANG.keys())

IPHONE_MEDIA_OMITTED = {item: key for key, item in GIF_OMITTED_LANG.items()}


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


def day_text(number):

    if number in DATE_ENDINGS:
        return DATE_ENDINGS[number]
    else:
        return f"{number}th"
