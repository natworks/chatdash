import re
import os
import requests
import numpy as np
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

import emoji
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from wordcloud import WordCloud
from dotenv import load_dotenv

load_dotenv()

import utils
import data_cleaning

ACCESS_KEY = os.getenv("ACCESS_KEY")

def get_busiest_day(chat_data: pd.DataFrame):
    unique_days = [
        [date, len(counts)]
        for date, counts in chat_data.groupby(
            ["day_of_month", "month", "year"]
        ).groups.items()
    ]
    count = [info[1] for info in unique_days]
    idx = count.index(max(count))
    return unique_days[idx]


def get_gap_string(timedelta):

    days = timedelta.days
    hours = timedelta.components.hours
    minutes = timedelta.components.minutes

    if days > 0:
        return "{} days {} hours and {} minutes".format(days, hours, minutes)
    elif hours > 0:
        return "{} hours and {} minutes".format(hours, minutes)
    elif minutes > 0:
        return "{} minutes".format(minutes)


def get_biggest_msg_gap(chat_data: pd.DataFrame):

    time_differences = chat_data["datetime"].diff()
    timedelta = time_differences.max()

    formatted_time = get_gap_string(timedelta)

    idx = time_differences.idxmax()

    gap_start = chat_data.iloc[idx - 1, :]
    gap_end = chat_data.iloc[idx, :]

    return formatted_time, gap_start, gap_end


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
        (np.asarray(utils.CMAP((i + 1) / len(author_names))[:-1]) * 255).astype(
            np.uint8
        )
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
                x=[str(e) for e in ordered_data],
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
    fig = px.pie(
        pd.DataFrame.from_dict({"authors": author_names, "links": links_per_user}),
        values="links",
        names="authors",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    return (
        author_names[idx_spammer],
        favourite_site[idx_spammer][0],
        favourite_site[idx_spammer][1],
        fig,
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

    url = f"https://api.unsplash.com/photos/random/?topics=='nature'&count=3&orientation=landscape&client_id={ACCESS_KEY}"

    r = requests.get(url)  # , data=token_data, headers=token_headers)
    token_response_data = r.json()

    font = ImageFont.truetype(
        "./fonts/philosopher/Philosopher-BoldItalic.ttf", 32, encoding="unic"
    )

    body_idx = chat_data.columns.get_loc("body")
    author_idx = chat_data.columns.get_loc("author")

    while count < 3:
        i = np.random.randint(0, chat_data.shape[0], size=1)[0]
        txt = "'{}'".format(chat_data.iloc[i, body_idx])
        author = chat_data.iloc[i, author_idx]

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
            and "omitido" not in txt
            and "omitida" not in txt
            and "ocultado" not in txt
        ):

            response = requests.get(
                token_response_data[count]["urls"]["raw"] + "&w=600"
            )
            images[count] = Image.open(BytesIO(response.content))
            captions[count] = [
                token_response_data[count]["user"]["name"],
                token_response_data[count]["user"]["links"]["html"].split("/")[-1],
            ]

            d = ImageDraw.Draw(images[count])
            width, height = images[count].size

            sentences = split_sentence(txt.strip(), char_per_line=26)

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


def handle_android_media(chat_data: pd.DataFrame, prase: str):
    author_names, _ = data_cleaning.get_users(chat_data)
    media_per_author = []

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

    gif_phrase = utils.GIF_OMITTED_LANG.get(language)
    audio_phrase = utils.AUDIO_OMITTED_LANG.get(language)

    gifs_per_author = []
    audios_per_author = []

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

    if input_source == "signal":
        return handle_signal_media(chat_data)
    else:
        body = " ".join(str(msg) for msg in chat_data.body)

        try:
            for android_media in utils.ANDROID_MEDIA_OMITTED:
                if android_media in body:
                    return handle_android_media(chat_data, android_media)

            for iphone_media in list(utils.IPHONE_MEDIA_OMITTED.keys()):
                if iphone_media in body:
                    return handle_iphone_media(
                        chat_data, utils.IPHONE_MEDIA_OMITTED[iphone_media]
                    )
        except:
            return None, None, None, None

        return None, None, None, None


def generate_word_cloud(chat_data: pd.DataFrame):
    text = " ".join(str(msg) for msg in chat_data.body)

    # Generate a word cloud image
    wc = WordCloud(
        stopwords=utils.stopwords,
        background_color="white",
        width=1600,
        height=1000,
        max_words=300,
        colormap="magma",
    ).generate(text)

    return wc.to_image()


def get_first_responders(chat_data: pd.DataFrame, authors: list = None):

    if authors is None:
        authors = list(chat_data["author"].unique())

    responder_matrix = np.zeros((len(authors), len(authors)))
    authors_id = {name: idx for idx, name in enumerate(authors)}

    col_id = chat_data.columns.get_loc("author")

    for author_idx, author in enumerate(authors):
        indices = chat_data[chat_data["author"] == author].index.values.astype(int)
        for idx in indices:
            if idx < chat_data.shape[0] - 2:
                responder = chat_data.iloc[idx + 1, col_id]
                if responder != author:
                    responder_matrix[author_idx][authors_id[responder]] += 1

    total_replied_msgs = np.sum(responder_matrix, axis=0)
    total_replied_msgs[np.where(total_replied_msgs == 0.0)] = 1e-3
    data = (responder_matrix / total_replied_msgs.reshape(-1, 1)) * 100
    z_text = np.around(data, decimals=2)

    names = [n.replace("+", "Num: +") for n in authors]

    fig = ff.create_annotated_heatmap(
        data,
        x=names,
        y=names,
        annotation_text=z_text,
        colorscale="blues",
        hoverinfo="z",
    )
    fig.update_xaxes(side="bottom", title={"text": "First Person to Respond"})
    fig.update_yaxes(title={"text": "Sender"})

    return fig
