import json

from aiohttp import web

from serializers import serialize_body

routes = web.RouteTableDef()

import smtplib
import email


@routes.post('/api/v1/emails')
@serialize_body('post_email')
async def send_email(request: web.Request, body):
    print(body)
    subject = None

    if 'subject' in body:
        subject = body['subject']

    await email_sender(body['to_addr'], body['msg'], request.app['config'], subject)
    return web.Response(status=200, content_type='application/json', body=json.dumps({'status': 'Ok'}))


async def email_sender(toaddr: str, body: str, config: dict, subject=None):
    fromaddr = config['EMAIL_ADDRESS']
    msg = email.message.EmailMessage()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject if subject else 'None'

    msg.set_content(body)

    with smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT']) as server:
        server.starttls()
        server.login(fromaddr, config['EMAIL_PASSWORD'])
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
