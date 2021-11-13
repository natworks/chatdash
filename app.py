import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ClientsideFunction, MATCH, ALL

import dash_table
import io
import base64
import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib

import data_cleaning
import data_analysis

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "ChatDash"

server = app.server
app.config.suppress_callback_exceptions = True

def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            # html.H5("Chat Analysis"),
            html.H5("Welcome to the ChatDash"),
            html.Div(
                id="intro",
                children="Simply load an exported chat from WhastApp and we'll analyse it for you. You may see a demo on the right.",
            ),
        ],
    )



def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            # html.P("Upload chat .txt file"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('chat file')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '5px'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
            dcc.Store(id='original-df'),
            html.Div(id='output-data-upload', children=[])]
            # dcc.Dropdown(
            #     id="clinic-select",
            #     options=[{"label": i, "value": i} for i in clinic_list],
            #     value=clinic_list[0],
            # ),
            )
    #         ,



    #         dcc.Dropdown(
    #             id="clinic-select",
    #             options=[{"label": i, "value": i} for i in clinic_list],
    #             value=clinic_list[0],
    #         ),
    #         html.Br(),
    #         html.P("Select Check-In Time"),
    #         dcc.DatePickerRange(
    #             id="date-picker-select",
    #             start_date=dt(2014, 1, 1),
    #             end_date=dt(2014, 1, 15),
    #             min_date_allowed=dt(2014, 1, 1),
    #             max_date_allowed=dt(2014, 12, 31),
    #             initial_visible_month=dt(2014, 1, 1),
    #         ),
    #         html.Br(),
    #         html.Br(),
    #         html.P("Select Admit Source"),
    #         dcc.Dropdown(
    #             id="admit-select",
    #             options=[{"label": i, "value": i} for i in admit_list],
    #             value=admit_list[:],
    #             multi=True,
    #         ),
    #         html.Br(),
    #         html.Div(
    #             id="reset-btn-outer",
    #             children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
    #         ),
    #     ],
    # )


app.layout = html.Div(
    id="app-container",
    children=[
        # # Banner
        # html.Div(
        #     id="banner",
        #     className="banner",
        #     children=[html.Img(src=app.get_asset_url("plotly_logo.png"))],
        # ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(), generate_control_card()]
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
                # Patient Volume Heatmap
                html.Div(
                    id="group-volume-data",
                    children=[
                        html.B("Total Number of Messages"),
                        html.Hr(),
                        dcc.Graph(id="overall-data"),
                    ],
                ),
                # Patient Wait time by Department
                html.Div(
                    id="chatting",
                    children=[
                        html.B("Chatting Patterns"),
                        html.Hr(),
                        html.Div(id="wait_time_table") # children=initialize_table()),
                    ],
                ),
            ],
        ),
    ],
)


def get_year_dropdown(years):
    return [html.P("Please select the year you wish to analyse"),
            dcc.Dropdown(
                # id="year-select",
                id={
                    'type': 'filter-dropdown',
                    'index': 0
                },
                options=[{"label": i, "value": i} for i in years],
                value=years[0],
            )]

def get_numbers_dropdown(author_names, phone_numbers):

    box = [
        html.P("Some of you friends have changed numbers over the years. For a more accurate analysis, please specify their owners.")
    ]
    names = ['Ignore number'] +  author_names
    for number in phone_numbers:
        box.append(html.B(number))
        box.append(
            dcc.Dropdown(
                id=f"drop-{number}",
                options=[{"label": i, "value": i} for i in names],
                value=names[0],
            )
        )
    return box

@app.callback(Output('output-data-upload', 'children'),
              Input('original-df', 'data'),
              State('output-data-upload', 'children'),
              prevent_initial_call=True)
def parse_contents(jsonified_cleaned_data, children):
    if jsonified_cleaned_data is not None:
        chat_df = pd.read_json(jsonified_cleaned_data, orient='split')
        author_names, phone_numbers = data_cleaning.get_users(chat_df)
        
        years = list(chat_df['year'].unique())
        # years = [str(y) for y in years]
        if len(years) > 1 and phone_numbers:
            years.sort(reverse=True)
            years  = ['All years'] + years
            return get_year_dropdown(years) + get_numbers_dropdown(author_names, phone_numbers)

        if len(years) > 1 and not phone_numbers:
            years.sort(reverse=True)
            years  = ['All years'] + years
            return get_year_dropdown(years)
        
        return None

@app.callback(Output('original-df', 'data'),
              Input('upload-data', 'contents'), prevent_initial_call=True)
def load_data(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        chat_df, input_source = data_cleaning.preprocess_input_data(base64.b64decode(content_string))
        return chat_df.to_json(date_format='iso', orient='split')


@app.callback(Output('overall-data', 'figure'),
              Input('original-df', 'data'),
              Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
              prevent_initial_call=True,
              suppress_callback_exceptions=True)
def update_total_messages(jsonified_cleaned_data, years):
    chat_df = pd.read_json(jsonified_cleaned_data, orient='split')
    
    if years and years[0] != 'All years':
        figure = data_analysis.display_num_of_messages(chat_df[chat_df['year']==years[0]])
    else:
        figure = data_analysis.display_num_of_messages(chat_df)
    
    return figure

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)