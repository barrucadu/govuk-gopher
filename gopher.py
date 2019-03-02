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


def render(content_item):
    raise Exception(content_item)
