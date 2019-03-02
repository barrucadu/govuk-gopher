from markup import Elem


class BadMarkup(Exception):
    pass


def usage_message(port):
    """Print a message about how to use the server, with some example
    pages.
    """

    return (
        'iWelcome to the GOV.UK-to-Gopher Service\r\n'
        'i\r\n'
        'iRequest any path to get a rendition of that page on GOV.UK as a Gopher directory listing.\r\n'
        'iFor example:\r\n'
        f'1Tax your vehicle\t/vehicle-tax\t\t{port}\r\n')


def generic_error(title, message):
    """Return a generic error 'page'.
    """

    return (
        f'i{title}\r\n'
        'i\r\n'
        f'i{message}\r\n'
    )


def bad_content_message(base_path, message):
    """Return an error message when rendering a page has gone awry.
    """

    return generic_error(
        f'Could not render "{base_path}"',
        message,
    )


def bad_request_message(request):
    """Return an error message when the request is malformed.
    """

    return generic_error(
        f'Could not understand "{request}"',
        'Requests should be paths on GOV.UK.',
    )


def wordwrap(string, colwidth=80):
    """Wrap some text by breaking lines at spaces.
    """

    if string[0:4] == '  * ':
        string = string[4:]
        islist = True
        colwidth = 76
    else:
        islist = False

    out = []
    line = ''
    for word in string.split():
        if line == '':
            line = word
            continue
        if len(line) + len(word) + 1 > colwidth:
            out.append(line)
            line = word
        else:
            line = f'{line} {word}'
    if line != '':
        out.append(line)

    if islist:
        for i in range(len(out)):
            if i == 0:
                out[i] = f'  * {out[i]}'
            else:
                out[i] = f'    {out[i]}'

    if out == []:
        out = ['']

    return out


def render(content_item):
    """Render a content item as a gopher menu.
    """

    menu = [
        f'i{content_item.title}\r\n',
        f'i{content_item.updated_at}\r\n',
        f'i\r\n',
        f'i-------------------------------------------------------------------------------\r\n',
        f'i\r\n',
    ]
    for line in wordwrap(content_item.description):
        menu.append(f'i{line}\r\n')
    menu.extend([
        f'i\r\n',
        f'i-------------------------------------------------------------------------------\r\n',
        f'i\r\n',
    ])

    for item in content_item.body:
        if item['type'] == Elem.HEADING:
            menu.append(f'i# {item["text"]}\r\n')
            menu.append('i\r\n')
        elif item['type'] == Elem.TEXT:
            for line in item['text'].split('\n'):
                for lline in wordwrap(line):
                    menu.append(f'i{lline}\r\n')
        elif item['type'] == Elem.WEB_LINK:
            menu.append('i\r\n')
            menu.append(
                f'h{item["text"]} (HTTP link)\tURL:{item["target"]}\t\t\r\n')
            menu.append('i\r\n')
        else:
            raise BadMarkup(item['type'])

    return ''.join(menu)
