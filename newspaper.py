import logging
import time
from argparse import ArgumentParser
from pathlib import Path

import yaml

from llm.topic_queries import build_topic_checker
from news.fetch_news import build_news_source
from notifications.message_content import build_message
from notifications.email import send_notification
from py_tools.file_lock import FileLock, LockUnavailable

# Config based on YML
CONFIG_FILE_NAME = 'config.yml'

# Database currently implemented using stupid_database
#  but could be any DB in the future
DATABASE_FILE_NAME = 'database.yml'

FETCH_INTERVAL = 24 * 60 * 60  # 24h


def main():
    parser = ArgumentParser()
    parser.add_argument('--base-path', '-p', default='.')
    parser.add_argument('--setup_cron', '-c', default=False)
    parser.add_argument('--daemon', '-d', default=False)

    args = parser.parse_args()

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

        # TODO change to a fixed fetch time
        time.sleep(FETCH_INTERVAL)


def check_the_news(config):
    for user in config['users']:
        all_news = []
        for news_source_config in user['sources']:
            news_source = build_news_source(config, news_source_config)
            news_items = news_source.fetch()
            all_news.extend(news_items)
        topic_options = user['topics']
        topic_checker = build_topic_checker(config)
        identified_topics = topic_checker.check(all_news, topic_options)
        message = build_message(config, all_news, topic_options, identified_topics)
        send_notification(config, user, 'Newspaper: Daily news feed', message)


def setup_cron(config):
    # TODO
    logging.info('Cron job set up.')


def start_daemon(config):
    pass  # TODO


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s :: %(name)s :: %(message)s")
    main()
