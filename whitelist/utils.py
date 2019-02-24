from django.conf import settings


# 3rd Party
try:
    from termcolor import cprint as _cprint, colored
except ImportError:
    def _cprint(msg, *_args, **_kwargs):
        print(msg)

    def colored(msg, *_args, **_kwargs):
        return msg


def cprint(msg, *args, **kwargs):
    if settings.DEBUG or settings.TESTING:
        _cprint(msg, *args, **kwargs)
    else:
        pass


def colored_resp_time(resp_time):
    """
    For stdout (either management commands or the dev server). Colors the
    supplied `resp_time` based on rules of speed.
    Args:
    @resp_time   int    The milliseconds it took for some request to come back.
    """
    resp_time = round(float(resp_time), 3)
    if resp_time < 200.0:
        color = 'green'
    elif resp_time < 500.0:
        color = 'yellow'
    else:
        color = 'red'

    return colored(resp_time, color=color)
