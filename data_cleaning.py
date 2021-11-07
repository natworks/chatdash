import re
import pandas as pd
from io import StringIO
from datetime import datetime


def preprocess_input_data(chat_file, year=2021):

    lines = StringIO(chat_file.getvalue().decode("utf-8")).readlines()[1:]

    # the sinal chat has already been formatted, does not have a date
    if re.search(r'(\d+/\d+/\d+)', lines[0]) is None:
        chat = pd.read_csv(chat_file, sep=',')
        return chat[chat['year']== year], 'signal'

    ## check if it is a normal message
    is_normal_message = None
    line_iter = iter(lines)
    line_test = ''
    while is_normal_message is None:
        line_test = next(line_iter)
        is_normal_message = re.search(r'(\d+/\d+/\d+)',line_test)

    if re.search(r'(\d+/\d+/\d+,)', line_test) is not None:
        dict_file = process_data(lines)
        input_source = 'android'
    elif re.search(r'(\d+/\d+/\d+\s(.*?)])', line_test) is not None:
        dict_file = process_data(lines, formatting='iphone')
        input_source = 'iphone'
    else:
        raise ValueError("I'm sorry, I cannot make sense of this file format. :(")

    chat = pd.DataFrame.from_dict(dict_file)

    return chat[chat['year']== str(year)], input_source


def process_data(lines, formatting='android'):
    dict_file = {"day_of_month": [], "weekday": [], "month":[], "year": [], "hour_of_day": [], "minute_of_hour": [],
                 "hour_quartile": [], "author": [], "body": []}
    
    name_pattern = '- (.*?):' if formatting=='android' else '] (.*?):'
    date_pattern = '(\d+/\d+/\d+\,(.*?)\-)' if formatting=='android' else '(\d+/\d+/\d+\s(.*?)])'
    hour_pattern = '%d/%m/%Y, %H:%M' if formatting=='android' else '%d/%m/%Y %H:%M:%S'
    
    for idx, line in enumerate(lines):
                
        line = line.strip()

        date_info = re.search(r"{}".format(date_pattern),line)
        previous_line = ""

        if date_info is not None:
            has_author = re.search(r"{}".format(name_pattern), line)
            if has_author is not None:
                date = datetime.strptime(date_info.group(1)[:-1].strip(), hour_pattern)

                dict_file['day_of_month'].append(datetime.strftime(date, '%d'))
                dict_file['weekday'].append(datetime.strftime(date, '%a'))
                dict_file['month'].append(datetime.strftime(date, '%b'))
                dict_file['year'].append(datetime.strftime(date, '%Y'))
                dict_file["hour_of_day"].append(datetime.strftime(date, '%H'))
                minute_of_hour = datetime.strftime(date, '%M')
                dict_file["minute_of_hour"].append(minute_of_hour)
                dict_file["hour_quartile"].append(int(minute_of_hour)//15)

                dict_file["author"].append(has_author.group(1).strip().encode('ascii', 'ignore').decode("utf-8"))
                
                previous_line = line[has_author.span()[1]+1:].strip()
                end_msg_block = False
                counter = idx+1
                while end_msg_block is not True and counter < len(lines)-1:
                    block = re.search(r'(\d+/\d+/\d+)',lines[counter])
                    if block is None:
                        previous_line += lines[counter].strip()
                    else:
                        end_msg_block = True
                    counter +=1
                dict_file["body"].append(previous_line)

    return dict_file


def get_users(chat_data):
    list_of_authors = list(chat_data['author'].unique())
    author_names = []
    phone_numbers = []
    for author in list_of_authors:
        is_name_numerical = re.search(r'(\+\d+)', author)
        if is_name_numerical is None:
            author_names.append(author)
        else:
            phone_numbers.append(is_name_numerical.group(1))
    return author_names, phone_numbers


def fix_phone_numbers(chat_data, num_name_pairs):

    for num, name in num_name_pairs.items():
        chat_data.loc[chat_data['author'] == num, 'author'] = name

    # return chat_data
    