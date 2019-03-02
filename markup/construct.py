import html2text


def heading(text):
    """Construct a section heading.
    """

    return {
        'type': 'heading',
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
        # strip trailing whitespace
        lines.append(line.rstrip())

    return {
        'type': 'text',
        'text': '\n'.join(lines).strip(),
    }


def web_link(text, target):
    """Construct an external link (to the web).
    """

    return {
        'type': 'web_link',
        'text': text,
        'target': target,
    }
