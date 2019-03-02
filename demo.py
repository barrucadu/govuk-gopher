#!/usr/bin/env python

from govuk.api import fetch_content_item
from markup import Elem

content_item = fetch_content_item('vehicle-tax')

print(f'title:\n{content_item.title}\n')

print(f'description:\n{content_item.description}\n')

print(f'updated_at:\n{content_item.updated_at}\n')

print('body:')
for item in content_item.body:
    if item['type'] == Elem.TEXT:
        print(item['text'])
    elif item['type'] == Elem.HEADING:
        print(f'----- {item["text"]} -----')
    elif item['type'] == Elem.WEB_LINK:
        print(f'EXTERNAL LINK: {item["text"]} @ {item["target"]}')
    print()
