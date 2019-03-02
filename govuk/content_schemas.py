import markup
from collections import namedtuple

ContentItem = namedtuple(
    'ContentItem', [
        'title', 'description', 'updated_at', 'body'])


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

    Returns a 'ContentItem'.
    """

    if 'document_type' not in raw:
        raise NoDocumentType()

    document_type = raw['document_type']
    document_type_parser = f'parse_details_{document_type}'

    if document_type_parser not in globals():
        raise UnknownDocumentType(document_type)

    try:
        body = globals()[document_type_parser](raw['details'])
        return ContentItem(
            title=raw['title'],
            description=raw.get('description') or '',
            updated_at=raw['public_updated_at'],
            body=body,
        )
    except Exception as e:
        raise MalformedContentItem(e)


def parse_details_transaction(details):
    """Parse a transaction content item details hash."""

    body = []

    if 'introductory_paragraph' in details:
        body.append(markup.text(details['introductory_paragraph']))

    body.append(
        markup.web_link(
            details['start_button_text'],
            details['transaction_start_link']))

    if 'more_information' in details:
        body.append(markup.heading('More information'))
        body.append(markup.text(details['more_information']))

    if 'other_ways_to_apply' in details:
        body.append(markup.heading('Other ways to apply'))
        body.append(markup.text(details['other_ways_to_apply']))

    return body


def parse_details_html_publication(details):
    """Parse an html_publication content item details hash."""

    return [markup.text(details['body'])]
