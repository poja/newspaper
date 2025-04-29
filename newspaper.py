import logging
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

import yaml
import markdown

from llm.topic_queries import build_topic_checker
from news.fetch_news import build_news_source
from notifications.message_content import build_message
from notifications.email import send_notification
from py_tools.file_lock import FileLock, LockUnavailable
from py_tools.stupid_database import StupidDatabase

# Config based on YML
CONFIG_FILE_NAME = 'config.yml'

# Database currently implemented using stupid_database
#  but could be any DB in the future
DATABASE_FILE_NAME = 'database.yml'

LOOP_INTERVAL = 10 * 60  # 10 minutes


def main():
    parser = ArgumentParser()
    parser.add_argument('--base-path', '-p', default='.')
    parser.add_argument('--setup_cron', '-c', action='store_true')
    parser.add_argument('--daemon', '-d', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    base_path = Path(args.base_path)
    try:
        with FileLock(base_path / '.lock'):

            with open(base_path / CONFIG_FILE_NAME, 'r') as f:
                config = yaml.safe_load(f)
                if config is None:
                    config = {}

            assert 'base_path' not in config
            config['base_path'] = base_path

            if args.setup_cron:
                setup_cron(config)
            elif args.daemon:
                start_daemon(config)
            else:
                update_loop(config)

    except LockUnavailable:
        logging.error(f"Couldn't get lock for base directory {base_path}")


def update_loop(config):
    while True:
        check_the_news(config)

        time.sleep(LOOP_INTERVAL)


def check_the_news(config):
    for user in config['users']:
        fetch_hour = int(user.get('news_feed_hour', '2'))
        last_update = last_updated(config, user['name'])
        if not does_require_update(last_update, fetch_hour):
            logging.debug(f'User {user["name"]} does not require update')
            continue
        all_news = []
        for news_source_config in user['sources']:
            news_source = build_news_source(config, news_source_config)
            news_items = news_source.fetch()
            all_news.extend(news_items)
        topic_options = user['topics']
        topic_checker = build_topic_checker(config)
        identified_topics = topic_checker.check(all_news, topic_options)
        message = build_message(config, user['name'], all_news, topic_options, identified_topics)
        html = markdown.markdown(message)
        notification_title = f"Newspaper: Daily news feed ({datetime.now().strftime('%Y-%m-%d')})"
        send_notification(config, user, notification_title, html)
        update_last_updated(config, user['name'])


def setup_cron(config):
    # TODO
    logging.info('Cron job set up.')


def start_daemon(config):
    pass  # TODO


def last_updated(config, username):
    db = StupidDatabase(config['base_path'] / 'database.yml')
    data = db.read()
    user_data = data.get('users', {}).get(username, {})
    last_update = user_data.get('last_updated', '1990-01-01')
    if isinstance(last_update, str):
        last_update = datetime.fromisoformat(last_update)
    return last_update


def update_last_updated(config, username):
    db = StupidDatabase(config['base_path'] / 'database.yml')
    data = db.read()
    if 'users' not in data:
        data['users'] = {}
    if username not in data['users']:
        data['users'][username] = {}
    data['users'][username]['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    db.write(data)


def does_require_update(last_update, news_feed_hour):
    current_time = datetime.now()
    if last_update.date() == current_time.date():
        if current_time.hour < news_feed_hour:
            return False
    elif last_update.date() == (current_time.date() - timedelta(days=1)):
        if last_update.hour >= news_feed_hour and current_time.hour < news_feed_hour:
            return False
    return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s :: %(name)s :: %(message)s")
    main()
