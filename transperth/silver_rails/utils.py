import re

PARAM_RE = re.compile(r":((?!/).+?)\b")


def prepare_url(url, params):
    return PARAM_RE.sub(
        lambda param: params.get(param.groups()[0], ''),
        url
    )
