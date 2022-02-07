from dash import dcc
from dash import html

import base64
import pathlib
from calendar import isleap
from datetime import datetime

import utils
import data_analysis

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
ASSETS_PATH = BASE_PATH.joinpath("assets").resolve()


def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Welcome to the ChatDash"),
            html.Div(
                id="intro",
                children=[
                    # html.P("ChatDash is an app for analysing chat data that has been beWhatsApp chata cata."),
                    html.P(
                        children=[
                            "ChatDash is an app for analysing chat data which has been ",
                            html.A(
                                "exported from WhatsApp",
                                href="https://faq.whatsapp.com/android/chats/how-to-save-your-chat-history/?lang=en",
                            ),
                            ". On the right you can see a demo of what the analysis will look like.",
                        ]
                    ),
                    html.P(
                        children=[
                            html.Span(
                                "Simply load your chat file below to get started!",
                                style={"font-weight": "bold"},
                            ),
                            " Please note that loading may take a few seconds depending on the size of you file.",
                        ]
                    ),
                ],
            ),
        ],
    )


def get_faq():

    return html.Div(
        className="faq-wrapper",
        children=[
            html.Br(),
            html.Br(),
            html.Div(
                # className="faq",
                children=[
                    html.H5("FAQ"),
                    html.Button(
                        "How can I export my WhatsApp group chat?",
                        n_clicks=0,
                        className="collapsible",
                        id="fqa-b1",
                    ),
                    html.Div(
                        className="content",
                        children=[
                            html.P(
                                [
                                    "Open the individual or group chat. Tap on ",
                                    html.Span(
                                        "More options", style={"font-style": "italic"}
                                    ),
                                    html.Span(" > ", style={"font-weight": "bold"}),
                                    html.Span("More", style={"font-style": "italic"}),
                                    html.Span(" > ", style={"font-weight": "bold"}),
                                    "Export chat. ",
                                    html.Span(
                                        "Exporting without media is recommended.",
                                        style={"font-weight": "bold"},
                                    ),
                                ]
                            ),
                        ],
                        id="bt1-child",
                    ),
                    html.Button(
                        "Is my chat data stored anywhere?",
                        n_clicks=0,
                        className="collapsible",
                        id="fqa-b2",
                    ),
                    html.Div(
                        className="content",
                        children=[
                            html.P(
                                children=[
                                    "No! Everything runs locally in your browser and no data is sent to a server. If you don't want to take my word for it, you can check the code out on ",
                                    html.A(
                                        "Github",
                                        href="https://github.com/natworks/chatdash",
                                    ),
                                    ".",
                                ]
                            ),
                        ],
                        id="bt2-child",
                    ),
                    html.Button(
                        "Does it support data from other apps?",
                        n_clicks=0,
                        className="collapsible",
                        id="fqa-b3",
                    ),
                    html.Div(
                        className="content",
                        children=[
                            html.P(
                                "Probably not. ChatDash has been created for WhatsApp data and has not been tested on chats exported from Telegram, Signal, etc..."
                            ),
                        ],
                        id="bt3-child",
                    ),
                    html.Button(
                        "Why is my media information not displaying correctly?",
                        n_clicks=0,
                        className="collapsible",
                        id="fqa-b4",
                    ),
                    html.Div(
                        className="content",
                        children=[
                            html.P(
                                "Media information relies on parsing the file searching for certain key phrases. They vary according to your device's system langue. At the moment, ChatDash only supports English, Portuguese, and French."
                            ),
                        ],
                        id="bt4-child",
                    ),
                    html.Button(
                        children=["Other things don't work. Where can I complain?"],
                        n_clicks=0,
                        className="collapsible",
                        id="fqa-b5",
                    ),
                    html.Div(
                        className="content",
                        children=[
                            html.P(
                                children=[
                                    "You may yell at me on Twitter ",
                                    html.A(
                                        "@chatdashapp",
                                        href="https://twitter.com/chatdashapp",
                                    ),
                                    " or just email me ",
                                    html.A(
                                        "chatdashapp(at)gmail.com",
                                        href="mailto:chatdashapp@gmail.com",
                                    ),
                                    ".",
                                ]
                            ),
                        ],
                        id="bt5-child",
                    ),
                ]
            ),
        ],
    )


def get_usage_plots(chat_df, year: str = ""):
    author_names = list(chat_df["author"].unique())

    plot_title_add = f"in {year}" if year else ""

    month_chart, top_month = data_analysis.get_frequency_info(
        chat_df,
        "month",
        "Month",
        utils.MONTHS,
        author_names,
        plot_title=f"Busiest Month {plot_title_add}",
    )
    day_chart, top_day = data_analysis.get_frequency_info(
        chat_df,
        "weekday",
        "Weekday",
        utils.WEEKDAYS,
        author_names,
        plot_title=f"Busiest Day of The Week {plot_title_add}",
    )
    hour_chart, top_hour = data_analysis.get_frequency_info(
        chat_df,
        "hour_of_day",
        "Hour of Day",
        utils.HOURS,
        author_names,
        plot_title=f"Busiest Hour of The Day {plot_title_add}",
    )

    top_hour_end = str(int(top_hour) + 1)

    if year:
        month_text = [
            f"In {year}, ",
            html.Span(
                f"{top_month}", style={"font-size": "18px", "font-weight": "bold"}
            ),
            " was the",
        ]
        day_text = [
            f"In {year}, ",
            html.Span(f"{top_day}", style={"font-size": "18px", "font-weight": "bold"}),
            " was the",
        ]
        hour_text = [
            html.Span(
                f"{top_hour}:00 to {top_hour_end}:00",
                style={"font-size": "18px", "font-weight": "bold"},
            ),
            f" was when the chat was the busiest in {year}.",
        ]
    else:
        month_text = [
            "Overall, ",
            html.Span(
                f"{top_month}", style={"font-size": "18px", "font-weight": "bold"}
            ),
            " is the ",
        ]
        day_text = [
            "Over the years, ",
            html.Span(f"{top_day}", style={"font-size": "18px", "font-weight": "bold"}),
            " has been the",
        ]
        hour_text = [
            "From ",
            html.Span(
                f"{top_hour}:00", style={"font-size": "18px", "font-weight": "bold"}
            ),
            " to ",
            html.Span(
                f"{top_hour_end}:00", style={"font-size": "18px", "font-weight": "bold"}
            ),
            " is when the chat is normally most alive.",
        ]

    return [
        html.P(children=month_text + [" busiest month of the year."]),
        dcc.Graph(figure=month_chart),
        html.P(children=day_text + [" busiest day of the week."]),
        dcc.Graph(figure=day_chart),
        html.P(hour_text),
        dcc.Graph(figure=hour_chart),
    ]


def get_emojis(chat_df):
    top_emojis = data_analysis.display_favourite_emojis(chat_df)
    as_str = "                   ".join(em for em in top_emojis)
    return html.H1(
        as_str, style={"width": "100%", "text-align": "center", "font-size": "86px"}
    )


def get_biggest_spammer(chat_df, time_frame=["", "is", "have"]):
    (
        spammer,
        favourite_source,
        source_quantity,
        fig,
    ) = data_analysis.display_biggest_spammer(chat_df)
    return [
        html.P(
            [
                time_frame[0],
                html.Span(f"{spammer}", style={"font-size": "28px"}),
                f" {time_frame[1]} the biggest spammer in your group. Their favourite source {time_frame[1]} ",
                html.A(f"{favourite_source}", href=f"{favourite_source}"),
                f". In fact, they {time_frame[2]} shared this website alone {source_quantity} times.",
            ]
        ),
        dcc.Graph(figure=fig),
    ]


def get_media_info(chat_df, source):
    gif_person, fig_gif, audio_person, fig_audio = data_analysis.display_media_person(
        chat_df, source
    )

    if fig_gif is None:
        encoded_image = base64.b64encode(
            open(ASSETS_PATH.joinpath("error.png"), "rb").read()
        )
        return [
            html.Img(
                src=utils.HTML_IMG_SRC_PARAMETERS + encoded_image.decode(),
                style={
                    "display": "block",
                    "margin-left": "auto",
                    "margin-right": "auto",
                    "width": "50%",
                },
            ),
            html.Caption(
                children=[
                    "Original Image by: Who’s Denilo ?",
                    html.A(
                        "(@whoisdenilo)",
                        href="https://unsplash.com/@whoisdenilo",
                    ),
                    " from Unsplash",
                ],
                style={
                    "display": "block",
                    "margin-left": "auto",
                    "margin-right": "auto",
                    "width": "100%",
                    "font-size": "10px",
                },
            ),
        ]

    if fig_audio:
        return [
            html.P(
                [
                    "Sharing gifs is a skill that ",
                    html.Span(f"{gif_person}", style={"font-size": "28px"}),
                    " has certaily mastered.",
                ]
            ),
            dcc.Graph(figure=fig_gif),
            html.P(
                [
                    html.Span(f"{audio_person}", style={"font-size": "28px"}),
                    " is almost a podcast host considering their audios stats. Don't forget to like and subscribe!",
                ]
            ),
            dcc.Graph(figure=fig_audio),
        ]
    else:
        return [
            html.P(
                [
                    html.Span(f"{gif_person}", style={"font-size": "28px"}),
                    f" is just sitting there sharing audios and gifs. They have sent a whopping {audio_person} messages containing media this year.",
                ]
            ),
            dcc.Graph(figure=fig_gif),
        ]


def get_word_cloud(df):
    wc = data_analysis.generate_word_cloud(df)
    return html.Img(
        src=utils.HTML_IMG_SRC_PARAMETERS + utils.pil_to_b64(wc, enc_format="png"),
        width="100%",
    )


def get_busiest_day(df, years):
    date, msg_count = data_analysis.get_busiest_day(df)
    time_gap_text, gap_start, gap_end = data_analysis.get_biggest_msg_gap(df)

    day = utils.day_text(str(date[0]))

    right_now = datetime.now(tz=None)
    if years == "All years" or years == str(right_now.year):
        days_so_far = (
            right_now - df.iloc[0, df.columns.get_loc("datetime")].replace(tzinfo=None)
        ).days
    else:
        days_so_far = 366 if isleap(int(years)) else 365

    if years == "All years":
        return html.Header(
            children=[
                "It has been ",
                html.Span(
                    f"{days_so_far} days",
                    style={"font-size": "16px", "font-weight": "bold"},
                ),
                " since the first available message in this group. That is an average of ",
                html.Span(
                    f"{df.shape[0]//days_so_far} messages",
                    style={"font-size": "16px", "font-weight": "bold"},
                ),
                f" per day. The quiest period happened between the {utils.day_text(str(gap_start['day_of_month']))} of {gap_start['month']} \
             of {gap_start['year']} and the {utils.day_text(str(gap_end['day_of_month']))} of {gap_end['month']} of {gap_end['year']}, a total of ",
                html.Span(
                    f"{time_gap_text}",
                    style={"font-size": "16px", "font-weight": "bold"},
                ),
                f" without messages. The busiest day has been the {day} of {date[1]} of {date[2]} when a total of ",
                html.Span(
                    f"{msg_count} messages",
                    style={"font-size": "16px", "font-weight": "bold"},
                ),
                " were sent.",
            ]
        )
    else:
        return html.Header(
            children=[
                "In ",
                html.Span(
                    f"{years}", style={"font-size": "16px", "font-weight": "bold"}
                ),
                " your group shared an average of ",
                html.Span(
                    f"{df.shape[0]//days_so_far} messages",
                    style={"font-size": "16px", "font-weight": "bold"},
                ),
                f" per day. The quiest period happened between the {utils.day_text(str(gap_start['day_of_month']))} of {gap_start['month']} \
             of {gap_start['year']} and the {utils.day_text(str(gap_end['day_of_month']))} of {gap_end['month']} of {gap_end['year']}, a total of ",
                html.Span(
                    f"{time_gap_text}",
                    style={"font-size": "16px", "font-weight": "bold"},
                ),
                f" without messages. The busiest day was the {day} of {date[1]} of {date[2]} when a total of ",
                html.Span(
                    f"{msg_count} messages",
                    style={"font-size": "16px", "font-weight": "bold"},
                ),
                " were sent.",
            ]
        )


def initialise_table(df):
    children = []
    figure, total_msgs = data_analysis.display_num_of_messages(
        df, plot_title="Total Number of Messages"
    )
    children.append(
        html.P(
            [
                "Your group has shared a total of ",
                html.Span(
                    f"{total_msgs:,} messages.",
                    style={"font-size": "18px", "font-weight": "bold"},
                ),
            ]
        )
    )
    children.append(dcc.Graph(figure=figure))
    return children


def initialise_chatting(df):
    return get_usage_plots(df)


def initialise_responder(df):
    fig = data_analysis.get_first_responders(df)
    return dcc.Graph(figure=fig)


def initialise_emojis(df):
    return get_emojis(df)


def initialise_media(df):
    return get_biggest_spammer(df) + get_media_info(df, source="android")


def get_image_html(images, captions):
    images_to_display = []
    for i in range(len(images)):
        images_to_display += [
            html.Img(
                src=utils.HTML_IMG_SRC_PARAMETERS
                + utils.pil_to_b64(images[i], enc_format="png"),
                width="100%",
            ),
            html.Caption(
                children=[
                    "Original Image by: ",
                    html.A(
                        f"{captions[i][0]}",
                        href=f"https://unsplash.com/{captions[i][1]}?utm_source=ChatDash&utm_medium=referral",
                    ),
                    " on ",
                    html.A(
                        "Unsplash",
                        href="https://unsplash.com/?utm_source=ChatDash&utm_medium=referral",
                    ),
                ],
                style={
                    "display": "block",
                    "margin-left": "auto",
                    "margin-right": "auto",
                    "width": "100%",
                    "font-size": "10px",
                    "margin-top": "0px",
                    "margin-bottom": "10px",
                },
            ),
        ]

    return images_to_display


def initialise_quotes(df):

    quotes = data_analysis.display_quote(df)

    if quotes is None:
        return None

    return get_image_html(quotes[0], quotes[1])


def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag and Drop or ", html.A("chat file (.txt)")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "5px",
                },
                # Allow multiple files to be uploaded
                multiple=False,
                accept=".txt",
            ),
            dcc.Store(id="original-df"),
            html.Div(id="output-data-upload", children=[]),
        ],
    )


def get_year_dropdown(years):
    return [
        html.Br(),
        html.P("Please select the year you wish to analyse"),
        dcc.Dropdown(
            # id="year-select",
            id={"type": "filter-dropdown", "index": 0},
            options=[{"label": i, "value": i} for i in years],
            value=years[0],
        ),
    ]


def get_numbers_dropdown(author_names, phone_numbers):

    box = [
        html.Br(),
        html.P(
            "Some of you friends have changed numbers over the years. For a more accurate analysis, please specify their owners."
        ),
    ]
    names = ["Use number"] + author_names
    for dp_n, number in enumerate(phone_numbers):
        box.append(html.B(f"Phone {number} belongs to:"))
        box.append(
            dcc.Dropdown(
                id={"type": "number-dropdowns", "index": dp_n},
                options=[{"label": i, "value": i} for i in names],
                value=names[0],
            )
        )
    return box


def get_data_loading_error_message():
    error_data_loading = base64.b64encode(
        open(ASSETS_PATH.joinpath("sad.jpg"), "rb").read()
    )
    return [
        html.P(
            children=[
                "Hi there! Unfortunately, we are currently unable to read the file you have tried to upload and can't analyse your chat right now. Please report this issue by either sending an email to ",
                html.A("chatdashapp(at)gmail.com", href="mailto:chatdashapp@gmail.com"),
                " or creating a new issue on ",
                html.A("Github", href="https://github.com/natworks/chatdash/issues"),
                ".",
            ],
            style={
                "margin-top": "5rem",
            },
        ),
        html.Img(
            src=utils.HTML_IMG_SRC_PARAMETERS + error_data_loading.decode(),
            style={
                "display": "block",
                "margin-left": "auto",
                "margin-right": "auto",
                "margin-top": "10rem",
                "width": "50%",
            },
        ),
        html.Caption(
            children=[
                "Original Image by: ",
                html.A(
                    "Matthew Henry",
                    href="https://unsplash.com/@matthewhenry?utm_source=ChatDash&utm_medium=referral",
                ),
                " on ",
                html.A(
                    "Unsplash",
                    href="https://unsplash.com/?utm_source=ChatDash&utm_medium=referral",
                ),
            ],
            style={
                "display": "block",
                "margin-left": "auto",
                "margin-right": "auto",
                "width": "100%",
                "font-size": "10px",
            },
        ),
    ]
