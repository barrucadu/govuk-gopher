import markup.construct as m


class NoDocumentType(Exception):
    pass


class UnknownDocumentType(Exception):
    pass


class MalformedContentItem(Exception):
    pass


def parse_raw(raw):
    """Attempt to parse a raw content item.

    Throws:

    - 'NoDocumentType' if the 'document_type' field is missing

    - 'UnknownDocumentType' if the 'document_type' field is present,
      but there's no parser for that type

    - 'MalformedContentItem' if parsing fails

    Returns the parsed content item.
    """

    if 'document_type' not in raw:
        raise NoDocumentType()

    document_type = raw['document_type']
    document_type_parser = f'parse_type_{document_type}'

    if document_type_parser not in globals():
        raise UnknownDocumentType(document_type)

    try:
        return globals()[document_type_parser](raw)
    except Exception as e:
        raise MalformedContentItem(e)


def parse_type_transaction(raw):
    """Parse a transaction content item."""

    details = raw['details']

    body = []
    if 'introductory_paragraph' in details:
        body.append(m.text(details['introductory_paragraph']))
    body.append(
        m.web_link(
            details['start_button_text'],
            details['transaction_start_link']))
    if 'more_information' in details:
        body.append(m.heading('More information'))
        body.append(m.text(details['more_information']))
    if 'other_ways_to_apply' in details:
        body.append(m.heading('Other ways to apply'))
        body.append(m.text(details['other_ways_to_apply']))

    return {
        'title': raw['title'],
        'description': raw['description'],
        'updated_at': raw['public_updated_at'],
        'body': body,
    }
