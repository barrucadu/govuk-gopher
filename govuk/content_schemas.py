import markup
from collections import namedtuple
from govuk.search_api import fetch_raw_search_results

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
        body = globals()[document_type_parser](details, raw)
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
    """Parse a links hash.  Only some of the links are included.

    One of the included links is the parent.  There are three cases:

    1. There is a 'parent' list, in which case we take the first one.

    2. There is a 'parent_taxons' list, in which case we take the
       first one.

    3. There is no parent.

    We don't treat the 'root_taxon' as a parent for consistency with
    the mainstream browse pages.  The mainstream browse page sections
    don't have a parent-link to the top-level browse page.
    """

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

    raw_parents = links.get('parent') or links.get(
        'parent_taxons') or links.get('root_taxons') or []
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


def parse_details_transaction(details, _content_item):
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


def parse_details_html_publication(details, _content_item):
    """Parse an html_publication content item details hash."""

    return [markup.text(details['body'])]


def parse_details_answer(details, _content_item):
    """Parse an answer content item details hash."""

    return [markup.text(details['body'])]


def parse_details_news_story(details, _content_item):
    """Parse a news_story content item details hash."""

    return [markup.text(details['body'])]


def parse_details_guide(details, _content_item):
    """Parse a guide content item details hash."""

    body = []

    for part in details['parts']:
        body.append(markup.heading(part['title']))
        body.append(markup.text(part['body']))

    return body


def parse_details_organisation(details, _content_item):
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


def parse_details_mainstream_browse_page(details, content_item):
    """Parse a mainstream_browse_page content item details hash.

    There are two types of mainstream browse page: "sections", which
    contain subsections; and "subsections", which contain content.
    There's also the top-level "/browse" page which has a list of
    sections.

    Content can be tagged to a subsection in two ways:

    1. There is a 'details.groups', in which case this is a mainstream
       browse page with curated content, and the page details are in
       the 'links.children' hash.

    2. The search API finds things tagged to it.

    If there is no tagged content, this is a section.  Now there are
    three cases:

    1. There is a 'details.ordered_second_level_browse_pages', in
       which case this is a section with subsections in a given order
       and the subsection details may or may not be in the
       'links.children' hash (if not the search API can be used to get
       the title).

    2. There is a 'links.children', in which case this is a section
       with subsections in an arbitrary order.

    3. There is no 'links.children', in which case this is the
       top-level "/browse" page and has a
       'links.top_level_browse_pages'.

    """

    body = []

    all_links = []
    all_links.extend(content_item['links'].get('children') or [])
    all_links.extend(content_item['links'].get(
        'second_level_browse_pages') or [])

    all_links_by_base_path = {link['base_path']: link for link in all_links}
    all_links_by_content_id = {link['content_id']: link for link in all_links}

    # Check for a curated list of children
    for group in details.get('groups') or []:
        group_links = []
        for base_path in group['contents']:
            link = all_links_by_base_path.get(base_path)
            if link:
                group_links.append(
                    markup.link(
                        link['title'],
                        base_path))
            else:
                search = fetch_raw_search_results(
                    {'link': base_path}).get('results') or []
                if search != []:
                    group_links.append(
                        markup.link(
                            search[0]['title'],
                            base_path
                        )
                    )
        if group_links != []:
            body.append(markup.heading(group['name']))
            body.extend(group_links)
    if body != []:
        return body

    # Check for a tagged list of children
    prefix = '/browse/'
    mbp_path = content_item['base_path'][len(prefix):]
    for result in fetch_raw_search_results(
            {'mainstream_browse_pages': mbp_path}).get('results') or []:
        body.append(markup.link(result['title'], result['link']))
    if body != []:
        return body

    # Check for an ordered list of subsections
    for content_id in details.get('ordered_second_level_browse_pages') or []:
        link = all_links_by_content_id.get(content_id)
        if link:
            body.append(
                markup.link(link['title'], link['base_path']))
    if body != []:
        return body

    # Check for an unordered list of subsections
    for link in content_item['links'].get('second_level_browse_pages') or []:
        body.append(markup.link(link['title'], link['base_path']))
    if body != []:
        return body

    # This is the top-level browse page
    for link in content_item['links'].get('top_level_browse_pages') or []:
        body.append(markup.link(link['title'], link['base_path']))

    return body


def parse_details_taxon(details, content_item):
    """Parse a taxon content item details hash.

    Content is tagged to taxons, and is surfaced through search.  The
    taxon content item doesn't directly refer to its children.  This
    is essentially a simpler version of the mainstream_browse_page
    type.
    """

    body = []

    for result in fetch_raw_search_results(
            {'part_of_taxonomy_tree': content_item['content_id']}).get('results') or []:
        body.append(markup.link(result['title'], result['link']))

    return body
