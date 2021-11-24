import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL

import json
import time
import base64
from dash.html.Span import Span
import emoji
import pandas as pd
from io import BytesIO as _BytesIO
import pathlib

import utils
import data_cleaning
import data_analysis

# Variables
HTML_IMG_SRC_PARAMETERS = "data:image/png;base64, "

BASE_CSS = {
  "padding": "0 18px",
  "max-height": "0",
  "overflow": "hidden",
  "transition": "max-height 0.2s ease-out",
  "background-color": "#f1f1f1"
}
SHOWY_CSS = BASE_CSS.copy()
SHOWY_CSS["max-height"] = "300px"


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "ChatDash"

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Read data
default_df = pd.read_csv(DATA_PATH.joinpath("random_generator_v2.txt"))


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
                    "Simply load a group chat that has been ",
                    html.A(
                        "exported from WhatsApp",
                        href="https://faq.whatsapp.com/android/chats/how-to-save-your-chat-history/?lang=en",
                    ),
                    " and ChatDash will analyse it for you. On the right, you can see a demo of what the analysis will look like."
                    ]
            ),
        ]
    )

def get_faq():

    return html.Div(className="faq-wrapper", 
    children=[
        html.Div(
                # className="faq",
                children=[
                    html.H5("FAQ"),
                    html.Button("How can I export my WhatsApp group chat?", n_clicks=0, className="collapsible", id="fqa-b1"),
                    html.Div(className="content", children=[
                        html.P("Open the individual or group chat > Tap More options > More > Export chat. We recommend exporting without media."),
                    ], id="bt1-child"),
                    html.Button("Is my chat data stored anywhere?", n_clicks=0, className="collapsible", id="fqa-b2"),
                    html.Div(className="content", children=[
                        html.P("No! Everything runs locally in your browser and no data sent to a server. If you don't want to take my word for it, the code is freely available on github"),
                    ], id="bt2-child"),
                    html.Button("Does it only work for data from WhatsApp?", n_clicks=0, className="collapsible", id="fqa-b3"),
                    html.Div(className="content", children=[
                        html.P("As far as I know, yes. It has not been tested on data from any other platform."),
                    ], id="bt3-child"),
                    html.Button(children=["Things don't work. Where can I complain?"], n_clicks=0, className="collapsible", id="fqa-b4"),
                    html.Div(className="content", children=[
                        html.P("You may yell at me on @twitter or just email me @"),
                    ], id="bt4-child")
                ]
        )
    ]
)

def get_usage_plots(chat_df):
    author_names = list(chat_df["author"].unique())

    month_chart, top_month = data_analysis.get_frequency_info(
        chat_df, "month", "Month", data_analysis.MONTHS, author_names
    )
    day_chart, top_day = data_analysis.get_frequency_info(
        chat_df, "weekday", "Weekday", data_analysis.WEEKDAYS, author_names
    )
    hour_chart, top_hour = data_analysis.get_frequency_info(
        chat_df, "hour_of_day", "Hour of Day", data_analysis.HOURS, author_names
    )

    return [
        html.Header(f"{top_month} is the busiest month of the year"),
        dcc.Graph(figure=month_chart),
        html.Header(f"{top_day} is the busiest day of the week"),
        dcc.Graph(figure=day_chart),
        html.Header(f"{top_hour}:00hr is when the chat is most alive."),
        dcc.Graph(figure=hour_chart),
    ]


def get_emojis(chat_df):
    top_emojis = data_analysis.display_favourite_emojis(chat_df)
    as_str = "                   ".join(em for em in top_emojis)
    return html.H1(
        as_str, style={"width": "100%", "text-align": "center", "font-size": "86px"}
    )


def get_biggest_spammer(chat_df, time_frame=""):
    spammer, favourite_source, source_quantity = data_analysis.display_biggest_spammer(
        chat_df
    )
    return [
        html.Header(
            [
                html.Span(f"{spammer}", style={"font-size": "28px"}),
                " is the biggest spammer in your group. Their favourite source is ",
                html.A(f"{favourite_source}", href=f"{favourite_source}"),
                f". In fact, they have shared this website alone {source_quantity} times{time_frame}",
            ]
        ),
        # html.Img(src="./imgs/awkward.png"),
        html.Img(
            src=app.get_asset_url("imgs/awkward_copy.png"),
            style={
                "display": "block",
                "margin-left": "auto",
                "margin-right": "auto",
                "width": "50%",
            },
        ),
        html.Caption(
            "awkward..",
            style={
                "display": "block",
                "margin-left": "auto",
                "margin-right": "auto",
                "width": "100%",
                "font-size": "15px",
            },
        ),
    ]


def get_media_info(chat_df, source):
    gif_person, fig_gif, audio_person, fig_audio = data_analysis.display_media_person(
        chat_df, source
    )
    if fig_audio:
        return [
            html.Header(
                [
                    "Sharing gifs is a skill that ",
                    html.Span(f"{gif_person}", style={"font-size": "28px"}),
                    " has certaily mastered.",
                ]
            ),
            dcc.Graph(figure=fig_gif),
            html.Header(
                [
                    html.Span(f"{audio_person}", style={"font-size": "28px"}),
                    " is almost a podcast host considering their audios stats. Don't forget to like and subscribe!",
                ]
            ),
            dcc.Graph(figure=fig_audio),
        ]
    else:
        return [
            html.Header(
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
            src=HTML_IMG_SRC_PARAMETERS + utils.pil_to_b64(wc, enc_format="png"),
            width="100%",
        )

def initialise_table():
    children = []
    figure, total_msgs = data_analysis.display_num_of_messages(default_df)
    children.append(
        html.Header(
            f"Your group has shared a total of {total_msgs:,} messages."
        )
    )
    children.append(dcc.Graph(figure=figure))
    return children


def initialise_chatting():
    return get_usage_plots(default_df)

def initialise_responder(df):
    fig = data_analysis.get_first_responders(df)
    return dcc.Graph(figure=fig)


def initialise_emojis():
    return get_emojis(default_df)


def initialise_media():
    return get_biggest_spammer(default_df, time_frame=".") + get_media_info(
        default_df, source="android"
    )


def initialise_quotes(df):

    images, captions = data_analysis.display_quote(df)

    return [
        html.Img(
            src=HTML_IMG_SRC_PARAMETERS + utils.pil_to_b64(images[0], enc_format="png"),
            width="100%",
        ),
        html.Caption(
            children=[
                f"Original Image by: {captions[0][0]} ",
                html.A(
                    f"({captions[0][1]}) ",
                    href=f"https://unsplash.com/{captions[0][1]}",
                    ),
                "from Unsplash"
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
        html.Img(
            src=HTML_IMG_SRC_PARAMETERS + utils.pil_to_b64(images[1], enc_format="png"),
            width="100%",
        ),
        html.Caption(
            children=[
                f"Original Image by: {captions[1][0]} ",
                html.A(
                    f"({captions[1][1]}) ",
                    href=f"https://unsplash.com/{captions[1][1]}",
                    ),
                "from Unsplash"
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
        html.Img(
            src=HTML_IMG_SRC_PARAMETERS + utils.pil_to_b64(images[2], enc_format="png"),
            width="100%",
        ),
        html.Caption(
            children=[
                f"Original Image by: {captions[2][0]} ",
                html.A(
                    f"({captions[2][1]})",
                    href=f"https://unsplash.com/{captions[2][1]}",
                    ),
                " from Unsplash"
            ],
            style={
                "display": "block",
                "margin-left": "auto",
                "margin-right": "auto",
                "width": "100%",
                "margin-bottom": "40px",
                "margin-top": "0px",
                "font-size": "10px",
            },
        ),
    ]


def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag and Drop or ", html.A("chat file")]),
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
            ),
            dcc.Store(id="original-df"),
            html.Div(id="output-data-upload", children=[]),
        ],
    )


app.layout = html.Div(
    id="app-container",
    children=[
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(), generate_control_card(), get_faq()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                html.H6("Total Number of Messages"),
                html.Hr(),
                # Overall number of messages
                dcc.Loading(id='loading-input-1', 
                children=[
                    html.Div(id="loading-output-1"),
                    html.Div(id="group-volume-data", children=initialise_table())
                ],
                type="default"),

                html.H6("Chatting Patterns"),
                html.Hr(),

                dcc.Loading(id='loading-input-2', 
                children=[
                    html.Div(id="loading-output-2"),
                    html.Div(
                    id="chatting",
                    children=[
                        html.Div(
                            id="chatting-patterns", children=initialise_chatting()
                        ),
                    ],
                )],
                type="default"),

                html.H6("First Responder"),
                html.Hr(),
                html.P("This heatmap shows what percentage of the sender's messages was first replied by each of the group members"),
                
                dcc.Loading(id='loading-input-8', 
                children=[
                    html.Div(id="loading-output-8"),
                    html.Div(
                        id="responders",
                        children=[
                            html.Div(id="responding-patterns", children=initialise_responder(default_df))
                        ]
                    )],
                type="default"),


                html.H6("Your favourite emojis"),
                html.Hr(),

                dcc.Loading(id='loading-input-3', 
                children=[
                    html.Div(id="loading-output-3"),
                    html.Div(
                        id="emojis",
                        children=[
                            html.Div(id="emoji-patterns", children=initialise_emojis())
                        ]
                    )],
                type="default"),

                html.H6("Media Sharing"),
                html.Hr(),

                dcc.Loading(id='loading-input-4', 
                children=[
                    html.Div(id="loading-output-4"),
                    html.Div(id="spams",
                    children=[
                        html.Div(id="media-patterns", children=initialise_media()),
                    ])],
                type="default"),
                
                html.H6("Word Cloud"),
                html.Hr(),
                
                dcc.Loading(id='loading-input-5', 
                children=[
                    html.Div(id="loading-output-5"),
                    html.Div(id="wordcloud",
                    children=[ 
                        html.Div(id="word-cloud", children=get_word_cloud(default_df)),
                    ])],
                type="default"),

                html.H6("Remember some of your messages"),
                html.Hr(),

                html.Div(
                    id="quotes",
                    children=[
                        html.Button(
                            "Generate New",
                            id="btn-see-media",
                            style={"margin-bottom": "20px"},
                        ),
                        dcc.Loading(
                            id='loading-input-6', 
                            children=[
                                html.Div(id="loading-output-6"),
                                html.Div(id="quotes-div", 
                                        children=initialise_quotes(default_df)
                            )
                        ], type="default")
                    ]
                )
            ]
        )
    ]
)

                        


def get_year_dropdown(years):
    return [
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
        html.P(
            "Some of you friends have changed numbers over the years. For a more accurate analysis, please specify their owners."
        )
    ]
    names = ["Ignore number"] + author_names
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


@app.callback(
    Output("output-data-upload", "children"),
    Input("original-df", "data"),
    State("output-data-upload", "children"),
    prevent_initial_call=True,
)
def parse_contents(jsonified_cleaned_data, children):
    if jsonified_cleaned_data is not None:
        blob = json.loads(jsonified_cleaned_data)
        chat_df = pd.read_json(blob["chat_df"], orient="split")
        author_names, phone_numbers = data_cleaning.get_users(chat_df)

        years = list(chat_df["year"].unique())
        if len(years) > 1 and phone_numbers:
            years.sort(reverse=True)
            years = ["All years"] + years
            return get_year_dropdown(years) + get_numbers_dropdown(
                author_names, phone_numbers
            )

        if len(years) > 1 and not phone_numbers:
            years.sort(reverse=True)
            years = ["All years"] + years
            return get_year_dropdown(years)

        return None


@app.callback(
    Output("original-df", "data"),
    Input("upload-data", "contents"),
    prevent_initial_call=True,
)
def load_data(contents):
    if contents is not None:
        content_type, content_string = contents.split(",")
        chat_df, input_source = data_cleaning.preprocess_input_data(
            base64.b64decode(content_string)
        )
        json_data = {"chat_df": chat_df.to_json(date_format="iso", orient="split")}
        json_data["input_source"] = input_source
        return json.dumps(json_data)


@app.callback(
    Output("group-volume-data", "children"),
    Output("chatting-patterns", "children"),
    Output("responding-patterns", "children"),
    Output("emoji-patterns", "children"),
    Output("media-patterns", "children"),
    Input("original-df", "data"),
    Input({"type": "filter-dropdown", "index": ALL}, "value"),
    Input({"type": "number-dropdowns", "index": ALL}, "value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True,
)
def update_total_messages(jsonified_cleaned_data, years, phone_dps):

    blob = json.loads(jsonified_cleaned_data)
    chat_df = pd.read_json(blob["chat_df"], orient="split")
    children = []
    media = []

    if phone_dps:
        _, phone_numbers = data_cleaning.get_users(chat_df)
        num_name_pairs = {
            pn: name
            for pn, name in zip(phone_numbers, phone_dps)
            if name != "Ignore number"
        }

        data_cleaning.fix_phone_numbers(chat_df, num_name_pairs)

    if years and years[0] != "All years":
        data_subset = chat_df[chat_df["year"] == years[0]]
        figure, total_msgs = data_analysis.display_num_of_messages(data_subset)
        children.append(
            html.Header(
                f"In {years[0]} your group has shared a total of {total_msgs:,} messages."
            )
        )
        children.append(dcc.Graph(figure=figure))

        usage = get_usage_plots(data_subset)
        emojis = get_emojis(data_subset)
        data_subset.reset_index(inplace=True)
        responder = dcc.Graph(figure=data_analysis.get_first_responders(data_subset))
        media = get_biggest_spammer(
            data_subset, time_frame=f" in {years[0]}."
        ) + get_media_info(data_subset, source=blob["input_source"])
    else:
        figure, total_msgs = data_analysis.display_num_of_messages(chat_df)
        children.append(
            html.Header(
                f"Your group has shared a total of {total_msgs:,} messages."
            )
        )
        children.append(dcc.Graph(figure=figure))
        if years:
            yearly_breakdown, total_msgs = data_analysis.display_num_of_messages(
                chat_df, per_year=True
            )
            children.append(dcc.Graph(figure=yearly_breakdown))

        usage = get_usage_plots(chat_df)
        emojis = get_emojis(chat_df)
        responder = dcc.Graph(figure=data_analysis.get_first_responders(chat_df))
        media = get_biggest_spammer(chat_df, time_frame=".") + get_media_info(
            chat_df, source=blob["input_source"]
        )

    return children, usage, responder, emojis, media



@app.callback(
    Output("word-cloud", "children"),
    Input("original-df", "data"),
    Input({"type": "filter-dropdown", "index": ALL}, "value"),
    prevent_initial_call=True
)
def update_word_cloud(jsonified_cleaned_data, years):

    blob = json.loads(jsonified_cleaned_data)
    chat_df = pd.read_json(blob["chat_df"], orient="split")

    if years and years[0] != "All years":
        data_subset = chat_df[chat_df["year"] == years[0]]
        return get_word_cloud(data_subset)
    else:
        return get_word_cloud(chat_df)


@app.callback(Output("loading-output-1", "children"), Input("loading-input-1", "loading_state"))
def input_triggers_spinner(value):
    time.sleep(1)
    return value

@app.callback(Output("loading-output-2", "children"), Input("loading-input-2", "loading_state"))
def input_triggers_spinner(value):
    time.sleep(1)
    return value

@app.callback(Output("loading-output-3", "children"), Input("loading-input-3", "loading_state"))
def input_triggers_spinner(value):
    time.sleep(1)
    return value

@app.callback(Output("loading-output-4", "children"), Input("loading-input-4", "loading_state"))
def input_triggers_spinner(value):
    time.sleep(1)
    return value

@app.callback(Output("loading-output-5", "children"), Input("loading-input-5", "loading_state"))
def input_triggers_spinner(value):
    time.sleep(1)
    return value

@app.callback(Output("loading-output-6", "children"), Input("loading-input-6", "loading_state"))
def input_triggers_spinner(value):
    time.sleep(1)
    return value

@app.callback(Output("loading-output-8", "children"), Input("loading-input-8", "loading_state"))
def input_triggers_spinner(value):
    time.sleep(1)
    return value

@app.callback(
    Output("quotes-div", "children"),
    Input("original-df", "data"),
    Input("btn-see-media", "n_clicks"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True,
)
def display_quotes(jsonified_cleaned_data, click):
    if jsonified_cleaned_data is None:
        return initialise_quotes(default_df)
    else:
        blob = json.loads(jsonified_cleaned_data)
        chat_df = pd.read_json(blob["chat_df"], orient="split")
        return initialise_quotes(chat_df)


@app.callback(
    Output("bt1-child", "style"),
    Output("bt2-child", "style"),
    Output("bt3-child", "style"),

    Input("fqa-b1", "n_clicks"),
    Input("fqa-b2", "n_clicks"),
    Input("fqa-b3", "n_clicks"),

    prevent_initial_call=True
)
def control_faq(btn1, btn2, btn3):

    style1 = SHOWY_CSS if btn1 % 2 == 1 else BASE_CSS
    style2 = SHOWY_CSS if btn2 % 2 == 1 else BASE_CSS
    style3 = SHOWY_CSS if btn3 % 2 == 1 else BASE_CSS

    return style1, style2, style3
    


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
