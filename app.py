import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL

import json
import time
import base64
import pandas as pd
from io import BytesIO as _BytesIO


import data_cleaning
import data_analysis

# Variables
HTML_IMG_SRC_PARAMETERS = 'data:image/png;base64, '

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
            )

app.layout = html.Div(
    id="app-container",
    children=[
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
                html.H6("Total Number of Messages"),
                html.Hr(),
                # Overall number of messages
                html.Div(
                    id="group-volume-data", 
                ),
                # Chatting behaviour w.r.t. time
                html.Div(
                    id="chatting",
                    children=[
                        html.H6("Chatting Patterns"),
                        html.Hr(),
                        html.Div(id="chatting-patterns"),
                    ],
                ),
                html.Div(
                    id="spams",
                    children=[
                        html.H6("Media Sharing"),
                        html.Hr(),
                        html.Div(id="media-patterns"),
                    ],
                ),
                html.Div(
                    id="quotes",
                    children=[
                        html.H6("Remember some of your messages"),
                        html.Hr(),
                        html.Button("Generate New", id="btn-see-media", style={"margin-bottom":"20px"}),
                        html.Div(id="quotes-div"),
                    ],
                )
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
    for dp_n, number in enumerate(phone_numbers):
        box.append(html.B(f'Phone {number} belongs to:'))
        box.append(
            dcc.Dropdown(
                id={
                    'type': 'number-dropdowns',
                    'index': dp_n
                },
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
        blob = json.loads(jsonified_cleaned_data)
        chat_df = pd.read_json(blob['chat_df'], orient='split')
        author_names, phone_numbers = data_cleaning.get_users(chat_df)
        
        years = list(chat_df['year'].unique())
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
        json_data = {'chat_df': chat_df.to_json(date_format='iso', orient='split')}
        json_data['input_source'] = input_source
        return json.dumps(json_data)


def get_usage_plots(chat_df):
    author_names = list(chat_df['author'].unique())

    month_chart, top_month  = data_analysis.get_frequency_info(chat_df, 'month', 'Month', data_analysis.MONTHS, author_names)
    day_chart, top_day = data_analysis.get_frequency_info(chat_df, 'weekday', 'Weekday', data_analysis.WEEKDAYS, author_names)
    hour_chart, top_hour = data_analysis.get_frequency_info(chat_df, 'hour_of_day', 'Hour of Day', data_analysis.HOURS, author_names)


    return [
        html.Header(f'{top_month} is the busiest month of the year'),
        dcc.Graph(figure=month_chart),
        html.Header(f'{top_day} is the busiest day of the week'),
        dcc.Graph(figure=day_chart),
        html.Header(f'{top_hour}:00hr is when the chat is most alive.'),
        dcc.Graph(figure=hour_chart)
    ]

def get_emojis(chat_df):
    top_emojis = data_analysis.display_favourite_emojis(chat_df)
    as_str = '                   '.join(em for em in top_emojis)
    return [
        html.Header("Your group's favourite emojis:"),
        html.H1(as_str, style={'width': '100%','text-align': 'center', 'font-size': '72px'})
    ]

def get_biggest_spammer(chat_df, time_frame=''):
    spammer, favourite_source, source_quantity = data_analysis.display_biggest_spammer(chat_df)
    return [
        html.Header(f'{spammer} is the biggest spammer in your group. \
            Their favourite source is {favourite_source}. In fact, they have shared this website alone {source_quantity} times{time_frame}'),
        # html.Img(src="./imgs/awkward.png"),
        html.Img(src=app.get_asset_url('imgs/awkward_copy.png'), style={
            'display': 'block',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'width': '50%'
        }),
        html.Caption('awkward..', style={
            'display': 'block',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'width': '50%'
        })
    ]

def get_media_info(chat_df, source):
    gif_person, fig_gif, audio_person, fig_audio = data_analysis.display_media_person(chat_df, source)
    if fig_audio:
        return [
            html.Header(f'Sharing gifs is a skill that {gif_person} has certaily mastered.'),
            dcc.Graph(figure=fig_gif),
            html.Header(f'{audio_person} is almost a podcast host considering their audios stats. Don\'t forget to like and subscribe!'),
            dcc.Graph(figure=fig_audio),
        ]
    else:
        return [
            html.Header(f'{gif_person} is just sitting there sharing audios and gifs. They have sent a whopping {audio_person} messages containing media this year.'),
            dcc.Graph(figure=fig_gif),
        ]

@app.callback(Output('group-volume-data', 'children'),
              Output('chatting-patterns', 'children'),
              Output('media-patterns', 'children'),
              Input('original-df', 'data'),
              Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
              Input({'type': 'number-dropdowns', 'index': ALL}, 'value'),
              prevent_initial_call=True,
              suppress_callback_exceptions=True)
def update_total_messages(jsonified_cleaned_data, years, phone_dps):
    
    
    blob = json.loads(jsonified_cleaned_data)
    chat_df = pd.read_json(blob['chat_df'], orient='split')
    children=[]
    media = []

    if phone_dps:
        _, phone_numbers = data_cleaning.get_users(chat_df)
        num_name_pairs = {pn: name for pn, name in zip(phone_numbers, phone_dps) if name != 'Ignore number'}
        
        data_cleaning.fix_phone_numbers(chat_df, num_name_pairs)
    
    if years and years[0] != 'All years':
        data_subset = chat_df[chat_df['year']==years[0]]
        figure, total_msgs = data_analysis.display_num_of_messages(data_subset)
        children.append(html.Header(f'In {years[0]} your group shared a total of {total_msgs:,} messages.'))
        children.append(dcc.Graph(figure=figure))

        usage = get_usage_plots(data_subset)
        media = get_emojis(data_subset) + get_biggest_spammer(data_subset, time_frame=f' in {years[0]}.') + get_media_info(data_subset, source=blob['input_source'])
    else:
        figure, total_msgs = data_analysis.display_num_of_messages(chat_df)
        children.append(html.Header(f'Since inception, your group shared a total of {total_msgs:,} messages.'))
        children.append(dcc.Graph(figure=figure))
        if years:
            yearly_breakdown, total_msgs = data_analysis.display_num_of_messages(chat_df, per_year=True)
            children.append(dcc.Graph(figure=yearly_breakdown))

        usage = get_usage_plots(chat_df)
        media = get_emojis(chat_df) + get_biggest_spammer(chat_df, time_frame='.') + get_media_info(chat_df, source=blob['input_source'])
    
    return children, usage, media


# Image utility functions
def pil_to_b64(im, enc_format='png', verbose=False, **kwargs):
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

    t_end = time.time()
    if verbose:
        print(f"PIL converted to b64 in {t_end - t_start:.3f} sec")

    return encoded


@app.callback(Output('quotes-div', 'children'),
              Input('original-df', 'data'),
              Input('btn-see-media', 'n_clicks'),
              prevent_initial_call=True,
              suppress_callback_exceptions=True)
def display_quotes(jsonified_cleaned_data, click):
    blob = json.loads(jsonified_cleaned_data)
    chat_df = pd.read_json(blob['chat_df'], orient='split')
    images = data_analysis.display_quote(chat_df)

    return [html.Img(
        src=HTML_IMG_SRC_PARAMETERS + pil_to_b64(images[0], enc_format='png'),
        width='100%',
        style={"margin-bottom":"10px"}
    ),
    html.Img(
        src=HTML_IMG_SRC_PARAMETERS + pil_to_b64(images[1], enc_format='png'),
        width='100%',
        style={"margin-bottom":"10px"}
    ),
    html.Img(
        src=HTML_IMG_SRC_PARAMETERS + pil_to_b64(images[2], enc_format='png'),
        width='100%',
        style={"margin-bottom":"40px"}
    )
    ]
    
# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)