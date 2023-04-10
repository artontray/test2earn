from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

"""
Function found on Slack :
https://code-institute-room.slack.com/archives/CGWQJQKC5/p1659115569168149?thread_ts=1659005118.161939&cid=CGWQJQKC5
"""


def starting_with_space_input(textfield):
    """
    Function to avoid First space character on inputs
    """
    cleaned_data = strip_tags(textfield).replace("&nbsp;", " ")
    if cleaned_data.startswith(" "):
        raise ValidationError("Field cannot begin with whitespace.")
        