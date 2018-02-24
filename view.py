import json
import os

from aiohttp import web, ClientSession
import emails
from emails.template import JinjaTemplate as T
from serializers import serialize_body

routes = web.RouteTableDef()
base_dir = os.path.abspath(os.path.curdir)


@routes.post('/api/v1/emails')
@serialize_body('post_email')
async def send_email(request: web.Request, body):
    subject = None

    if 'subject' in body:
        subject = body['subject']

    template = await read_template(os.path.join(base_dir, 'email_template.html'))

    response = await email_sender(body, template, request.app['config'], subject)
    return web.Response(status=200, content_type='application/json', body=json.dumps(response))


@routes.get('/api/v1/emails/transactions/{transaction_id}')
async def check_email(request: web.Request):
    transaction_id = request.match_info['transaction_id']

    transaction_data = await check_transaction_status(transaction_id, request.app['config']['API_KEY'])

    if not transaction_data['success']:
        raise web.HTTPNotFound(content_type='application/json',
                               body=json.dumps({'error': transaction_data['error']}))

    return web.Response(status=200, content_type='application/json', body=json.dumps(transaction_data))


@routes.get('/api/v1/emails/messages/{message_id}')
async def get_message_data(request: web.Request):
    message_id = request.match_info['message_id']
    message_data = await check_message_status(message_id, request.app['config']['API_KEY'])

    if not message_data['success']:
        raise web.HTTPNotFound(content_type='application/json',
                               body=json.dumps({'error': message_data['error']}))

    return web.Response(status=200, content_type='application/json', body=json.dumps(message_data))


async def email_sender(body: dict, template: str, config: dict, subject='None'):

    message = emails.html(
        subject=subject,
        html=T(template),
        mail_from=('My StartUP', config['EMAIL_ADDRESS'])
    )
    response = message.send(
        to=body['to_addr'],
        render={'name': 'Djohn Black', 'verify_linc': 'www.fake.linc'},
        smtp={'host': config['SMTP_SERVER'], 'port': config['SMTP_PORT'],
              'tls': True, 'user': config['LOGIN'], 'password': config['PASSWORD']},
    )
    # import ipdb; ipdb.set_trace()
    print(response)
    status = response.status_code
    text = response.status_text.decode('utf-8').split()[1]

    return {'status': status, 'transaction_id': text}


async def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template = template_file.read()
    return template


async def check_transaction_status(transaction_id: str, api_key: str):
    params = {
        'transactionID': transaction_id,
        'apikey': api_key,
        'showFailed': 'true',
        'showErrors': 'true',
        'showMessageIDs': 'true',
        'showAbuse': 'true',
        'showClicked': 'true',
        'showDelivered': 'true',
        'showOpened': 'true',
        'showPending': 'true',
        'showSent': 'true',
        'showUnsubscribed': 'true',
    }
    async with ClientSession() as session:
        async with session.get('https://api.elasticemail.com/v2/email/getstatus', params=params) as response:
            return await response.json()


async def check_message_status(message_id: str, api_key: str):
    params = {
        'apikey': api_key,
        'messageID': message_id,
    }
    async with ClientSession() as session:
        async with session.get('https://api.elasticemail.com/v2/email/status', params=params) as response:
            return await response.json()
