#!/usr/bin/env python3

from govuk.api import fetch_content_item
import govuk.content_schemas as schemas
import gopher
import asyncio
import re
import sys
import traceback

BASE_PATH_PATTERN = re.compile('^(/[a-zA-Z0-9\-]+)+/?$')


async def handler(reader, writer):
    raw = await reader.read(4096)
    request = raw.decode().strip()
    ip, port = writer.get_extra_info('sockname')
    addr = writer.get_extra_info('peername')
    print(f'{addr}: "{request}"')

    if request in ['', '/']:
        response = gopher.usage_message(ip, port)
    elif BASE_PATH_PATTERN.match(request):
        try:
            content_item = fetch_content_item(request)
            response = gopher.render(content_item)
        except schemas.UnknownDocumentType as e:
            response = gopher.bad_content_message(
                request, f'This page is of type "{e.args[0]}", which is not supported.')
        except Exception as e:
            print(f'Exception: {str(e)}')
            traceback.print_exc(file=sys.stdout)
            response = gopher.bad_content_message(
                request, 'Something went wrong parsing the response from GOV.UK.')
    else:
        response = gopher.bad_request_message(request)

    writer.write(response.encode())
    await writer.drain()

    writer.close()


def run(ip='127.0.0.1', port=70):
    """Serves gopher requests until C-c is hit.
    """

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handler, ip, port, loop=loop)
    server = loop.run_until_complete(coro)

    print('Gopher server running')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    run(port=7070)
