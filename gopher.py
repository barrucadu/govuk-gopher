from markup import Elem


class BadMarkup(Exception):
    pass


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
        colwidth = colwidth - 4
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


def render(host, port, content_item):
    """Render a content item as a gopher menu.
    """

    return sections_to_menu(content_item_to_sections(host, port, content_item))


def content_item_to_sections(host, port, content_item):
    """Turn a content item into a list of sections.
    """

    sections = []

    sections.append([[
        f'i{content_item.title}\r\n',
        f'i{content_item.updated_at}\r\n',
    ]])

    if content_item.description != '':
        chunk = []
        for line in wordwrap(content_item.description):
            chunk.append(f'i{line}\r\n')
        sections.append([chunk])

    chunks = []
    linklist = []
    for item in content_item.body:
        if linklist != [] and item['type'] not in [Elem.LINK, Elem.WEB_LINK]:
            chunks.append(linklist)
            linklist = []

        if item['type'] == Elem.HEADING:
            chunks.append([f'i# {item["text"]}\r\n'])
        elif item['type'] == Elem.TEXT:
            chunk = []
            for line in item['text'].split('\n'):
                for lline in wordwrap(line):
                    chunk.append(f'i{lline}\r\n')
            chunks.append(chunk)
        elif item['type'] == Elem.LINK:
            linklist.append(
                f'1{item["text"]}\t{item["target"]}\t{host}\t{port}\r\n')
        elif item['type'] == Elem.WEB_LINK:
            linklist.append(
                f'h{item["text"]} (HTTP link)\tURL:{item["target"]}\t\t\r\n')
        else:
            raise BadMarkup(item['type'])
    if linklist != []:
        chunks.append(linklist)
    sections.append(chunks)

    chunks = []

    def do_links(title, links):
        render_links_as_chunk(
            title,
            links,
            host,
            port,
            chunks)

    if content_item.links.parent is not None:
        do_links('Parent', [content_item.links.parent])
    do_links('Explore this topic', content_item.links.explore)
    do_links('Related people', content_item.links.people)
    do_links('Related organisations', content_item.links.organisations)
    do_links('Related items', content_item.links.related_items)
    sections.append(chunks)

    return sections


def sections_to_menu(sections):
    """Turn a list of sections into a Gopher menu.
    """

    section_divider = [
        'i\r\n',
        'i-------------------------------------------------------------------------------\r\n',
        'i\r\n',
    ]

    chunk_divider = ['i\r\n']

    menu = []

    first_section = True
    for section in sections:
        if not first_section:
            menu.extend(section_divider)
        first_chunk = True
        for chunk in section:
            if not first_chunk:
                menu.extend(chunk_divider)
            menu.extend(chunk)
            first_chunk = False
        first_section = False

    return ''.join(menu)


def render_links_as_chunk(title, links, host, port, chunks):
    """Render some links as a chunk."""

    if links == []:
        return

    chunk = []
    for link in links:
        chunk.append(
            f'1{link.title}\t{link.base_path}\t{host}\t{port}\r\n')

    chunks.append([f'i{title}:\r\n'])
    chunks.append(chunk)
