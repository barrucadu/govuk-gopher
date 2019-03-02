#!/usr/bin/env python

from govuk.api import fetch_content_item

content_item = fetch_content_item('vehicle-tax')

for k, v in content_item.items():
    print(f'{k}:')
    if k == 'body':
        for item in v:
            if item['type'] == 'text':
                print(item['text'])
            elif item['type'] == 'heading':
                print(f'----- {item["text"]} -----')
            elif item['type'] == 'web_link':
                print(f'EXTERNAL LINK: {item["text"]} @ {item["target"]}')
            print()
    else:
        print(v)
    print()
