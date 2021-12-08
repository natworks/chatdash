class ColnamesDf:
    DATE = "date"
    """Date column"""

    USERNAME = "username"
    """Username column"""

    MESSAGE = "message"
    """Message column"""

    MESSAGE_LENGTH = "message_length"
    """Message length column"""


COLNAMES_DF = ColnamesDf()


regex_simplifier = {
    "%Y": r"(?P<year>\d{2,4})",
    "%y": r"(?P<year>\d{2,4})",
    "%m": r"(?P<month>\d{1,2})",
    "%d": r"(?P<day>\d{1,2})",
    "%H": r"(?P<hour>\d{1,2})",
    "%I": r"(?P<hour>\d{1,2})",
    "%M": r"(?P<minutes>\d{2})",
    "%S": r"(?P<seconds>\d{2})",
    "%P": r"(?P<ampm>[AaPp].? ?[Mm].?)",
    "%p": r"(?P<ampm>[AaPp].? ?[Mm].?)",
    "%name": fr"(?P<{COLNAMES_DF.USERNAME}>[^:]*)",
}
