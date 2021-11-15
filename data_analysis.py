import re
import requests
import numpy as np
import pandas as pd
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import emoji
import plotly
from matplotlib import cm
import plotly.express as px
import plotly.graph_objects as go

import data_cleaning
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

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
HOURS = [t for t in range(24)]
CMAP = cm.get_cmap("RdYlBu")


def display_signal_analysis(chat_data: pd.DataFrame):
    pass


def get_date(row_idx, chat_data):
    date = datetime.strptime(
        "{}:{} {} {} {}".format(
            chat_data.iloc[row_idx, chat_data.columns.get_loc("hour_of_day")],
            chat_data.iloc[row_idx, chat_data.columns.get_loc("minute_of_hour")],
            chat_data.iloc[row_idx, chat_data.columns.get_loc("day_of_month")],
            chat_data.iloc[row_idx, chat_data.columns.get_loc("month")],
            chat_data.iloc[row_idx, chat_data.columns.get_loc("year")],
        ),
        "%H:%M %d %B %Y",
    )
    return date


def get_quietest_interval(chat_data):
    deltas = [0]
    previous_date = get_date(0, chat_data)

    for i in range(1, chat_data.shape[0]):
        current_date = get_date(i, chat_data)
        deltas.append((current_date - previous_date).total_seconds())
        previous_date = current_date

    quiest_interval = max(deltas)
    return deltas.index(quiest_interval), quiest_interval


def convert_seconds(seconds):
    day = int(seconds // (24 * 3600))
    time = seconds % (24 * 3600)
    hour = int(time // 3600)
    time %= 3600
    minutes = int(time // 60)
    time %= 60
    seconds = int(time)

    if day > 0:
        return "{} days {} hours and {} minutes".format(day, hour, minutes)
    elif hour > 0:
        return "{} hours and {} minutes".format(hour, minutes)
    elif minutes > 0:
        return "{} minutes".format(minutes)
    else:
        return "{} seconds".format(seconds)


def display_msg_gap(chat_data: pd.DataFrame):

    daily_average = chat_data.shape[0] // 365
    quiest_interval_id, delta_in_seconds = get_quietest_interval(chat_data)
    formatted_time = convert_seconds(delta_in_seconds)
    interval_start = "{} of {}".format(
        chat_data.iloc[
            quiest_interval_id - 1, chat_data.columns.get_loc("day_of_month")
        ],
        chat_data.iloc[quiest_interval_id - 1, chat_data.columns.get_loc("month")],
    )
    interval_end = "{} of {}".format(
        chat_data.iloc[quiest_interval_id, chat_data.columns.get_loc("day_of_month")],
        chat_data.iloc[quiest_interval_id, chat_data.columns.get_loc("month")],
    )


def display_num_of_messages(chat_data: pd.DataFrame, per_year: bool = False):
    """
    Biggest Message block
    """
    column = "year" if per_year else "author"
    msg_count = chat_data[column].value_counts().to_frame()
    msg_count.reset_index(inplace=True)
    msg_count.columns = [column.capitalize(), "Count"]
    total_msgs = msg_count["Count"].sum()

    fig = px.bar(
        msg_count,
        y="Count",
        text="Count",
        x=column.capitalize(),
        color="Count",
        color_continuous_scale=plotly.colors.sequential.Sunset,
    )
    fig.update_traces(
        texttemplate="%{text:.2s}", textposition="outside", showlegend=False
    )  # , marker_coloraxis=None)
    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        plot_bgcolor="rgb(255,255, 255)",
        coloraxis_showscale=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgb(220,220,220)",
        title={"text": "Number of Messages"},
    )

    return fig, total_msgs


def get_frequency_info(chat_data, column, column_renamed, sorting_order, author_names):
    c_gaps = [
        (np.asarray(CMAP((i + 1) / len(author_names))[:-1]) * 255).astype(np.uint8)
        for i in range(len(author_names))
    ]
    markers = ["rgb({}, {}, {})".format(e[0], e[1], e[2]) for e in c_gaps]

    all_col_names = set(chat_data[column].unique())
    data = []
    values = [0] * len(all_col_names)
    for c, author in enumerate(author_names):
        individual_info = (
            chat_data[chat_data["author"] == author][column].value_counts().to_frame()
        )
        individual_info.reset_index(inplace=True)
        individual_info.columns = [column_renamed, "Messages"]

        person = set(individual_info[column_renamed].unique())

        if all_col_names != person:
            diff = all_col_names - person
            for d in diff:
                individual_info = individual_info.append(
                    {column_renamed: d, "Messages": 0}, ignore_index=True
                )
        tmp = individual_info.set_index(column_renamed, drop=False)
        available_data = individual_info[column_renamed].to_list()
        ordered_data = [v for v in sorting_order if v in available_data]
        sorted_data = tmp.loc[ordered_data]
        values += sorted_data.to_numpy()[:, 1]
        data.append(
            go.Bar(
                name=author,
                x=ordered_data,
                y=list(sorted_data["Messages"]),
                marker_color=markers[c],
            )
        )

    fig = go.Figure(data=data)
    fig.update_layout(barmode="stack")
    fig.update_layout(
        uniformtext_minsize=8, uniformtext_mode="hide", plot_bgcolor="rgb(255,255, 255)"
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgb(220,220,220)",
        title={"text": "Number of Messages"},
    )
    fig.update_xaxes(title={"text": column_renamed})

    return fig, ordered_data[np.argmax(values)]


def display_favourite_emojis(chat_data: pd.DataFrame):
    text = " ".join(str(msg) for msg in chat_data.body)
    all_emojis = "".join(word for word in text if emoji.is_emoji(word))

    unique_emojis = list(set(all_emojis))
    emoji_count = []

    for emoj in unique_emojis:
        count = all_emojis.count(emoj)
        emoji_count.append(count)

    arg_sorted = np.argsort(
        emoji_count,
    )[::-1]
    top_emojis = [unique_emojis[arg_sorted[i]] for i in range(5)]
    return top_emojis


def display_biggest_spammer(chat_data: pd.DataFrame):
    author_names, _ = data_cleaning.get_users(chat_data)
    links_per_user = []
    favourite_site = []

    for author in author_names:
        author_msgs = chat_data[chat_data["author"] == author]
        author_msgs_list = " ".join(str(msg) for msg in author_msgs.body)
        websites = re.findall(
            "https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", author_msgs_list
        )
        unique_websites = list(set(websites))
        links_per_user.append(len(websites))
        if len(websites) > 0:
            counts = [websites.count(site) for site in unique_websites]
            sorted_idx = np.argsort(
                counts,
            )[::-1]
            favourite_site.append(
                [unique_websites[sorted_idx[0]], counts[sorted_idx[0]]]
            )
        else:
            favourite_site.append([0, 0])

    idx_spammer = links_per_user.index(max(links_per_user))
    return (
        author_names[idx_spammer],
        favourite_site[idx_spammer][0],
        favourite_site[idx_spammer][1],
    )


def split_sentence(input_phrase, char_per_line=22):
    sentences = ""
    text = ""
    all_words = input_phrase.split(" ")
    start = 0
    complete = False
    while not complete:
        text = ""
        for idx in range(start, len(all_words)):
            tmp_text = text + all_words[idx]
            if len(tmp_text) > char_per_line:
                start = idx
                sentences += f"{text}\n"
                break
            else:
                text += f"{all_words[idx]} "
                start = idx

        if start == len(all_words) - 1 and len(tmp_text) < char_per_line:
            sentences += f"{text}\n"
            complete = True

    return sentences


def display_quote(chat_data: pd.DataFrame):
    count = 0
    images = {}
    captions = {}
    
    url = f"https://api.unsplash.com/photos/random/?topics=='nature'&count=3&orientation=landscape&client_id={YOUR_ACCESS_KEY}"

    r = requests.get(url)  # , data=token_data, headers=token_headers)
    token_response_data = r.json()

    font = ImageFont.truetype(
        "./fonts/philosopher/Philosopher-BoldItalic.ttf", 32, encoding="unic"
    )

    while count < 3:
        i = np.random.randint(0, chat_data.shape[0], size=1)[0]
        txt = "'{}'".format(chat_data.iloc[i, chat_data.columns.get_loc("body")])
        author = chat_data.iloc[i, chat_data.columns.get_loc("author")]

        if (
            5 < len(txt) < 200
            and "<Media omitted>" not in txt
            and "kkk" not in txt
            and "haha" not in txt
            and "http" not in txt
            and "gif" not in txt
            and "GIF" not in txt
            and "vídeo" not in txt
            and "video" not in txt
            and "image" not in txt
            and "audio" not in txt
        ):

            response = requests.get(
                token_response_data[count]["urls"]["raw"] + "&w=600"
            )
            images[count] = Image.open(BytesIO(response.content))
            captions[count] = "Original Image by: {} ({}) from Unsplash".format(
                token_response_data[count]["user"]["name"],
                token_response_data[count]["user"]["links"]["html"].split("/")[-1],
            )

            d = ImageDraw.Draw(images[count])
            width, height = images[count].size

            sentences = split_sentence(txt, char_per_line=26)

            d.multiline_text(
                (int(width * 0.1), int(height * 0.05)),
                "{}".format(sentences),
                font=font,
                fill=(255, 255, 255),
            )
            d.multiline_text(
                (int(width * 0.40), int(height * 0.85)),
                "-{}".format(author),
                font=font,
                fill=(255, 255, 255),
            )
            count += 1

    return images, captions


def handle_signal_media(chat_data: pd.DataFrame):
    author_names, _ = data_cleaning.get_users(chat_data)
    gifs_per_author = []
    audios_per_author = []

    for author in author_names:
        author_msgs = chat_data[chat_data["author"] == author]
        author_msgs_list = " ".join(str(msg) for msg in author_msgs.body)
        gifs = re.findall("image/gif", author_msgs_list)
        audios = re.findall("audio/aac", author_msgs_list)
        videos = re.findall("video/mp4", author_msgs_list)
        gifs_per_author.append(len(gifs) + len(videos))
        audios_per_author.append(len(audios))

    idx_gif_spammer = gifs_per_author.index(max(gifs_per_author))
    gif_person = author_names[idx_gif_spammer]

    idx_audio_spammer = audios_per_author.index(max(audios_per_author))
    audio_person = author_names[idx_audio_spammer]

    fig_gifs = px.pie(
        pd.DataFrame.from_dict({"authors": author_names, "media": gifs_per_author}),
        values="media",
        names="authors",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )

    fig_audios = px.pie(
        pd.DataFrame.from_dict({"authors": author_names, "media": audios_per_author}),
        values="media",
        names="authors",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )

    return gif_person, fig_gifs, audio_person, fig_audios


def handle_android_media(chat_data: pd.DataFrame, language: str):
    author_names, _ = data_cleaning.get_users(chat_data)
    media_per_author = []

    prase = "Mídia omitida" if language == "pt" else "<Media omitted>"

    for author in author_names:
        author_msgs = chat_data[chat_data["author"] == author]
        author_msgs_list = " ".join(str(msg) for msg in author_msgs.body)
        media = re.findall(prase, author_msgs_list)
        media_per_author.append(len(media))

    idx_media_spammer = media_per_author.index(max(media_per_author))
    media_person = author_names[idx_media_spammer]

    fig = px.pie(
        pd.DataFrame.from_dict({"authors": author_names, "media": media_per_author}),
        values="media",
        names="authors",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    return media_person, fig, max(media_per_author), []


def handle_iphone_media(chat_data: pd.DataFrame, language: str):
    author_names, _ = data_cleaning.get_users(chat_data)
    gifs_per_author = []
    audios_per_author = []

    gif_phrase = "GIF omitido" if language == "pt" else "GIF omitted"
    audio_phrase = "áudio ocultado" if language == "pt" else "audio omitted"

    for author in author_names:
        author_msgs = chat_data[chat_data["author"] == author]
        author_msgs_list = " ".join(str(msg) for msg in author_msgs.body)
        gifs = re.findall(gif_phrase, author_msgs_list)
        audios = re.findall(audio_phrase, author_msgs_list)
        gifs_per_author.append(len(gifs))
        audios_per_author.append(len(audios))

    idx_gif_spammer = gifs_per_author.index(max(gifs_per_author))
    gif_person = author_names[idx_gif_spammer]

    idx_audio_spammer = audios_per_author.index(max(audios_per_author))
    audio_person = author_names[idx_audio_spammer]

    fig_gif = px.pie(
        pd.DataFrame.from_dict({"authors": author_names, "media": gifs_per_author}),
        values="media",
        names="authors",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )

    fig_audio = px.pie(
        pd.DataFrame.from_dict({"authors": author_names, "media": audios_per_author}),
        values="media",
        names="authors",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )

    return gif_person, fig_gif, audio_person, fig_audio


def display_media_person(chat_data: pd.DataFrame, input_source: str):
    body = " ".join(str(msg) for msg in chat_data.body)
    language = "pt" if "omitida" in body else "en"
    if input_source == "signal":
        return handle_signal_media(chat_data)
    elif input_source == "android":
        return handle_android_media(chat_data, language)
    else:
        return handle_iphone_media(chat_data, language)
