from django.core.exceptions import ValidationError
from django.utils.html import strip_tags




def starting_with_space_input(textfield):
    """
    Function to avoid First space character on inputs
    """
    cleaned_data = strip_tags(textfield).replace("&nbsp;", " ")
    if cleaned_data.startswith(" "):
        raise ValidationError("Field cannot begin with whitespace.")
        