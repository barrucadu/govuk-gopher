import requests

API_PATH = 'https://www.gov.uk/api/search.json'


def fetch_raw_search_results(query, count=25):
    """Query the GOV.UK search API, and don't do any validation or parsing
    beyond interpreting it as JSON.
    """

    payload = {f'filter_{field}': value for (field, value) in query.items()}
    payload['count'] = count

    resp = requests.get(f'{API_PATH}', params=payload)
    return resp.json()
