import re
import pandas as pd
from io import StringIO
from datetime import datetime

import streamlit as st

MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}
WEEKDAYS = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def preprocess_input_data(chat_file, year="2021"):

    lines = StringIO(chat_file.decode("utf-8")).readlines()[1:]

    # the sinal chat has already been formatted, does not have a date
    if re.search(r"(\d+/\d+/\d+)", lines[0]) is None:
        chat = pd.read_csv(StringIO(chat_file.decode("utf-8")), sep=",")
        return chat, "signal"

    ## check if it is a normal message
    is_normal_message = None
    line_iter = iter(lines)
    line_test = ""
    while is_normal_message is None:
        line_test = next(line_iter)
        is_normal_message = re.search(r"(\d+/\d+/\d+)", line_test)

    if re.search(r"(\d+/\d+/\d+,)", line_test) is not None:
        dict_file = process_data(lines)
        input_source = "android"
    elif re.search(r"(\d+/\d+/\d+\s(.*?)])", line_test) is not None:
        dict_file = process_data(lines, formatting="iphone")
        input_source = "iphone"
    else:
        raise ValueError("I'm sorry, I cannot make sense of this file format. :(")

    chat = pd.DataFrame.from_dict(dict_file)

    return chat, input_source  # [chat['year']== year], input_source


# @st.cache(allow_output_mutation=True)
def process_data(lines, formatting="android"):
    dict_file = {
        "day_of_month": [],
        "weekday": [],
        "month": [],
        "year": [],
        "hour_of_day": [],
        "minute_of_hour": [],
        "author": [],
        "body": [],
    }

    name_pattern = "- (.*?):" if formatting == "android" else "] (.*?):"
    date_pattern = (
        "(\d+/\d+/\d+\,(.*?)\-)" if formatting == "android" else "(\d+/\d+/\d+\s(.*?)])"
    )
    hour_pattern = "%d/%m/%Y, %H:%M" if formatting == "android" else "%d/%m/%Y %H:%M:%S"

    for line in lines:

        line = line.strip()

        date_info = re.search(r"{}".format(date_pattern), line)
        has_author = re.search(r"{}".format(name_pattern), line)

        if date_info is not None and has_author is not None:
            date = datetime.strptime(date_info.group(1)[:-1].strip(), hour_pattern)

            dict_file["day_of_month"].append(str(date.day))
            dict_file["weekday"].append(WEEKDAYS[date.weekday()])
            dict_file["month"].append(MONTHS[date.month])
            dict_file["year"].append(str(date.year))
            dict_file["hour_of_day"].append(str(date.hour))
            dict_file["minute_of_hour"].append(str(date.minute))

            dict_file["author"].append(
                has_author.group(1).strip().encode("ascii", "ignore").decode("utf-8")
            )
            dict_file["body"].append(line[has_author.span()[1] + 1 :])

        if date_info is None and has_author is None:
            dict_file["body"][-1] += " {}".format(line)

    return dict_file


def get_users(chat_data):
    list_of_authors = list(chat_data["author"].unique())
    author_names = []
    phone_numbers = []
    for author in list_of_authors:
        is_name_numerical = re.search(r"(\+\d+)", author)
        if is_name_numerical is None:
            author_names.append(author)
        else:
            phone_numbers.append(is_name_numerical.group(1))
    return author_names, phone_numbers


def fix_phone_numbers(chat_data, num_name_pairs):

    for num, name in num_name_pairs.items():
        chat_data.loc[chat_data["author"] == num, "author"] = name

    # return chat_data
