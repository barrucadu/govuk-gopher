import html2text
import enum


class Elem(enum.Enum):
    HEADING = enum.auto()
    TEXT = enum.auto()
    WEB_LINK = enum.auto()


def heading(text):
    """Construct a section heading.
    """

    return {
        'type': Elem.HEADING,
        'text': text
    }


def text(html):
    """Parse some HTML text.
    """

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True

    lines = []
    for line in h.handle(html).split('\n'):
        # strip abbreviations, which can't be disabled...
        if line[0:4] == '  *[':
            continue
        # replace fancy quotes
        line = line.replace('‘', '\'').replace('’', '\'')
        # strip trailing whitespace
        lines.append(line.rstrip())

    return {
        'type': Elem.TEXT,
        'text': '\n'.join(lines).strip(),
    }


def web_link(text, target):
    """Construct an external link (to the web).
    """

    return {
        'type': Elem.WEB_LINK,
        'text': text,
        'target': target,
    }
