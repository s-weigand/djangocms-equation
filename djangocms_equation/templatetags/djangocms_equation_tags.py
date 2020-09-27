"""Module containing custom templatetags."""
from django import template

register = template.Library()


@register.filter(name="format_float_dot_delimiter")
def format_float_dot_delimiter(value):
    """Ensure that the float value has '.' as the decimal delimiter.

    This prevents errors caused by internationalisation where it is not wanted,
    i.e. 'de' where the decimal delimiter is ',' and not '.' .


    Parameters
    ----------
    value : float
        Arbitrary float value that should be formatted

    Returns
    -------
    str
        String representation of the float value,
        with the decimal delimiter.
    """
    return str(value)
