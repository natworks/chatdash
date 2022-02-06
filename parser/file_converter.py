import re
import pandas as pd
from datetime import datetime

from . import header_extractor

from . import parser_utils

"""
The code found here has been copied/modified from:
https://github.com/lucasrodes/whatstk/blob/main/whatstk/whatsapp/parser.py
"""


def convert_text_to_df(chat_info_as_text):

    header_information = header_extractor.extract_header_from_text(chat_info_as_text)
    
    if header_information is None:
        return None

    hformat, dates_codes= header_information[0], header_information[1]
   
    try:
        # Generate regex for given hformat
        r, r_x = generate_regex(hformat=hformat)
        # Parse chat to DataFrame
        df = _parse_chat(chat_info_as_text, r)
    except:
        day_pos = dates_codes.index("%d")
        year_pos = dates_codes.index("%y")
        month_pos = dates_codes.index("%m")

        if (day_pos < year_pos < month_pos) or (month_pos < year_pos < day_pos):
            hformat = hformat.replace("%y", "tmonth").replace("%m", "%y").replace("tmonth", "%m")

        r, r_x = generate_regex(hformat=hformat)
        df = _parse_chat(chat_info_as_text, r)

    # try again with a different date order

    df = _remove_alerts_from_df(r_x, df)
    df = _add_schema(df)
    
    return df


def generate_regex(hformat):
    r"""Generate regular expression from hformat.
    Args:
        hformat (str): Simplified syntax for the header, e.g. ``'%y-%m-%d, %H:%M:%S - %name:'``.
    Returns:
        str: Regular expression corresponding to the specified syntax.
    Example:
        Generate regular expression corresponding to ``'hformat=%y-%m-%d, %H:%M:%S - %name:'``.
        ..  code-block:: python
            >>> from whatstk.whatsapp.parser import generate_regex
            >>> generate_regex('%y-%m-%d, %H:%M:%S - %name:')
            ('(?P<year>\\d{2,4})-(?P<month>\\d{1,2})-(?P<day>\\d{1,2}), (?P<hour>\\d{1,2}):(?P<minutes>\\d{2}):(?
            P<seconds>\\d{2}) - (?P<username>[^:]*): ', '(?P<year>\\d{2,4})-(?P<month>\\d{1,2})-(?P<day>\\d{1,2}), (?
            P<hour>\\d{1,2}):(?P<minutes>\\d{2}):(?P<seconds>\\d{2}) - ')
    """
    items = re.findall(r"\%\w*", hformat)
    for i in items:
        hformat = hformat.replace(i, parser_utils.regex_simplifier[i])

    hformat = hformat + " "
    hformat_x = hformat.split("(?P<username>[^:]*)")[0]
    return hformat, hformat_x


def _parse_chat(text, regex):
    """Parse chat using given regex.
    Args:
        text (str) Whole log chat text.
        regex (str): Regular expression
    Returns:
        pandas.DataFrame: DataFrame with messages sent by users, index is the date the messages was sent.
    Raises:
        RegexError: When provided regex could not match the text.
    """
    result = []
    headers = list(re.finditer(regex, text))
    for i in range(len(headers)):
        try:
            line_dict = _parse_line(text, headers, i)
        except KeyError:
            pass
        result.append(line_dict)
    df_chat = pd.DataFrame.from_records(result)
    df_chat = df_chat[
        [
            parser_utils.COLNAMES_DF.DATE,
            parser_utils.COLNAMES_DF.USERNAME,
            parser_utils.COLNAMES_DF.MESSAGE,
        ]
    ]
    return df_chat


def _remove_alerts_from_df(r_x, df):
    """Try to get rid of alert/notification messages.
    Args:
        r_x (str): Regular expression to detect whatsapp warnings.
        df (pandas.DataFrame): DataFrame with all interventions.
    Returns:
        pandas.DataFrame: Fixed version of input dataframe.
    """
    df_new = df.copy()
    df_new.loc[:, parser_utils.COLNAMES_DF.MESSAGE] = df_new[
        parser_utils.COLNAMES_DF.MESSAGE
    ].apply(lambda x: _remove_alerts_from_line(r_x, x))
    return df_new


def _add_schema(df):
    """Add default chat schema to df.
    Args:
        df (pandas.DataFrame): Chat dataframe.
    Returns:
        pandas.DataFrame: Chat dataframe with correct dtypes.
    """
    df = df.astype(
        {
            parser_utils.COLNAMES_DF.DATE: "datetime64[ns]",
            parser_utils.COLNAMES_DF.USERNAME: pd.StringDtype(),
            parser_utils.COLNAMES_DF.MESSAGE: pd.StringDtype(),
        }
    )
    return df


def _parse_line(text, headers, i):
    """Get date, username and message from the i:th intervention.
    Args:
        text (str): Whole log chat text.
        headers (list): All headers.
        i (int): Index denoting the message number.
    Returns:
        dict: i:th date, username and message.
    """
    result_ = headers[i].groupdict()
    if "ampm" in result_:
        hour = int(result_["hour"])
        mode = result_.get("ampm").lower()
        if hour == 12 and mode == "am":
            hour = 0
        elif hour != 12 and mode == "pm":
            hour += 12
    else:
        hour = int(result_["hour"])

    # Check format of year. If year is 2-digit represented we add 2000
    if len(result_["year"]) == 2:
        year = int(result_["year"]) + 2000
    else:
        year = int(result_["year"])

    if "seconds" not in result_:
        date = datetime(
            year,
            int(result_["month"]),
            int(result_["day"]),
            hour,
            int(result_["minutes"]),
        )
    else:
        date = datetime(
            year,
            int(result_["month"]),
            int(result_["day"]),
            hour,
            int(result_["minutes"]),
            int(result_["seconds"]),
        )
    username = result_[parser_utils.COLNAMES_DF.USERNAME]
    message = _get_message(text, headers, i)
    line_dict = {
        parser_utils.COLNAMES_DF.DATE: date,
        parser_utils.COLNAMES_DF.USERNAME: username,
        parser_utils.COLNAMES_DF.MESSAGE: message,
    }
    return line_dict


def _remove_alerts_from_line(r_x, line_df):
    """Remove line content that is not desirable (automatic alerts etc.).
    Args:
        r_x (str): Regula expression to detect WhatsApp warnings.
        line_df (str): Message sent as string.
    Returns:
        str: Cleaned message string.
    """
    if re.search(r_x, line_df):
        return line_df[: re.search(r_x, line_df).start()]
    else:
        return line_df


def _get_message(text, headers, i):
    """Get i:th message from text.
    Args:
        text (str): Whole log chat text.
        headers (list): All headers.
        i (int): Index denoting the message number.
    Returns:
        str: i:th message.
    """
    msg_start = headers[i].end()
    msg_end = headers[i + 1].start() if i < len(headers) - 1 else headers[i].endpos
    msg = text[msg_start:msg_end].strip()
    return msg
