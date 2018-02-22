import json
from jinja2 import Template
import os

from aiohttp import web
import emails
from emails.template import JinjaTemplate as T
from serializers import serialize_body

routes = web.RouteTableDef()

import smtplib
import email
from email6.mime.multipart import MIMEMultipart
from email6.mime.text import MIMEText


base_dir = os.path.abspath(os.path.curdir)

@routes.post('/api/v1/emails')
@serialize_body('post_email')
async def send_email(request: web.Request, body):
    subject = None

    if 'subject' in body:
        subject = body['subject']

    message_template = await read_template(os.path.join(base_dir, 'email_template.html'))
    # import ipdb; ipdb.set_trace()
    # print(message_template.render())
    # await email_sender(body['to_addr'], body['msg'], request.app['config'], subject)
    # await email_sender(body['to_addr'], message_template, request.app['config'], subject)
    response = await new_email_sender(body['to_addr'], body, request.app['config'], subject)
    return web.Response(status=200, content_type='application/json', body=json.dumps(response))


async def email_sender(toaddr: str, body: str, config: dict, subject=None):
    fromaddr = config['EMAIL_ADDRESS']


    # msg = email.message.EmailMessage()
    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject if subject else 'None'

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT']) as server:
        server.starttls()
        server.login(fromaddr, config['EMAIL_PASSWORD'])
        text = msg.as_string()
        r = server.sendmail(fromaddr, toaddr, text)
    

async def new_email_sender(toaddr: str, body: str, config: dict, subject='None'):

    with open(os.path.join(base_dir, 'email_template.html'), 'r', encoding='utf-8') as template_file:
        template = template_file.read()

    message = emails.html(
        subject=subject,
        html=T(template),
        mail_from=('My StartUP', config['EMAIL_ADDRESS'])
    )
    response = message.send(
        to=toaddr,
        render={'massage': 'Congratulate', 'name': 'Djohn Black'},
        smtp={'host': config['SMTP_SERVER'], 'port': config['SMTP_PORT'], 'tls': True, 'user': config['LOGIN'], 'password': config['PASSWORD']},
    )
    # import ipdb; ipdb.set_trace()

    status = response.status_code
    text = response.status_text.decode('utf-8').split()[1]

    return {'status': status, 'message': text}


async def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template = template_file.read()
    return template
