import logging

import yagmail
import yaml


def send_notification(config, user_config, title, body):
    email_address = user_config['email']
    send_email(email_address, title, body)


def send_email(address, title, body):
    # TODO no hard coded data directories
    with open('data/gmail_app_password.yml', 'r') as f:
        gmail_credentials = yaml.safe_load(f)

    yag = yagmail.SMTP(gmail_credentials['user'], gmail_credentials['password'])
    yag.log.setLevel(logging.DEBUG)
    result = yag.send(to=address, subject=title, contents=body)
    # logging.info(f'Sent an email to {address} titled {title} and body:\n{body}')
    return result
