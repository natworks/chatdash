import os
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL

import json
import time
import base64
import pathlib
import pandas as pd
from datetime import datetime

import utils
import data_cleaning
import data_analysis
import display_helpers

from dotenv import load_dotenv

load_dotenv()


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

# demo data
default_df = pd.read_csv(DATA_PATH.joinpath("random_generator_v3.txt"), parse_dates=[0])

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-115571481-2"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'UA-115571481-2');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


# main app
app.layout = html.Div(
    id="app-container",
    children=[
        html.Div(
            id="left-column",
            className="four columns",
            children=[
                display_helpers.description_card(),
                display_helpers.generate_control_card(),
                display_helpers.get_faq(),
            ]
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
                html.H6("Total Number of Messages", id="msg_header", style={}),
                html.Hr(id="msg_hr", style={}),
                # Overall number of messages
                dcc.Loading(
                    id="loading-input-1",
                    children=[
                        html.Div(id="loading-output-1"),
                        html.Div(
                            id="group-volume-data",
                            children=display_helpers.initialise_table(default_df),
                        ),
                        html.Div(
                            id="unique_days",
                            children=display_helpers.get_busiest_day(
                                default_df, "All years"
                            ),
                        ),
                    ],
                    type="default",
                ),
                html.Br(),
                html.H6("Chatting Patterns", id="chatting_patterns_header", style={}),
                html.Hr(id="chatting_patterns_hr", style={}),
                dcc.Loading(
                    id="loading-input-2",
                    children=[
                        html.Div(id="loading-output-2"),
                        html.Div(
                            id="chatting",
                            children=[
                                html.Div(
                                    id="chatting-patterns",
                                    children=display_helpers.initialise_chatting(
                                        default_df
                                    ),
                                ),
                            ],
                        ),
                    ],
                    type="default",
                ),
                html.H6("First Responder", id="responder_header", style={}),
                html.Hr(id="responder_hr", style={}),
                html.P(
                    "This heatmap shows what percentage of the sender's messages was first replied by each of the group members.",
                    id="responder_phrase",
                    style={},
                ),
                dcc.Loading(
                    id="loading-input-8",
                    children=[
                        html.Div(id="loading-output-8"),
                        html.Div(
                            id="responders",
                            children=[
                                html.Div(
                                    id="responding-patterns",
                                    children=display_helpers.initialise_responder(
                                        default_df
                                    ),
                                )
                            ],
                        ),
                    ],
                    type="default",
                ),
                html.H6("Favourite Emojis", id="emoji_header", style={}),
                html.Hr(id="emoji_hr", style={}),
                dcc.Loading(
                    id="loading-input-3",
                    children=[
                        html.Div(id="loading-output-3"),
                        html.Div(
                            id="emojis",
                            children=[
                                html.Div(
                                    id="emoji-patterns",
                                    children=display_helpers.initialise_emojis(
                                        default_df
                                    ),
                                )
                            ],
                        ),
                    ],
                    type="default",
                ),
                html.H6("Media Sharing", id="media_header", style={}),
                html.Hr(id="media_hr", style={}),
                dcc.Loading(
                    id="loading-input-4",
                    children=[
                        html.Div(id="loading-output-4"),
                        html.Div(
                            id="spams",
                            children=[
                                html.Div(
                                    id="media-patterns",
                                    children=display_helpers.initialise_media(
                                        default_df
                                    ),
                                ),
                            ],
                        ),
                    ],
                    type="default",
                ),
                html.H6("Word Cloud", id="word_cloud_header", style={}),
                html.Hr(id="word_cloud_hr", style={}),
                dcc.Loading(
                    id="loading-input-5",
                    children=[
                        html.Div(id="loading-output-5"),
                        html.Div(
                            id="wordcloud",
                            children=[
                                html.Div(
                                    id="word-cloud",
                                    children=display_helpers.get_word_cloud(default_df),
                                ),
                            ],
                        ),
                    ],
                    type="default",
                ),
                html.H6("Reliving Some of Your Messages", id="quotes_header", style={}),
                html.Hr(id="quotes_hr", style={}),
                html.Div(
                    id="quotes",
                    children=[
                        html.Button(
                            "Generate New",
                            id="btn-see-media",
                            style={"margin-bottom": "30px"},
                        ),
                        dcc.Loading(
                            id="loading-input-6",
                            children=[
                                html.Div(id="loading-output-6"),
                                html.Div(
                                    id="quotes-div",
                                    children=display_helpers.initialise_quotes(
                                        default_df
                                    ),
                                ),
                            ],
                            type="default",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id="footer",
            className="footer",
            children=html.P(
                children=[
                    f"\N{COPYRIGHT SIGN}{datetime.now().year} - ",
                    html.A("natworks", href="https://github.com/natworks"),
                ]
            ),
        ),
    ],
)


@app.callback(
    Output("output-data-upload", "children"),
    Input("original-df", "data"),
    State("output-data-upload", "children"),
    prevent_initial_call=True,
)
def parse_contents(jsonified_cleaned_data, children):
    if jsonified_cleaned_data is not None:
        blob = json.loads(jsonified_cleaned_data)

        if blob["chat_df"] == "FAIL":
            return None

        chat_df = pd.read_json(blob["chat_df"], orient="split")

        author_names, phone_numbers = data_cleaning.get_users(chat_df)

        years = list(chat_df["year"].unique())
        if len(years) > 1 and phone_numbers:
            years.sort(reverse=True)
            years = ["All years"] + years
            return display_helpers.get_year_dropdown(
                years
            ) + display_helpers.get_numbers_dropdown(author_names, phone_numbers)

        if len(years) > 1 and not phone_numbers:
            years.sort(reverse=True)
            years = ["All years"] + years
            return display_helpers.get_year_dropdown(years)

        return None


@app.callback(
    Output("original-df", "data"),
    Input("upload-data", "contents"),
    prevent_initial_call=True,
)
def load_data(contents):
    if contents is not None:
        
        try:
            content_type, content_string = contents.split(",")
        except:
            return json.dumps({"chat_df": "FAIL", "input_source": "FAIL"})

        chat_df, input_source = data_cleaning.preprocess_input_data(
            base64.b64decode(content_string)
        )
        
        if chat_df is None or input_source is None:
            json_data = {"chat_df": "FAIL", "input_source": "FAIL"}
        else:
            json_data = {"chat_df": chat_df.to_json(date_format="iso", orient="split")}
            json_data["input_source"] = input_source

        return json.dumps(json_data)


@app.callback(
    Output("msg_header", "style"),
    Output("msg_hr", "style"),
    Output("chatting_patterns_header", "style"),
    Output("chatting_patterns_hr", "style"),
    Output("responder_header", "style"),
    Output("responder_hr", "style"),
    Output("responder_phrase", "style"),
    Output("emoji_header", "style"),
    Output("emoji_hr", "style"),
    Output("media_header", "style"),
    Output("media_hr", "style"),
    Output("word_cloud_header", "style"),
    Output("word_cloud_hr", "style"),
    Output("quotes_header", "style"),
    Output("quotes_hr", "style"),
    Output("btn-see-media", "style"),
    Input("original-df", "data"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True,
)
def handle_incorrect_input(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return display_helpers.initialise_table(default_df)
    else:
        blob = json.loads(jsonified_cleaned_data)

        if blob["chat_df"] == "FAIL":
            return (
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
            )
        else:
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                {"margin-bottom": "30px"}
            )


@app.callback(
    Output("group-volume-data", "children"),
    Input("original-df", "data"),
    Input({"type": "filter-dropdown", "index": ALL}, "value"),
    Input({"type": "number-dropdowns", "index": ALL}, "value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True,
)
def update_messages(jsonified_cleaned_data, years, phone_dps):
    if jsonified_cleaned_data is None:
        return display_helpers.initialise_table(default_df)
    else:
        blob = json.loads(jsonified_cleaned_data)

        if blob["chat_df"] == "FAIL":
            return display_helpers.get_data_loading_error_message()

        chat_df = pd.read_json(blob["chat_df"], orient="split")

        if phone_dps:
            data_cleaning.fix_phone_numbers(chat_df, phone_dps)

        children = []

        if years and years[0] != "All years":
            data_subset = chat_df[chat_df["year"] == years[0]]
            figure, total_msgs = data_analysis.display_num_of_messages(
                data_subset, plot_title=f"Total Number of Messages in {years[0]}"
            )
            children.append(
                html.P(
                    [
                        "Your group has shared a total of ",
                        html.Span(
                            f"{total_msgs:,} messages",
                            style={"font-size": "18px", "font-weight": "bold"},
                        ),
                        f" in {years[0]}.",
                    ]
                )
            )
            children.append(dcc.Graph(figure=figure))
        else:
            figure, total_msgs = data_analysis.display_num_of_messages(
                chat_df, plot_title=f"Total Number of Messages"
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
            if years:
                author_names = list(chat_df["author"].unique())
                yearly_breakdown, total_msgs = data_analysis.get_frequency_info(
                    chat_df,
                    "year",
                    "Year",
                    list(chat_df["year"].unique()),
                    author_names,
                    plot_title="Total Number of Messager Per Year and Per User",
                )
                children.append(dcc.Graph(figure=yearly_breakdown))

        return children


@app.callback(
    Output("unique_days", "children"),
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

    if blob["chat_df"] == "FAIL":
        return None, None, None, None, None

    chat_df = pd.read_json(blob["chat_df"], orient="split")
    media = []

    if phone_dps:
        data_cleaning.fix_phone_numbers(chat_df, phone_dps)

    if years and years[0] != "All years":
        data_subset = chat_df[chat_df["year"] == years[0]]
        usage = display_helpers.get_usage_plots(data_subset, years[0])
        emojis = display_helpers.get_emojis(data_subset)
        data_subset.reset_index(inplace=True)
        unique_days = display_helpers.get_busiest_day(data_subset, years[0])
        responder = dcc.Graph(figure=data_analysis.get_first_responders(data_subset))
        media = display_helpers.get_biggest_spammer(
            data_subset, time_frame=[f"In {years[0]}, ", "was", ""]
        ) + display_helpers.get_media_info(data_subset, source=blob["input_source"])
    else:
        usage = display_helpers.get_usage_plots(chat_df)
        unique_days = display_helpers.get_busiest_day(chat_df, "All years")
        emojis = display_helpers.get_emojis(chat_df)
        responder = dcc.Graph(figure=data_analysis.get_first_responders(chat_df))
        media = display_helpers.get_biggest_spammer(
            chat_df
        ) + display_helpers.get_media_info(chat_df, source=blob["input_source"])

    return unique_days, usage, responder, emojis, media


@app.callback(
    Output("word-cloud", "children"),
    Input("original-df", "data"),
    Input({"type": "filter-dropdown", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def update_word_cloud(jsonified_cleaned_data, years):

    blob = json.loads(jsonified_cleaned_data)

    if blob["chat_df"] == "FAIL":
        return None

    chat_df = pd.read_json(blob["chat_df"], orient="split")

    if years and years[0] != "All years":
        data_subset = chat_df[chat_df["year"] == years[0]]
        return display_helpers.get_word_cloud(data_subset)
    else:
        return display_helpers.get_word_cloud(chat_df)


@app.callback(
    Output("quotes-div", "children"),
    Input("original-df", "data"),
    Input("btn-see-media", "n_clicks"),
    Input({"type": "number-dropdowns", "index": ALL}, "value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True,
)
def display_quotes(jsonified_cleaned_data, click, phone_dps):

    if jsonified_cleaned_data is None:
        return display_helpers.initialise_quotes(default_df)
    else:
        blob = json.loads(jsonified_cleaned_data)

        if blob["chat_df"] == "FAIL":
            return None

        chat_df = pd.read_json(blob["chat_df"], orient="split")

        if phone_dps:
            data_cleaning.fix_phone_numbers(chat_df, phone_dps)

        return display_helpers.initialise_quotes(chat_df)


# --------- Display Loading Icons ---------#


@app.callback(
    Output("loading-output-1", "children"), Input("loading-input-1", "loading_state")
)
def input_triggers_spinner(value):
    time.sleep(1)
    return value


@app.callback(
    Output("loading-output-2", "children"), Input("loading-input-2", "loading_state")
)
def input_triggers_spinner(value):
    time.sleep(1)
    return value


@app.callback(
    Output("loading-output-3", "children"), Input("loading-input-3", "loading_state")
)
def input_triggers_spinner(value):
    time.sleep(1)
    return value


@app.callback(
    Output("loading-output-4", "children"), Input("loading-input-4", "loading_state")
)
def input_triggers_spinner(value):
    time.sleep(1)
    return value


@app.callback(
    Output("loading-output-5", "children"), Input("loading-input-5", "loading_state")
)
def input_triggers_spinner(value):
    time.sleep(1)
    return value


@app.callback(
    Output("loading-output-6", "children"), Input("loading-input-6", "loading_state")
)
def input_triggers_spinner(value):
    time.sleep(1)
    return value


@app.callback(
    Output("loading-output-8", "children"), Input("loading-input-8", "loading_state")
)
def input_triggers_spinner(value):
    time.sleep(1)
    return value


# --------- Handle FAQ Interaction ---------#


@app.callback(
    Output("bt1-child", "style"),
    Output("bt2-child", "style"),
    Output("bt3-child", "style"),
    Output("bt4-child", "style"),
    Output("bt5-child", "style"),
    Input("fqa-b1", "n_clicks"),
    Input("fqa-b2", "n_clicks"),
    Input("fqa-b3", "n_clicks"),
    Input("fqa-b4", "n_clicks"),
    Input("fqa-b5", "n_clicks"),
    prevent_initial_call=True,
)
def control_faq(btn1, btn2, btn3, btn4, btn5):

    style1 = utils.SHOWY_CSS if btn1 % 2 == 1 else utils.BASE_CSS
    style2 = utils.SHOWY_CSS if btn2 % 2 == 1 else utils.BASE_CSS
    style3 = utils.SHOWY_CSS if btn3 % 2 == 1 else utils.BASE_CSS
    style4 = utils.SHOWY_CSS if btn4 % 2 == 1 else utils.BASE_CSS
    style5 = utils.SHOWY_CSS if btn5 % 2 == 1 else utils.BASE_CSS

    return style1, style2, style3, style4, style5


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
