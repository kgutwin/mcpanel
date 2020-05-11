import json
import base64
import traceback
import urllib.parse

from lambdas import admin, user, templates


def route(method, path, data):
    if path == '/admin':
        if method == 'GET':
            return admin.render()
        elif method == 'POST':
            return admin.update(data)

    return user.render()


def http(body, status_code=200):
    return {
        'statusCode': status_code,
        'statusDescription': 'OK',
        'body': body,
        'headers': {
            'Content-Type': 'text/html'
        },
        'isBase64Encoded': False
    }


def handler(event, context):
    print(json.dumps(event))
    if 'body' in event:
        if event['isBase64Encoded']:
            data = base64.b64decode(event['body'])
        else:
            data = event['body']
        if event['headers'].get('content-type', '').lower() == 'application/x-www-form-urlencoded':
            data = urllib.parse.parse_qs(data.decode('utf-8'))
            data = {
                k: v[0] if len(v) == 1 else v
                for k, v in data.items()
            }
    else:
        data = None

    try:
        result = route(
            event['requestContext']['http']['method'],
            event['requestContext']['http']['path'],
            data
        )
        if result:
            return http(result)
        else:
            return http(templates.error(str(result)), 400)
    except Exception as ex:
        traceback.print_exc()
        return http(templates.error(str(ex)), 500)
