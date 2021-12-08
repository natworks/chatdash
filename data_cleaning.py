import re
import pandas as pd
from io import StringIO

from parser import file_converter
import utils


def preprocess_input_data(chat_file):

    try:
        chat = pd.read_csv(
            StringIO(chat_file.decode("utf-8")), sep=",", parse_dates=[0]
        )
        return chat, "signal"
    except:
        og_df = file_converter.convert_text_to_df(
            StringIO(chat_file.decode("utf-8")).read()
        )
        chat = process_input(og_df.iloc[1:])
        return chat, "whatsapp"


def process_input(chat_data: pd.DataFrame):

    (
        chat_data["day_of_month"],
        chat_data["weekday"],
        chat_data["month"],
        chat_data["year"],
        chat_data["hour_of_day"],
    ) = zip(*chat_data["date"].map(seprate_date))

    chat_data.rename(
        columns={"date": "datetime", "username": "author", "message": "body"},
        inplace=True,
    )
    return chat_data


def seprate_date(tstamp):
    return (
        str(tstamp.day),
        utils.WEEKDAYS[tstamp.weekday()],
        utils.MONTHS[tstamp.month - 1],
        str(tstamp.year),
        str(tstamp.hour),
    )


def get_users(chat_data):
    list_of_authors = list(chat_data["author"].unique())
    author_names = []
    phone_numbers = []
    for author in list_of_authors:
        is_name_numerical = re.search(r"(\+\d+)", author)
        if is_name_numerical is None:
            author_names.append(author)
        else:
            phone_numbers.append(author)
    return author_names, phone_numbers


def fix_phone_numbers(chat_data, num_name_pairs):

    for num, name in num_name_pairs.items():
        chat_data.loc[chat_data["author"] == num, "author"] = name
