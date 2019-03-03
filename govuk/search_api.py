import requests

API_PATH = 'https://www.gov.uk/api/search.json'


def fetch_raw_search_results(query):
    """Query the GOV.UK search API, and don't do any validation or parsing
    beyond interpreting it as JSON.
    """

    payload = {f'filter_{field}': value for (field, value) in query.items()}

    resp = requests.get(f'{API_PATH}', params=payload)
    return resp.json()
