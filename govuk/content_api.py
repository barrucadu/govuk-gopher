from govuk.content_schemas import parse_raw

import requests

API_PATH = 'https://www.gov.uk/api/content'


def fetch_raw_content_item(base_path):
    """Fetch a content item from the GOV.UK content API, and don't do any
    validation or parsing beyond interpreting it as JSON.
    """

    resp = requests.get(f'{API_PATH}/{base_path}')
    return resp.json()


def fetch_content_item(base_path):
    """Fetch a content item from the GOV.UK content API, and parse the
    JSON response if it's of a known type.
    """

    raw = fetch_raw_content_item(base_path)
    return parse_raw(raw)
