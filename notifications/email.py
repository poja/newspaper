import logging


def send_notification(config, user_config, title, body):
    email_address = user_config['email']
    send_email(email_address, title, body)


def send_email(address, title, body):
    pass  # TODO
    logging.info(f'Sent an email to {address} titled {title} and body:\n{body}')
