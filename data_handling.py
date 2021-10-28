import re
import pandas as pd
from io import StringIO
from datetime import datetime


def preprocess_input_data(chat_file):

    lines = StringIO(chat_file.getvalue().decode("utf-8")).readlines()

    ## check if it is a normal message
    is_normal_message = None
    line_iter = iter(lines)
    line_test = ''
    while is_normal_message is None:
        line_test = next(line_iter)
        is_normal_message = re.search(r'(\d+/\d+/\d+)',line_test)

    if re.search(r'(\d+/\d+/\d+,)', line_test) is not None:
        dict_file = process_data(lines)
    elif re.search(r'(\d+/\d+/\d+\s(.*?)])', line_test) is not None:
        dict_file = process_data(lines, formatting='iphone')
    else:
        raise ValueError("I'm sorry, I cannot make sense of this file format. :(")

    return pd.DataFrame.from_dict(dict_file)



def process_data(lines, formatting='android'):
    dict_file = {"weekday": [], "month":[], "year": [], "hour_of_day": [], "minute_of_hour": [],
                 "hour_quartile": [], "author": [], "body": []}
    
    name_pattern = '- (.*?):' if formatting=='android' else '] (.*?):'
    date_pattern = '(\d+/\d+/\d+,)' if formatting=='android' else '(\d+/\d+/\d+\s(.*?)])'
    hour_pattern = '%d/%m/%Y, %H:%M' if formatting=='android' else '%d/%m/%Y %H:%M:%S'
    offset = 1 if formatting=='android' else 0
    
    for idx, line in enumerate(lines):
                
        line = line.strip()

        date_info = re.search(r"{}".format(date_pattern),line)
        previous_line = ""

        if date_info is not None:
            has_author = re.search(r"{}".format(name_pattern), line)
            if has_author is not None:
                date = datetime.strptime(date_info.group(1)[:-1], hour_pattern)

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