import markup
from collections import namedtuple

ContentItem = namedtuple(
    'ContentItem', [
        'title', 'description', 'updated_at', 'body', 'links'])

Links = namedtuple('Links',
                   ['parent',
                    'explore',
                    'people',
                    'organisations',
                    'related_items'])

Link = namedtuple('Link', ['title', 'base_path'])


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
        details = raw.get('details') or {}
        links = raw.get('links') or {}
        body = globals()[document_type_parser](details, links)
        return ContentItem(
            title=raw['title'],
            description=raw.get('description') or '',
            updated_at=raw['public_updated_at'],
            body=body,
            links=parse_links(links)
        )
    except Exception as e:
        raise MalformedContentItem(e)


def parse_links(links):
    """Parse a links hash.  Only some of the links are included."""

    def go(links, out_links, all_links):
        for link in links:
            it = Link(
                title=link['title'],
                base_path=link['base_path'],
            )
            if it.base_path in all_links:
                continue
            out_links.append(it)
            all_links.append(it.base_path)

    all_links = []

    raw_parents = links.get('parent') or []
    if raw_parents == []:
        parent = None
    else:
        parent = []
        go([raw_parents[0]], parent, all_links)
        parent = parent[0]

    explore = []
    go(links.get('taxons') or [], explore, all_links)
    go(links.get('mainstream_browse_pages') or [], explore, all_links)

    people = []
    go(links.get('ministers') or [], people, all_links)
    go(links.get('people') or [], people, all_links)

    organisations = []
    go(links.get('organisations') or [], organisations, all_links)
    go(links.get('ordered_child_organisations') or [], organisations, all_links)
    go(links.get('ordered_high_profile_groups') or [], organisations, all_links)

    related = []
    go(links.get('ordered_related_items') or [], related, all_links)
    go(links.get('suggested_ordered_related_items') or [], related, all_links)

    return Links(
        parent=parent,
        explore=explore,
        people=people,
        organisations=organisations,
        related_items=related,
    )


def parse_details_transaction(details, _links):
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


def parse_details_html_publication(details, _links):
    """Parse an html_publication content item details hash."""

    return [markup.text(details['body'])]


def parse_details_answer(details, _links):
    """Parse an answer content item details hash."""

    return [markup.text(details['body'])]


def parse_details_news_story(details, _links):
    """Parse a news_story content item details hash."""

    return [markup.text(details['body'])]


def parse_details_guide(details, _links):
    """Parse a guide content item details hash."""

    body = []

    for part in details['parts']:
        body.append(markup.heading(part['title']))
        body.append(markup.text(part['body']))

    return body


def parse_details_organisation(details, _links):
    """Parse an organisation content item details hash."""

    body = []

    body.append(markup.text(details['body']))

    if details.get('foi_exempt'):
        body.append(markup.text(
            'This organisation is EXEMPT from freedom-of-information requests.'))

    info_pages = []
    for page in details.get('ordered_corporate_information_pages') or []:
        if page['href'][0] == '/':
            if '?' in page['href']:
                continue
            else:
                info_pages.append(markup.link(page['title'], page['href']))
        else:
            info_pages.append(markup.web_link(page['title'], page['href']))
    if info_pages != []:
        body.append(markup.heading('Information pages'))
        body.extend(info_pages)

    featured_documents = details.get('ordered_featured_documents') or []
    if featured_documents != []:
        body.append(markup.heading('Featured documents'))
        for page in featured_documents:
            body.append(markup.link(page['title'], page['href']))

    for (
        key,
        heading) in [
        ('ordered_ministers',
         'Ministers'),
        ('ordered_board_members',
         'Board members'),
        ('ordered_military_personnel',
         'Military personnel'),
        ('ordered_traffic_commissioners',
         'Traffic commissioners'),
        ('ordered_chief_professional_officers',
         'Chief professional officers'),
        ('ordered_special_representatives',
         'Special representatives')]:
        people = details.get(key) or []
        if people != []:
            body.append(markup.heading(heading))
            for person in people:
                prefix = person.get('name_prefix')
                if prefix:
                    name = f'{prefix} {person["name"]}'
                else:
                    name = person['name']
                href = person.get('role_href') or person['href']
                body.append(markup.link(f'{name}, {person["role"]}', href))

    return body


def parse_details_mainstream_browse_page(details, links):
    """Parse a mainstream_browse_page content item details hash.

    Retrieves page titles from the links hash.
    """

    body = []

    empty = True

    all_links = []
    all_links.extend(links.get('children') or [])
    all_links.extend(links.get('second_level_browse_pages') or [])
    all_links.extend(links.get('top_level_browse_pages') or [])

    all_links_by_base_path = {link['base_path']: link for link in all_links}
    all_links_by_content_id = {link['content_id']: link for link in all_links}

    for group in details.get('groups') or []:
        group_links = []
        for base_path in group['contents']:
            link = all_links_by_base_path.get(base_path)
            if link:
                group_links.append(
                    markup.link(
                        link['title'],
                        link['base_path']))
        if group_links != []:
            body.append(markup.heading(group['name']))
            body.extend(group_links)
            empty = False

    second_level_browse_pages = []
    for content_id in details.get('ordered_second_level_browse_pages') or []:
        link = all_links_by_content_id.get(content_id)
        if link:
            second_level_browse_pages.append(
                markup.link(link['title'], link['base_path']))
    if second_level_browse_pages != []:
        if not empty:
            body.append(markup.heading('Subtopics'))
        body.extend(second_level_browse_pages)
        empty = False

    if empty:
        links = links.get('second_level_browse_pages') or links.get(
            'top_level_browse_pages') or []
        for link in links:
            body.append(markup.link(link['title'], link['base_path']))

    return body
